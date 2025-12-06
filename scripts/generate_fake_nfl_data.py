#!/usr/bin/env python3
"""
Generate a large synthetic-but-plausible NFL dataset seeded with real player names.

This script is intentionally verbose and heavily commented because it doubles as a living
design note for the eventual real data pipeline. It follows the repository's data layout
(`data/raw`, `data/interim`, `data/processed`, `data/external`) and produces Parquet
artifacts that the UI and services can consume while the real ingestion work is underway.

Key behaviors:
 - Pull real player names from the NFLverse master registry (1999-2025 seasons).
 - Inflate the registry with rich fake attributes (ratings, vitals, per-season stats).
 - Generate companion team and coach datasets so search/navigation feel populated.
 - Emit Rich-powered progress output with timing and file size summaries.

Usage:
    python scripts/generate_fake_nfl_data.py \
        --start-season 1999 --end-season 2025 --min-players 21000 --max-players 25000
"""

from __future__ import annotations

import argparse
import hashlib
import math
import random
import sys
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Sequence

import pandas as pd

try:
    import nflreadpy as nfl
    _NFL_IMPORT_ERROR: Exception | None = None
except Exception as exc:  # pragma: no cover - optional dependency handling
    nfl = None  # type: ignore
    _NFL_IMPORT_ERROR = exc
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text

from gridironlabs.core.config import AppConfig, load_config
from gridironlabs.data.loaders.parquet_loader import ensure_directory, save_parquet_table

# ---------------------------------------------------------------------------
# Constants and lightweight reference data.
# ---------------------------------------------------------------------------

# A tiny, hand-maintained map of active team metadata for quick lookups.
TEAM_METADATA: Sequence[tuple[str, str, str, str]] = (
    ("ARI", "Arizona Cardinals", "NFC", "West"),
    ("ATL", "Atlanta Falcons", "NFC", "South"),
    ("BAL", "Baltimore Ravens", "AFC", "North"),
    ("BUF", "Buffalo Bills", "AFC", "East"),
    ("CAR", "Carolina Panthers", "NFC", "South"),
    ("CHI", "Chicago Bears", "NFC", "North"),
    ("CIN", "Cincinnati Bengals", "AFC", "North"),
    ("CLE", "Cleveland Browns", "AFC", "North"),
    ("DAL", "Dallas Cowboys", "NFC", "East"),
    ("DEN", "Denver Broncos", "AFC", "West"),
    ("DET", "Detroit Lions", "NFC", "North"),
    ("GB", "Green Bay Packers", "NFC", "North"),
    ("HOU", "Houston Texans", "AFC", "South"),
    ("IND", "Indianapolis Colts", "AFC", "South"),
    ("JAX", "Jacksonville Jaguars", "AFC", "South"),
    ("KC", "Kansas City Chiefs", "AFC", "West"),
    ("LV", "Las Vegas Raiders", "AFC", "West"),
    ("LAC", "Los Angeles Chargers", "AFC", "West"),
    ("LAR", "Los Angeles Rams", "NFC", "West"),
    ("MIA", "Miami Dolphins", "AFC", "East"),
    ("MIN", "Minnesota Vikings", "NFC", "North"),
    ("NE", "New England Patriots", "AFC", "East"),
    ("NO", "New Orleans Saints", "NFC", "South"),
    ("NYG", "New York Giants", "NFC", "East"),
    ("NYJ", "New York Jets", "AFC", "East"),
    ("PHI", "Philadelphia Eagles", "NFC", "East"),
    ("PIT", "Pittsburgh Steelers", "AFC", "North"),
    ("SF", "San Francisco 49ers", "NFC", "West"),
    ("SEA", "Seattle Seahawks", "NFC", "West"),
    ("TB", "Tampa Bay Buccaneers", "NFC", "South"),
    ("TEN", "Tennessee Titans", "AFC", "South"),
    ("WAS", "Washington Commanders", "NFC", "East"),
)

# Positions kept compact on purpose; rare special-teams roles are handled via random choice.
POSITIONS: Sequence[str] = (
    "QB",
    "RB",
    "WR",
    "TE",
    "FB",
    "OT",
    "G",
    "C",
    "DT",
    "DE",
    "LB",
    "CB",
    "S",
    "K",
    "P",
    "LS",
)

# Coach name fragments to seed believable-but-fake staff rosters.
COACH_FIRST_NAMES: Sequence[str] = (
    "Alex",
    "Taylor",
    "Jordan",
    "Casey",
    "Riley",
    "Morgan",
    "Avery",
    "Devin",
    "Reese",
    "Parker",
    "Hayden",
    "Jamie",
)
COACH_LAST_NAMES: Sequence[str] = (
    "Smith",
    "Johnson",
    "Williams",
    "Brown",
    "Jones",
    "Miller",
    "Davis",
    "Rodriguez",
    "Martinez",
    "Lee",
    "Walker",
    "White",
    "Thompson",
    "Harris",
    "Clark",
)
COACH_ROLES: Sequence[str] = (
    "HC",
    "OC",
    "DC",
    "STC",
    "QB Coach",
    "DL Coach",
    "DB Coach",
)


def _stable_id(seed: str) -> str:
    """
    Derive a short, deterministic identifier from a string seed.
    """

    return hashlib.sha1(seed.encode("utf-8")).hexdigest()[:12]


@dataclass(frozen=True)
class GeneratedPaths:
    """
    Convenience bundle so downstream code is explicit about where artifacts land.
    """

    player_summaries: Path
    player_seasons: Path
    team_summaries: Path
    team_seasons: Path
    coaches: Path
    external_registry: Path


@dataclass(frozen=True)
class GenerationConfig:
    """
    User-tunable knobs for shaping the fake dataset.
    """

    start_season: int
    end_season: int
    min_players: int
    max_players: int
    seed: int
    force_registry_refresh: bool


def parse_args(argv: Sequence[str] | None = None) -> GenerationConfig:
    """
    Parse CLI flags so the script can be nudged without editing code.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-season", type=int, default=1999, help="first season to include")
    parser.add_argument("--end-season", type=int, default=2025, help="last season to include")
    parser.add_argument(
        "--min-players",
        type=int,
        default=21_000,
        help="minimum unique players to keep after filtering",
    )
    parser.add_argument(
        "--max-players",
        type=int,
        default=25_000,
        help="maximum unique players to retain (sampled down if exceeded)",
    )
    parser.add_argument("--seed", type=int, default=42, help="seed for deterministic runs")
    parser.add_argument(
        "--force-registry-refresh",
        action="store_true",
        help="always re-download the NFLverse registry even if cached",
    )
    args = parser.parse_args(argv)
    return GenerationConfig(
        start_season=args.start_season,
        end_season=args.end_season,
        min_players=args.min_players,
        max_players=args.max_players,
        seed=args.seed,
        force_registry_refresh=args.force_registry_refresh,
    )


# ---------------------------------------------------------------------------
# NFLverse registry handling.
# ---------------------------------------------------------------------------

def _registry_cache_path(config: AppConfig) -> Path:
    """
    Route external downloads to the documented `data/external` folder.
    """

    return config.paths.external_data / "nflverse_players.csv"


def download_registry(config: AppConfig, console: Console, force: bool = False) -> Path:
    """
    Download the NFLverse player registry with a progress-friendly UI and cache it locally.

    Primary path uses `nflreadpy` for resilience and schema parity.
    """

    cache_path = _registry_cache_path(config)
    ensure_directory(cache_path.parent)
    if cache_path.exists() and not force:
        console.log(f"[bold green]Reusing cached registry:[/] {cache_path}")
        return cache_path

    if nfl is None:
        raise RuntimeError(
            "nflreadpy is required for real data extraction. "
            "Install with `pip install nflreadpy` or `pip install -e .` in this repo. "
            f"(import error: {_NFL_IMPORT_ERROR})"
        ) from _NFL_IMPORT_ERROR

    console.log(f"[bold yellow]Fetching NFLverse registry via nflreadpy ->[/] {cache_path}")
    df = nfl.load_players()

    # nflreadpy returns a Polars DataFrame; convert to pandas for downstream code.
    if hasattr(df, "to_pandas"):
        df_pd = df.to_pandas()
    else:  # pragma: no cover - defensive branch
        df_pd = pd.DataFrame(df)

    df_pd.to_csv(cache_path, index=False)
    console.log("[bold green]Download complete (nflreadpy)[/]")
    return cache_path


def _pick_column(df: pd.DataFrame, candidates: Sequence[str], fallback: str) -> pd.Series:
    """
    Choose the first matching column, otherwise return a Series filled with a fallback value.
    """

    for col in candidates:
        if col in df.columns:
            return df[col]
    return pd.Series([fallback] * len(df))


def load_player_registry(
    csv_path: Path,
    rng: random.Random,
    config: GenerationConfig,
) -> pd.DataFrame:
    """
    Load and filter the player registry, enforcing season bounds and headcount targets.

    The registry schema can drift, so this function defends against missing columns by
    picking from several likely options and filling sensible defaults when absent.
    """

    df = pd.read_csv(csv_path, low_memory=False)
    name_series = _pick_column(
        df,
        candidates=("full_name", "display_name", "player_display_name", "player_name", "name"),
        fallback="Unknown Player",
    )
    position_series = _pick_column(df, candidates=("position", "pos"), fallback=None)
    team_series = _pick_column(df, candidates=("team", "team_abbr", "recent_team"), fallback=None)
    first_season = _pick_column(
        df,
        candidates=("first_year", "first_season", "rookie_year", "season", "season_start"),
        fallback=config.start_season,
    )
    last_season = _pick_column(
        df,
        candidates=("last_year", "last_season", "season_end"),
        fallback=config.end_season,
    )

    registry = pd.DataFrame(
        {
            "name": name_series,
            "position": position_series,
            "team": team_series,
            "first_season": first_season.fillna(config.start_season).astype(int),
            "last_season": last_season.fillna(config.end_season).astype(int),
        }
    )
    registry = registry[registry["name"].notna()]

    # Guard against truncated names and make sure we only keep the target season window.
    registry["name"] = registry["name"].astype(str).str.strip()
    registry = registry[
        (registry["last_season"] >= config.start_season)
        & (registry["first_season"] <= config.end_season)
    ]

    # Build a stable id: prefer nflverse ids if present, otherwise hash the name+first season.
    if "gsis_id" in df.columns:
        registry["player_id"] = df["gsis_id"].fillna("").astype(str)
    elif "pfr_id" in df.columns:
        registry["player_id"] = df["pfr_id"].fillna("").astype(str)
    else:
        registry["player_id"] = [
            _stable_id(f"{row.name}-{row.first_season}") for row in registry.itertuples(index=False)
        ]
    registry.loc[registry["player_id"] == "", "player_id"] = [
        _stable_id(f"{row.name}-{row.first_season}") for row in registry.itertuples(index=False)
    ]

    registry["position"] = registry["position"].fillna("").replace({"nan": ""})
    registry["team"] = registry["team"].fillna("").replace({"nan": ""})
    registry = registry.drop_duplicates(subset=["player_id"])

    if len(registry) < config.min_players:
        deficit = config.min_players - len(registry)
        registry = pd.concat(
            [registry, _synthesize_extra_players(deficit, rng, config)],
            ignore_index=True,
        )

    if len(registry) > config.max_players:
        registry = registry.sample(
            n=config.max_players, random_state=config.seed
        ).reset_index(drop=True)

    return registry.reset_index(drop=True)


def _synthesize_extra_players(count: int, rng: random.Random, config: GenerationConfig) -> pd.DataFrame:
    """
    Pad the registry with obviously fake players when the real data source is thin.
    """

    console = Console()
    console.log(
        f"[bold yellow]Registry short by {count} players; padding with generated names.[/]"
    )
    fake_rows = []
    for idx in range(count):
        name = f"Gridiron Placeholder {idx:05d}"
        player_id = _stable_id(f"placeholder-{idx}")
        position = rng.choice(POSITIONS)
        team = rng.choice(TEAM_METADATA)[0]
        first = rng.randint(config.start_season, config.end_season - 1)
        last = rng.randint(first, config.end_season)
        fake_rows.append(
            {
                "player_id": player_id,
                "name": name,
                "position": position,
                "team": team,
                "first_season": first,
                "last_season": last,
            }
        )
    return pd.DataFrame(fake_rows)


# ---------------------------------------------------------------------------
# Synthetic data generation helpers.
# ---------------------------------------------------------------------------

def _random_birth_year(seasons: tuple[int, int], rng: random.Random) -> int:
    """
    Estimate a plausible birth year from the start/end season window.
    """

    start, end = seasons
    career_start_age = rng.randint(21, 25)
    return start - career_start_age


def _height_weight_for_position(position: str, rng: random.Random) -> tuple[int, int]:
    """
    Use loose positional averages so vitals look believable at a glance.
    """

    position = position.upper()
    if position in {"QB", "WR", "CB", "S"}:
        height = rng.randint(70, 76)
        weight = rng.randint(185, 225)
    elif position in {"RB", "FB"}:
        height = rng.randint(68, 73)
        weight = rng.randint(200, 240)
    elif position in {"TE", "LB"}:
        height = rng.randint(75, 79)
        weight = rng.randint(235, 265)
    elif position in {"OT", "G", "C", "DT", "DE"}:
        height = rng.randint(75, 80)
        weight = rng.randint(285, 335)
    elif position in {"K", "P", "LS"}:
        height = rng.randint(70, 75)
        weight = rng.randint(175, 215)
    else:
        height = rng.randint(70, 77)
        weight = rng.randint(190, 260)
    return height, weight


def _ratings_for_position(position: str, rng: random.Random) -> dict[str, int]:
    """
    Create a compact rating profile; values sit between 20-99.
    """

    base = rng.randint(55, 90)
    spread = rng.randint(5, 15)
    return {
        "overall": min(99, max(20, base)),
        "potential": min(99, max(20, base + spread)),
        "durability": rng.randint(50, 95),
        "football_iq": rng.randint(45, 95),
        "athleticism": rng.randint(40, 98),
        "motor": rng.randint(40, 98),
        "discipline": rng.randint(40, 98),
        "positional_rank": rng.randint(1, 150),
    }


def _per_season_stats(
    position: str,
    rng: random.Random,
    season_count: int,
    team_code: str,
) -> list[dict[str, object]]:
    """
    Generate per-season stat lines tuned loosely by position group.
    """

    stats: list[dict[str, object]] = []
    base_games = rng.randint(8, 17)
    for _ in range(season_count):
        if position == "QB":
            passing_yards = abs(int(rng.normalvariate(3200, 900)))
            stats.append(
                {
                    "games_played": base_games,
                    "passing_yards": passing_yards,
                    "passing_tds": rng.randint(10, max(12, passing_yards // 250)),
                    "interceptions": rng.randint(3, 20),
                    "rushing_yards": abs(int(rng.normalvariate(250, 180))),
                    "team": team_code,
                }
            )
        elif position in {"RB", "FB"}:
            rush = abs(int(rng.normalvariate(850, 400)))
            stats.append(
                {
                    "games_played": base_games,
                    "rushing_yards": rush,
                    "rushing_tds": rng.randint(3, max(4, rush // 250)),
                    "receptions": rng.randint(10, 70),
                    "receiving_yards": abs(int(rng.normalvariate(250, 200))),
                    "team": team_code,
                }
            )
        elif position in {"WR", "TE"}:
            rec = rng.randint(25, 120)
            yards = abs(int(rng.normalvariate(rec * 13, rec * 3)))
            stats.append(
                {
                    "games_played": base_games,
                    "receptions": rec,
                    "receiving_yards": yards,
                    "receiving_tds": rng.randint(2, max(3, yards // 300)),
                    "team": team_code,
                }
            )
        elif position in {"OT", "G", "C"}:
            stats.append(
                {
                    "games_played": base_games,
                    "pressures_allowed": rng.randint(0, 45),
                    "penalties": rng.randint(0, 12),
                    "team": team_code,
                }
            )
        elif position in {"DT", "DE", "LB"}:
            tackles = rng.randint(25, 120)
            stats.append(
                {
                    "games_played": base_games,
                    "tackles": tackles,
                    "sacks": rng.randint(0, max(1, tackles // 15)),
                    "tfl": rng.randint(0, max(1, tackles // 10)),
                    "forced_fumbles": rng.randint(0, 5),
                    "team": team_code,
                }
            )
        elif position in {"CB", "S"}:
            tackles = rng.randint(35, 95)
            stats.append(
                {
                    "games_played": base_games,
                    "tackles": tackles,
                    "interceptions": rng.randint(0, 8),
                    "passes_defended": rng.randint(2, 25),
                    "team": team_code,
                }
            )
        elif position in {"K", "P"}:
            stats.append(
                {
                    "games_played": base_games,
                    "fg_made": rng.randint(12, 40),
                    "fg_attempts": rng.randint(15, 45),
                    "xp_made": rng.randint(15, 60),
                    "avg_punt": abs(rng.normalvariate(45, 3)),
                    "team": team_code,
                }
            )
        else:
            stats.append({"games_played": base_games, "team": team_code})
    return stats


def build_player_tables(
    registry: pd.DataFrame,
    rng: random.Random,
    config: GenerationConfig,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Inflate the lean registry into detailed player summaries and player-season rows.
    """

    summaries: list[dict[str, object]] = []
    seasons: list[dict[str, object]] = []

    for row in registry.itertuples(index=False):
        # Anchor each player to a plausible position and team.
        position = row.position if isinstance(row.position, str) and row.position else rng.choice(POSITIONS)
        team_code = row.team if isinstance(row.team, str) and row.team else rng.choice(TEAM_METADATA)[0]

        career_length = rng.randint(1, min(15, config.end_season - config.start_season + 1))
        first_season = max(config.start_season, int(row.first_season))
        last_season = min(config.end_season, int(row.last_season))
        if last_season - first_season + 1 < career_length:
            career_length = last_season - first_season + 1

        # Choose a season window anchored inside the requested bounds.
        season_start_cap = max(first_season, last_season - career_length + 1)
        start_season = rng.randint(first_season, season_start_cap)
        end_season = min(last_season, start_season + career_length - 1)
        season_range = list(range(start_season, end_season + 1))

        ratings = _ratings_for_position(position, rng)
        height_in, weight_lbs = _height_weight_for_position(position, rng)
        birth_year = _random_birth_year((start_season, end_season), rng)
        birth_dt = date(birth_year, rng.randint(1, 12), rng.randint(1, 28))

        # Aggregate simple career-level stats by summing per-season lines.
        season_stats = _per_season_stats(position, rng, len(season_range), team_code)
        for season, stat_line in zip(season_range, season_stats, strict=True):
            seasons.append(
                {
                    "player_id": row.player_id,
                    "name": row.name,
                    "season": season,
                    "position": position,
                    "team": team_code,
                    **stat_line,
                }
            )

        career_games = sum(s.get("games_played", 0) for s in season_stats)
        scrimmage_yards = sum(
            s.get("rushing_yards", 0)
            + s.get("receiving_yards", 0)
            + s.get("passing_yards", 0)
            for s in season_stats
        )
        touchdowns = sum(
            s.get("receiving_tds", 0)
            + s.get("rushing_tds", 0)
            + s.get("passing_tds", 0)
            for s in season_stats
        )

        summaries.append(
            {
                "player_id": row.player_id,
                "name": row.name,
                "position": position,
                "team": team_code,
                "first_season": start_season,
                "last_season": end_season,
                "seasons_played": len(season_range),
                "birth_date": birth_dt,
                "height_in": height_in,
                "weight_lbs": weight_lbs,
                "ratings": ratings,
                "career_stats": {
                    "games_played": int(career_games),
                    "scrimmage_yards": int(scrimmage_yards),
                    "touchdowns": int(touchdowns),
                },
            }
        )

    summaries_df = pd.DataFrame(summaries)
    seasons_df = pd.DataFrame(seasons)
    return summaries_df, seasons_df


def build_team_tables(
    player_seasons: pd.DataFrame,
    rng: random.Random,
    config: GenerationConfig,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Aggregate team-level summaries from the player-season table.
    """

    season_rows: list[dict[str, object]] = []
    for season in range(config.start_season, config.end_season + 1):
        season_slice = player_seasons[player_seasons["season"] == season]
        for code, name, conf, div in TEAM_METADATA:
            slice_team = season_slice[season_slice["team"] == code]
            total_points = rng.randint(220, 520)
            season_rows.append(
                {
                    "team_id": code,
                    "name": name,
                    "conference": conf,
                    "division": div,
                    "season": season,
                    "wins": rng.randint(2, 15),
                    "losses": rng.randint(0, 15),
                    "points_for": total_points,
                    "points_allowed": rng.randint(180, 520),
                    "yards_from_scrimmage": int(
                        slice_team.get("rushing_yards", 0).sum()
                        + slice_team.get("receiving_yards", 0).sum()
                        + slice_team.get("passing_yards", 0).sum()
                    ),
                    "turnovers": rng.randint(10, 40),
                    "takeaways": rng.randint(10, 40),
                }
            )

    season_df = pd.DataFrame(season_rows)
    summary_df = (
        season_df.groupby(["team_id", "name", "conference", "division"], as_index=False)
        .agg(
            seasons_played=("season", "count"),
            avg_wins=("wins", "mean"),
            avg_points_for=("points_for", "mean"),
            avg_points_allowed=("points_allowed", "mean"),
        )
        .assign(
            ratings=lambda df: df.apply(
                lambda row: {
                    "overall": rng.randint(60, 95),
                    "offense": rng.randint(60, 95),
                    "defense": rng.randint(60, 95),
                    "special_teams": rng.randint(55, 90),
                },
                axis=1,
            )
        )
    )
    return summary_df, season_df


def build_coach_table(
    rng: random.Random,
    config: GenerationConfig,
) -> pd.DataFrame:
    """
    Generate a deep bench of fake coaches with varied roles and tenure.
    """

    rows: list[dict[str, object]] = []
    for season in range(config.start_season, config.end_season + 1):
        for team_code, team_name, _, _ in TEAM_METADATA:
            staff_size = rng.randint(3, 6)
            for _ in range(staff_size):
                first = rng.choice(COACH_FIRST_NAMES)
                last = rng.choice(COACH_LAST_NAMES)
                role = rng.choice(COACH_ROLES)
                coach_id = _stable_id(f"{first}-{last}-{team_code}-{season}")
                rows.append(
                    {
                        "coach_id": coach_id,
                        "name": f"{first} {last}",
                        "role": role,
                        "team": team_code,
                        "season": season,
                        "history": [
                            f"{team_code} {season} ({role})",
                            f"{team_name} development coach",
                        ],
                        "ratings": {
                            "leadership": rng.randint(50, 98),
                            "scheme": rng.randint(45, 98),
                            "development": rng.randint(45, 98),
                        },
                    }
                )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Presentation helpers.
# ---------------------------------------------------------------------------

def _format_size(num_bytes: int) -> str:
    """
    Convert raw byte counts into human-friendly strings.
    """

    if num_bytes <= 0:
        return "0 B"
    units = ("B", "KB", "MB", "GB")
    power = int(math.log(num_bytes, 1024))
    power = min(power, len(units) - 1)
    size = num_bytes / (1024**power)
    return f"{size:,.2f} {units[power]}"


def render_summary(console: Console, paths: GeneratedPaths, started_at: float) -> None:
    """
    Print a Rich table showing where data landed and how large it is.
    """

    table = Table(
        title="Generated Artifacts",
        box=box.MINIMAL_DOUBLE_HEAD,
        header_style="bold magenta",
        show_lines=False,
    )
    table.add_column("Dataset")
    table.add_column("Path")
    table.add_column("Size")

    for label, path in (
        ("Player summaries", paths.player_summaries),
        ("Player seasons", paths.player_seasons),
        ("Team summaries", paths.team_summaries),
        ("Team seasons", paths.team_seasons),
        ("Coaches", paths.coaches),
        ("NFLverse registry cache", paths.external_registry),
    ):
        size = _format_size(path.stat().st_size if path.exists() else 0)
        table.add_row(label, str(path), size)

    runtime = time.perf_counter() - started_at
    console.print(table)
    console.print(
        Panel.fit(
            Text(f"Completed in {runtime:0.2f} seconds", style="bold green"),
            border_style="green",
        )
    )


# ---------------------------------------------------------------------------
# Main orchestration.
# ---------------------------------------------------------------------------

def generate_fake_data(config: GenerationConfig) -> None:
    """
    Tie everything together with Rich progress reporting.
    """

    console = Console()
    rng = random.Random(config.seed)
    started_at = time.perf_counter()

    app_config = load_config()
    ensure_directory(app_config.paths.processed_data)
    ensure_directory(app_config.paths.external_data)

    paths = GeneratedPaths(
        player_summaries=app_config.paths.processed_data / "players.parquet",
        player_seasons=app_config.paths.processed_data / "player_seasons.parquet",
        team_summaries=app_config.paths.processed_data / "teams.parquet",
        team_seasons=app_config.paths.processed_data / "team_seasons.parquet",
        coaches=app_config.paths.processed_data / "coaches.parquet",
        external_registry=_registry_cache_path(app_config),
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task_download = progress.add_task("Download NFLverse registry", start=False, total=None)
        task_players = progress.add_task("Build player tables", start=False, total=None)
        task_teams = progress.add_task("Build team tables", start=False, total=None)
        task_coaches = progress.add_task("Build coach table", start=False, total=None)
        task_write = progress.add_task("Persist Parquet datasets", start=False, total=None)

        progress.start_task(task_download)
        registry_path = download_registry(app_config, console, force=config.force_registry_refresh)
        progress.update(task_download, completed=1)

        progress.start_task(task_players)
        registry = load_player_registry(registry_path, rng, config)
        player_summaries, player_seasons = build_player_tables(registry, rng, config)
        progress.update(task_players, completed=1)

        progress.start_task(task_teams)
        team_summaries, team_seasons = build_team_tables(player_seasons, rng, config)
        progress.update(task_teams, completed=1)

        progress.start_task(task_coaches)
        coaches = build_coach_table(rng, config)
        progress.update(task_coaches, completed=1)

        progress.start_task(task_write)
        save_parquet_table(player_summaries, paths.player_summaries)
        save_parquet_table(player_seasons, paths.player_seasons)
        save_parquet_table(team_summaries, paths.team_summaries)
        save_parquet_table(team_seasons, paths.team_seasons)
        save_parquet_table(coaches, paths.coaches)
        progress.update(task_write, completed=1)

    render_summary(console, paths, started_at)
    console.print(
        Panel.fit(
            "[bold cyan]Next steps:[/]\n"
            "- Point repositories at `data/processed/*.parquet` to drive the UI.\n"
            "- Re-run with `--force-registry-refresh` to pull new NFLverse drops.\n"
            "- Adjust `--min-players/--max-players` to scale volume for load testing.",
            border_style="cyan",
        )
    )


def main(argv: Sequence[str] | None = None) -> None:
    """
    Entrypoint wrapper that keeps sys.exit handling contained.
    """

    config = parse_args(argv)
    try:
        generate_fake_data(config)
    except Exception as exc:  # pragma: no cover - best-effort UX for interactive runs.
        Console().print(f"[bold red]Generation failed:[/] {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()


"""Generate synthetic NFL-style datasets using real player names from nflreadpy.

This script populates the Gridiron Labs data layout with believable fake data so
you can prototype the UI without waiting on the full ingestion pipeline. Player
names are pulled from nflreadpy; ratings and stats are generated locally.
"""

from __future__ import annotations

import argparse
import random
import sys
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Iterable, Sequence
from uuid import NAMESPACE_DNS, uuid5

import polars as pl
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich.theme import Theme

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from gridironlabs.core.config import AppPaths, load_config


TEAM_CATALOG: list[tuple[str, str]] = [
    ("ARI", "Arizona Cardinals"),
    ("ATL", "Atlanta Falcons"),
    ("BAL", "Baltimore Ravens"),
    ("BUF", "Buffalo Bills"),
    ("CAR", "Carolina Panthers"),
    ("CHI", "Chicago Bears"),
    ("CIN", "Cincinnati Bengals"),
    ("CLE", "Cleveland Browns"),
    ("DAL", "Dallas Cowboys"),
    ("DEN", "Denver Broncos"),
    ("DET", "Detroit Lions"),
    ("GB", "Green Bay Packers"),
    ("HOU", "Houston Texans"),
    ("IND", "Indianapolis Colts"),
    ("JAX", "Jacksonville Jaguars"),
    ("KC", "Kansas City Chiefs"),
    ("LV", "Las Vegas Raiders"),
    ("LAC", "Los Angeles Chargers"),
    ("LAR", "Los Angeles Rams"),
    ("MIA", "Miami Dolphins"),
    ("MIN", "Minnesota Vikings"),
    ("NE", "New England Patriots"),
    ("NO", "New Orleans Saints"),
    ("NYG", "New York Giants"),
    ("NYJ", "New York Jets"),
    ("PHI", "Philadelphia Eagles"),
    ("PIT", "Pittsburgh Steelers"),
    ("SEA", "Seattle Seahawks"),
    ("SF", "San Francisco 49ers"),
    ("TB", "Tampa Bay Buccaneers"),
    ("TEN", "Tennessee Titans"),
    ("WAS", "Washington Commanders"),
]

ROSTER_TEMPLATE: dict[str, int] = {
    "QB": 3,
    "RB": 4,
    "WR": 6,
    "TE": 3,
    "OL": 9,
    "DL": 8,
    "LB": 7,
    "CB": 6,
    "S": 4,
    "K": 1,
    "P": 1,
    "ST": 1,
}

FALLBACK_FIRST_NAMES = [
    "Alex",
    "Jordan",
    "Taylor",
    "Casey",
    "Dakota",
    "Riley",
    "Cameron",
    "Jamie",
    "Kendall",
    "Micah",
    "Morgan",
    "Parker",
    "Reese",
    "Skyler",
    "Shawn",
]

FALLBACK_LAST_NAMES = [
    "Walker",
    "Adams",
    "Brooks",
    "Campbell",
    "Dawson",
    "Ellis",
    "Foster",
    "Griffin",
    "Hayes",
    "Jenkins",
    "Knight",
    "Marshall",
    "Patterson",
    "Reed",
    "Warren",
]

COACH_LAST_NAMES = [
    "Belmont",
    "Carroll",
    "Dorsey",
    "Everett",
    "Fangio",
    "Gruden",
    "Harper",
    "Iverson",
    "Judge",
    "Kelly",
    "Lewis",
    "Martinez",
    "Payne",
    "Quinn",
    "Rhodes",
    "Smith",
    "Tobin",
    "Ulrich",
    "Verner",
    "Zimmer",
]

COACH_FIRST_NAMES = [
    "Arthur",
    "Bill",
    "Courtney",
    "Dante",
    "Elliot",
    "Frank",
    "Gus",
    "Harvey",
    "Isaiah",
    "Justin",
    "Kyle",
    "Lance",
    "Marvin",
    "Nate",
    "Omar",
    "Pat",
    "Quentin",
    "Raheem",
    "Sean",
    "Todd",
]


@dataclass(frozen=True)
class PlayerIdentity:
    name: str
    position: str
    position_group: str


def build_console() -> Console:
    theme = Theme(
        {
            "success": "green",
            "warning": "yellow",
            "error": "red",
            "info": "cyan",
            "accent": "bold blue",
        }
    )
    return Console(theme=theme)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate synthetic NFL datasets using nflreadpy player names."
    )
    parser.add_argument(
        "--start-year",
        type=int,
        default=1999,
        help="First season to include (e.g., 1999).",
    )
    parser.add_argument(
        "--end-year",
        type=int,
        default=date.today().year,
        help="Last season to include (e.g., 2025).",
    )
    parser.add_argument(
        "--roster-size",
        type=int,
        default=53,
        help="Approximate players per team per season.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed for deterministic output.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Override output directory (defaults to data/processed).",
    )
    parser.add_argument(
        "--schema-version",
        type=str,
        default=None,
        help="Schema version string to stamp onto records (defaults to config).",
    )
    return parser.parse_args()


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def adjust_roster_template(
    base_template: dict[str, int], target_size: int, rng: random.Random
) -> dict[str, int]:
    """Resize the roster template to hit a target player count per team."""
    template = dict(base_template)
    current = sum(template.values())
    if target_size <= 0:
        return template
    while current < target_size:
        pick = rng.choice(list(template.keys()))
        template[pick] += 1
        current += 1
    shrinkable = [k for k, v in template.items() if v > 1]
    while current > target_size and shrinkable:
        pick = rng.choice(shrinkable)
        template[pick] -= 1
        current -= 1
        shrinkable = [k for k, v in template.items() if v > 1]
    return template


def position_group_for(position: str) -> str:
    pos = position.upper()
    if pos in {"QB"}:
        return "QB"
    if pos in {"RB", "FB"}:
        return "RB"
    if pos == "WR":
        return "WR"
    if pos == "TE":
        return "TE"
    if pos in {"C", "G", "T", "OT", "OG", "OC", "OL"}:
        return "OL"
    if pos in {"DE", "DT", "NT", "DL"}:
        return "DL"
    if pos in {"ILB", "OLB", "LB", "MLB"}:
        return "LB"
    if pos in {"CB"}:
        return "CB"
    if pos in {"S", "SS", "FS", "SAF", "DB"}:
        return "S"
    if pos == "K":
        return "K"
    if pos == "P":
        return "P"
    if pos == "LS":
        return "ST"
    return "ATH"


def stable_id(*parts: str) -> str:
    return str(uuid5(NAMESPACE_DNS, "|".join(parts)))


def load_player_identities(
    *, start_year: int, end_year: int, rng: random.Random, console: Console
) -> list[PlayerIdentity]:
    try:
        import nflreadpy as nfl
    except Exception as exc:  # pragma: no cover - optional dependency
        console.print(f"[warning]nflreadpy unavailable: {exc}. Falling back to generated names.")
        return build_fallback_names(rng, target=2000)

    try:
        df = nfl.load_players()
        mask = (
            (df["rookie_season"].fill_null(start_year) <= end_year)
            & (df["last_season"].fill_null(end_year) >= start_year)
        )
        filtered = df.filter(mask)
        subset = (
            filtered.select(["display_name", "position", "position_group"])
            .drop_nulls("display_name")
            .unique("display_name")
        )
        identities: list[PlayerIdentity] = []
        for row in subset.to_dicts():
            pos = str(row.get("position") or "ATH").strip() or "ATH"
            group = str(row.get("position_group") or position_group_for(pos)).strip() or "ATH"
            identities.append(
                PlayerIdentity(
                    name=row["display_name"],
                    position=pos.upper(),
                    position_group=group.upper(),
                )
            )
        if not identities:
            console.print(
                "[warning]No names returned from nflreadpy; switching to fallback name pool."
            )
            return build_fallback_names(rng, target=2000)
        console.print(
            f"[success]Loaded {len(identities):,} real player names from nflreadpy "
            f"for {start_year}-{end_year}."
        )
        return identities
    except Exception as exc:  # pragma: no cover - network/HTTP issues
        console.print(
            "[warning]nflreadpy player pull failed; generating fallback names instead.\n"
            f"Reason: {exc}"
        )
        return build_fallback_names(rng, target=2000)


def build_fallback_names(rng: random.Random, *, target: int) -> list[PlayerIdentity]:
    identities: list[PlayerIdentity] = []
    while len(identities) < target:
        first = rng.choice(FALLBACK_FIRST_NAMES)
        last = rng.choice(FALLBACK_LAST_NAMES)
        pos = rng.choice(list(ROSTER_TEMPLATE.keys()))
        group = position_group_for(pos)
        identities.append(PlayerIdentity(name=f"{first} {last}", position=pos, position_group=group))
    return identities


def ratings_block(rng: random.Random, *, base: float | None = None) -> dict[str, float]:
    overall = base if base is not None else rng.normalvariate(70, 8)
    overall = clamp(overall, 40, 99)
    return {
        "overall": round(overall, 1),
        "athleticism": round(clamp(overall + rng.normalvariate(0, 4), 35, 99), 1),
        "technical": round(clamp(overall + rng.normalvariate(0, 5), 35, 99), 1),
        "intangibles": round(clamp(overall + rng.normalvariate(0, 3), 35, 99), 1),
        "potential": round(clamp(overall + rng.normalvariate(1.5, 3), 40, 99), 1),
    }


def player_stats(position: str, rng: random.Random) -> dict[str, float]:
    base = {
        "games_played": rng.randint(8, 17),
        "snaps": rng.randint(150, 1150),
        "passing_yards": 0.0,
        "passing_tds": 0.0,
        "interceptions": 0.0,
        "rushing_yards": 0.0,
        "rushing_tds": 0.0,
        "receiving_yards": 0.0,
        "receiving_tds": 0.0,
        "tackles": 0.0,
        "sacks": 0.0,
        "forced_fumbles": 0.0,
        "def_interceptions": 0.0,
        "field_goals_made": 0.0,
        "punts": 0.0,
    }
    pos = position.upper()
    if pos == "QB":
        base["passing_yards"] = clamp(rng.normalvariate(3800, 750), 500, 6000)
        base["passing_tds"] = clamp(rng.normalvariate(27, 8), 2, 55)
        base["interceptions"] = clamp(rng.normalvariate(11, 5), 0, 30)
        base["rushing_yards"] = clamp(rng.normalvariate(220, 200), 0, 1200)
        base["rushing_tds"] = clamp(rng.normalvariate(3, 2), 0, 12)
    elif pos in {"RB", "FB"}:
        base["rushing_yards"] = clamp(rng.normalvariate(980, 320), 50, 2000)
        base["rushing_tds"] = clamp(rng.normalvariate(8, 4), 0, 25)
        base["receiving_yards"] = clamp(rng.normalvariate(310, 180), 0, 900)
        base["receiving_tds"] = clamp(rng.normalvariate(2, 2), 0, 10)
    elif pos == "WR":
        base["receiving_yards"] = clamp(rng.normalvariate(1050, 350), 100, 2200)
        base["receiving_tds"] = clamp(rng.normalvariate(7, 3), 0, 20)
    elif pos == "TE":
        base["receiving_yards"] = clamp(rng.normalvariate(720, 220), 80, 1500)
        base["receiving_tds"] = clamp(rng.normalvariate(6, 3), 0, 18)
    elif pos in {"CB", "S", "SAF", "DB"}:
        base["tackles"] = clamp(rng.normalvariate(70, 25), 10, 160)
        base["def_interceptions"] = clamp(rng.normalvariate(2.5, 2.5), 0, 12)
        base["forced_fumbles"] = clamp(rng.normalvariate(1.0, 1.2), 0, 8)
    elif pos in {"LB", "ILB", "OLB", "MLB"}:
        base["tackles"] = clamp(rng.normalvariate(105, 25), 20, 180)
        base["sacks"] = clamp(rng.normalvariate(4, 3), 0, 20)
        base["forced_fumbles"] = clamp(rng.normalvariate(1.5, 1.2), 0, 8)
    elif pos in {"DE", "DT", "NT", "DL"}:
        base["tackles"] = clamp(rng.normalvariate(55, 15), 10, 120)
        base["sacks"] = clamp(rng.normalvariate(6, 4), 0, 22)
        base["forced_fumbles"] = clamp(rng.normalvariate(1.0, 0.8), 0, 6)
    elif pos in {"K"}:
        base["field_goals_made"] = clamp(rng.normalvariate(25, 6), 10, 45)
    elif pos in {"P"}:
        base["punts"] = clamp(rng.normalvariate(70, 15), 30, 120)
    return {k: round(v, 2) if isinstance(v, float) else v for k, v in base.items()}


def group_names_by_position(
    names: Iterable[PlayerIdentity],
) -> dict[str, list[PlayerIdentity]]:
    grouped: dict[str, list[PlayerIdentity]] = {}
    for identity in names:
        grouped.setdefault(identity.position_group, []).append(identity)
    return grouped


def build_roster(
    grouped_names: dict[str, list[PlayerIdentity]],
    fallback_pool: Sequence[PlayerIdentity],
    rng: random.Random,
    roster_template: dict[str, int],
) -> list[PlayerIdentity]:
    roster: list[PlayerIdentity] = []
    for group, count in roster_template.items():
        candidates = grouped_names.get(group) or fallback_pool
        if not candidates:
            continue
        if len(candidates) >= count:
            roster.extend(rng.sample(candidates, count))
        else:
            roster.extend(rng.choices(candidates, k=count))
    rng.shuffle(roster)
    return roster


def generate_players(
    *,
    seasons: Sequence[int],
    roster_template: dict[str, int],
    team_catalog: Sequence[tuple[str, str]],
    names: list[PlayerIdentity],
    rng: random.Random,
    schema_version: str,
    progress: Progress,
    task_id: int,
) -> tuple[pl.DataFrame, dict[tuple[int, str], list[float]]]:
    grouped = group_names_by_position(names)
    team_overall: dict[tuple[int, str], list[float]] = {}
    records: list[dict[str, object]] = []
    today = date.today()
    for season in seasons:
        for abbr, team_name in team_catalog:
            roster = build_roster(grouped, names, rng, roster_template)
            for slot, identity in enumerate(roster):
                rating = ratings_block(rng)
                stats = player_stats(identity.position, rng)
                record = {
                    "id": stable_id("player", identity.name, str(season), abbr, str(slot)),
                    "name": identity.name,
                    "entity_type": "player",
                    "position": identity.position,
                    "team": abbr,
                    "era": str(season),
                    "ratings": rating,
                    "stats": stats,
                    "schema_version": schema_version,
                    "source": "synthetic:nflreadpy-names",
                    "updated_at": today,
                    "team_name": team_name,
                    "season": season,
                }
                records.append(record)
                team_overall.setdefault((season, abbr), []).append(rating["overall"])
            progress.advance(task_id)
    return pl.from_dicts(records), team_overall


def generate_teams(
    *,
    seasons: Sequence[int],
    team_catalog: Sequence[tuple[str, str]],
    team_overall: dict[tuple[int, str], list[float]],
    rng: random.Random,
    schema_version: str,
) -> tuple[pl.DataFrame, dict[tuple[int, str], dict[str, float]]]:
    records: list[dict[str, object]] = []
    summary: dict[tuple[int, str], dict[str, float]] = {}
    today = date.today()
    for season in seasons:
        for abbr, team_name in team_catalog:
            ratings_list = team_overall.get((season, abbr), [])
            base_overall = sum(ratings_list) / len(ratings_list) if ratings_list else rng.uniform(60, 82)
            rating = ratings_block(rng, base=base_overall)
            wins = clamp(rating["overall"] / 6.5 + rng.normalvariate(-2, 2.5), 0, 17)
            wins_int = int(round(wins))
            losses_int = max(0, 17 - wins_int)
            points_for = int(clamp(rng.normalvariate(320 + (rating["overall"] - 65) * 6, 45), 180, 620))
            points_against = int(clamp(rng.normalvariate(330 - (rating["overall"] - 65) * 5, 45), 180, 620))
            stats = {
                "wins": wins_int,
                "losses": losses_int,
                "points_for": points_for,
                "points_against": points_against,
                "epa_per_play": round(rng.normalvariate((rating["overall"] - 70) / 100, 0.05), 3),
                "success_rate": round(clamp(rng.normalvariate(0.46, 0.05), 0.3, 0.6), 3),
                "turnover_diff": round(rng.normalvariate((rating["overall"] - 70) / 20, 3), 1),
                "playoff_prob": round(clamp((rating["overall"] - 60) / 50, 0, 1), 3),
            }
            record = {
                "id": stable_id("team", abbr, str(season)),
                "name": team_name,
                "entity_type": "team",
                "era": str(season),
                "ratings": rating,
                "stats": stats,
                "schema_version": schema_version,
                "source": "synthetic:aggregate",
                "updated_at": today,
                "team": abbr,
                "season": season,
            }
            summary[(season, abbr)] = {
                "overall": rating["overall"],
                "wins": wins_int,
                "losses": losses_int,
                "playoff_prob": stats["playoff_prob"],
            }
            records.append(record)
    return pl.from_dicts(records), summary


def generate_coaches(
    *,
    seasons: Sequence[int],
    team_catalog: Sequence[tuple[str, str]],
    team_summary: dict[tuple[int, str], dict[str, float]],
    rng: random.Random,
    schema_version: str,
) -> pl.DataFrame:
    records: list[dict[str, object]] = []
    today = date.today()
    for season in seasons:
        for abbr, team_name in team_catalog:
            summary = team_summary.get((season, abbr), {"overall": 70.0, "wins": 6, "losses": 11})
            name = f"{rng.choice(COACH_FIRST_NAMES)} {rng.choice(COACH_LAST_NAMES)}"
            rating = ratings_block(rng, base=summary["overall"] + rng.normalvariate(0, 3))
            stats = {
                "wins": summary["wins"],
                "losses": summary["losses"],
                "playoff_prob": round(summary.get("playoff_prob", 0.25), 3),
                "tenure_years": round(rng.uniform(0.5, 6), 1),
            }
            record = {
                "id": stable_id("coach", name, abbr, str(season)),
                "name": name,
                "entity_type": "coach",
                "team": abbr,
                "era": str(season),
                "ratings": rating,
                "stats": stats,
                "schema_version": schema_version,
                "source": "synthetic:coaches",
                "updated_at": today,
                "team_name": team_name,
                "season": season,
            }
            records.append(record)
    return pl.from_dicts(records)


def _first_sunday_of_september(year: int) -> date:
    seed = date(year, 9, 5)
    while seed.weekday() != 6:  # 6 == Sunday
        seed += timedelta(days=1)
    return seed


def generate_games(
    *,
    seasons: Sequence[int],
    team_catalog: Sequence[tuple[str, str]],
    rng: random.Random,
    schema_version: str,
    weeks: int = 18,
) -> pl.DataFrame:
    records: list[dict[str, object]] = []
    today = date.today()
    kickoff_times = [time(13, 0), time(16, 25), time(20, 20)]
    team_lookup = {abbr: name for abbr, name in team_catalog}

    def weekly_pairings(teams: Sequence[str]) -> list[tuple[str, str]]:
        pool = list(teams)
        rng.shuffle(pool)
        pairs = []
        for idx in range(0, len(pool), 2):
            if idx + 1 >= len(pool):
                break
            home, away = pool[idx], pool[idx + 1]
            if rng.random() < 0.45:
                home, away = away, home
            pairs.append((home, away))
        return pairs

    for season in seasons:
        base_sunday = _first_sunday_of_september(season)
        teams = [abbr for abbr, _ in team_catalog]
        for week in range(1, weeks + 1):
            week_pairs = weekly_pairings(teams)
            for home, away in week_pairs:
                start_date = base_sunday + timedelta(days=7 * (week - 1))
                start_dt = datetime.combine(start_date, rng.choice(kickoff_times))
                status = "final" if start_date <= today else "scheduled"
                home_score = away_score = None
                if status == "final":
                    home_score = rng.randint(10, 42)
                    away_score = rng.randint(10, 42)
                    # Slight tilt for home field.
                    home_score = int(round(home_score + rng.normalvariate(1.5, 3)))
                records.append(
                    {
                        "id": stable_id("game", str(season), f"wk{week}", home, away),
                        "season": season,
                        "week": week,
                        "home_team": home,
                        "away_team": away,
                        "location": f"{team_lookup.get(home, home)} Stadium",
                        "start_time": start_dt,
                        "status": status,
                        "is_postseason": False,
                        "playoff_round": None,
                        "home_score": home_score,
                        "away_score": away_score,
                        "schema_version": schema_version,
                        "source": "synthetic:schedule",
                    }
                )

        # Simple postseason bracket with placeholder matchups.
        rounds: list[tuple[str, int]] = [
            ("Wild Card", 6),
            ("Divisional", 4),
            ("Conference", 2),
            ("Super Bowl", 1),
        ]
        current_week = weeks
        pool = list(teams)
        for round_name, game_count in rounds:
            current_week += 1
            rng.shuffle(pool)
            for i in range(game_count):
                if len(pool) < 2:
                    pool = list(teams)
                    rng.shuffle(pool)
                home, away = pool[i % len(pool)], pool[(i + 1) % len(pool)]
                start_date = base_sunday + timedelta(days=7 * (current_week - 1))
                start_dt = datetime.combine(start_date, rng.choice(kickoff_times))
                status = "final" if start_date <= today else "scheduled"
                home_score = away_score = None
                if status == "final":
                    home_score = rng.randint(13, 38)
                    away_score = rng.randint(10, 34)
                    home_score = int(round(home_score + rng.normalvariate(1.0, 2.5)))
                records.append(
                    {
                        "id": stable_id("game", str(season), f"post-{round_name}-{i}", home, away),
                        "season": season,
                        "week": current_week,
                        "home_team": home,
                        "away_team": away,
                        "location": f"{team_lookup.get(home, home)} Stadium",
                        "start_time": start_dt,
                        "status": status,
                        "is_postseason": True,
                        "playoff_round": round_name,
                        "home_score": home_score,
                        "away_score": away_score,
                        "schema_version": schema_version,
                        "source": "synthetic:schedule",
                    }
                )
    games_schema = {
        "id": pl.Utf8,
        "season": pl.Int64,
        "week": pl.Int64,
        "home_team": pl.Utf8,
        "away_team": pl.Utf8,
        "location": pl.Utf8,
        "start_time": pl.Datetime,
        "status": pl.Utf8,
        "is_postseason": pl.Boolean,
        "playoff_round": pl.Utf8,
        "home_score": pl.Int64,
        "away_score": pl.Int64,
        "schema_version": pl.Utf8,
        "source": pl.Utf8,
    }
    return pl.from_dicts(records, schema=games_schema)


def write_parquet(df: pl.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(path, compression="zstd")
    return path


def human_bytes(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def render_results(
    *,
    console: Console,
    players_path: Path,
    teams_path: Path,
    coaches_path: Path,
    games_path: Path,
    players_df: pl.DataFrame,
    teams_df: pl.DataFrame,
    coaches_df: pl.DataFrame,
    games_df: pl.DataFrame,
    seasons: Sequence[int],
) -> None:
    size_table = Table(title="Data package sizes", expand=True)
    size_table.add_column("Dataset", justify="left", style="accent")
    size_table.add_column("Rows", justify="right")
    size_table.add_column("File size", justify="right")
    for label, path, df in [
        ("Players", players_path, players_df),
        ("Teams", teams_path, teams_df),
        ("Coaches", coaches_path, coaches_df),
        ("Games", games_path, games_df),
    ]:
        size_table.add_row(label, f"{len(df):,}", human_bytes(path.stat().st_size))

    player_overall = players_df.select(pl.col("ratings").struct.field("overall").mean()).item()
    team_overall = teams_df.select(pl.col("ratings").struct.field("overall").mean()).item()
    coach_overall = coaches_df.select(pl.col("ratings").struct.field("overall").mean()).item()
    stat_table = Table(title="Generated data statistics", expand=True)
    stat_table.add_column("Metric", style="accent")
    stat_table.add_column("Value", justify="right")
    stat_table.add_row("Seasons covered", f"{min(seasons)}-{max(seasons)}")
    stat_table.add_row("Players per season (avg)", f"{len(players_df) // len(seasons):,}")
    stat_table.add_row("Teams per season", f"{len(teams_df) // len(seasons):,}")
    stat_table.add_row("Games per season", f"{len(games_df) // len(seasons):,}")
    stat_table.add_row("Average player overall", f"{player_overall:.1f}")
    stat_table.add_row("Average team overall", f"{team_overall:.1f}")
    stat_table.add_row("Average coach overall", f"{coach_overall:.1f}")
    stat_table.add_row(
        "Unique positions", str(players_df.select(pl.col("position").n_unique()).item())
    )

    console.print(size_table)
    console.print(stat_table)


def main() -> None:
    args = parse_args()
    console = build_console()
    rng = random.Random(args.seed)
    seasons = list(range(args.start_year, args.end_year + 1))
    if not seasons:
        console.print("[error]No seasons resolved from the provided range.")
        raise SystemExit(1)
    if args.start_year > args.end_year:
        console.print("[error]Start year must be less than or equal to end year.")
        raise SystemExit(1)
    roster_template = adjust_roster_template(ROSTER_TEMPLATE, args.roster_size, rng)

    paths = AppPaths.from_env()
    config = load_config(paths)
    output_root = Path(args.output_root) if args.output_root else paths.data_processed
    output_root.mkdir(parents=True, exist_ok=True)
    schema_version = args.schema_version or config.default_schema_version

    console.print(
        Panel.fit(
            "\n".join(
                [
                    "[accent]Gridiron Labs synthetic data generator[/accent]",
                    f"Seasons: {args.start_year}-{args.end_year}  "
                    f"Roster size: {sum(roster_template.values())}  "
                    f"Schema: {schema_version}",
                    f"Output: {output_root}",
                ]
            ),
            border_style="accent",
        )
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        fetch_task = progress.add_task("Fetching player names via nflreadpy", total=None)
        names = load_player_identities(
            start_year=args.start_year, end_year=args.end_year, rng=rng, console=console
        )
        progress.update(fetch_task, total=1, completed=1)

        gen_task = progress.add_task(
            "Generating player rosters and stats", total=len(seasons) * len(TEAM_CATALOG)
        )
        players_df, team_overall = generate_players(
            seasons=seasons,
            roster_template=roster_template,
            team_catalog=TEAM_CATALOG,
            names=names,
            rng=rng,
            schema_version=schema_version,
            progress=progress,
            task_id=gen_task,
        )

        team_df, team_summary = generate_teams(
            seasons=seasons,
            team_catalog=TEAM_CATALOG,
            team_overall=team_overall,
            rng=rng,
            schema_version=schema_version,
        )
        coaches_df = generate_coaches(
            seasons=seasons,
            team_catalog=TEAM_CATALOG,
            team_summary=team_summary,
            rng=rng,
            schema_version=schema_version,
        )
        games_task_total = len(seasons) * 18 * (len(TEAM_CATALOG) // 2)
        games_task = progress.add_task("Generating schedules", total=games_task_total)
        games_df = generate_games(
            seasons=seasons,
            team_catalog=TEAM_CATALOG,
            rng=rng,
            schema_version=schema_version,
            weeks=18,
        )
        progress.update(games_task, completed=games_task_total)

        write_task = progress.add_task("Writing Parquet datasets", total=4)
        players_path = write_parquet(players_df, output_root / "players.parquet")
        progress.advance(write_task)
        teams_path = write_parquet(team_df, output_root / "teams.parquet")
        progress.advance(write_task)
        coaches_path = write_parquet(coaches_df, output_root / "coaches.parquet")
        progress.advance(write_task)
        games_path = write_parquet(games_df, output_root / "games.parquet")
        progress.advance(write_task)

    render_results(
        console=console,
        players_path=players_path,
        teams_path=teams_path,
        coaches_path=coaches_path,
        games_path=games_path,
        players_df=players_df,
        teams_df=team_df,
        coaches_df=coaches_df,
        games_df=games_df,
        seasons=seasons,
    )
    console.print(
        "[success]Synthetic data generation complete. "
        "Parquet tables are ready under data/processed."
    )


if __name__ == "__main__":
    raise SystemExit(main())


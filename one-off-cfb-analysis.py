"""
One-off college football schedule difficulty split analyzer.

Usage:
    python one-off-cfb-analysis.py <start_year>

Notes:
- End year is fixed to 2025.
- Relies on the CollegeFootballData.com API (free, but requires an API key).
  Set environment variable CFBD_API_KEY (or CFB_API_KEY) before running.
- Uses the AP Top 25 poll to:
  * Count preseason-ranked opponents scheduled (home vs away).
  * Count final-ranked opponents played (home vs away).
- Neutral-site games are ignored.
- Output is a Rich table sorted by a weighted difficulty score.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

import requests
from rich import box
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

API_BASE = "https://api.collegefootballdata.com"
POLL_NAME = "AP Top 25"
THRESHOLDS = (5, 10, 15, 20, 25)
END_YEAR = 2025

# Mapping of display name -> CFBD team name
TEAM_NAME_MAP: Dict[str, str] = {
    "Ohio State": "Ohio State",
    "Michigan": "Michigan",
    "Oregon": "Oregon",
    "USC": "USC",
    "Penn State": "Penn State",
    "Miami (Florida)": "Miami",
    "Clemson": "Clemson",
    "Boston College": "Boston College",
    "Georgia": "Georgia",
    "Alabama": "Alabama",
    "Texas": "Texas",
    "Tennessee": "Tennessee",
    "Colorado": "Colorado",
    "Iowa State": "Iowa State",
    "BYU": "BYU",
    "Army": "Army",
    "Navy": "Navy",
}


@dataclass
class ThresholdCounts:
    home: int = 0
    away: int = 0

    def as_str(self) -> str:
        return f"{self.home:02d}-{self.away:02d}"


@dataclass
class TeamResult:
    preseason: Dict[int, ThresholdCounts] = field(
        default_factory=lambda: {t: ThresholdCounts() for t in THRESHOLDS}
    )
    final: Dict[int, ThresholdCounts] = field(
        default_factory=lambda: {t: ThresholdCounts() for t in THRESHOLDS}
    )
    score: float = 0.0


def get_api_key() -> Optional[str]:
    return os.environ.get("CFBD_API_KEY") or os.environ.get("CFB_API_KEY")


def fetch_json(url: str, params: Dict[str, object]) -> Optional[object]:
    headers = {}
    api_key = get_api_key()
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        if resp.status_code != 200:
            return None
        return resp.json()
    except Exception:
        return None


def fetch_polls_for_year(year: int) -> List[dict]:
    data = fetch_json(f"{API_BASE}/polls", {"year": year, "poll": POLL_NAME})
    if not isinstance(data, list):
        return []
    # Ensure ordered by week ascending.
    return sorted(data, key=lambda p: p.get("week", 9999))


def rankings_to_map(poll_entry: dict) -> Dict[str, int]:
    rankings = poll_entry.get("rankings", []) if isinstance(poll_entry, dict) else []
    return {r["school"]: int(r["rank"]) for r in rankings if "school" in r and "rank" in r}


def fetch_games_for_team_year(team: str, year: int) -> List[dict]:
    params = {
        "year": year,
        "team": team,
        "seasonType": "regular",
    }
    data = fetch_json(f"{API_BASE}/games", params)
    if not isinstance(data, list):
        return []
    return data


def location_and_opponent(game: dict, team: str) -> Optional[Tuple[str, bool]]:
    """Return (opponent, is_home) if determinate and non-neutral, else None."""
    if not isinstance(game, dict) or game.get("neutral_site"):
        return None
    home_team = game.get("home_team")
    away_team = game.get("away_team")
    if home_team == team:
        return away_team, True
    if away_team == team:
        return home_team, False
    return None


def update_counts(
    counts: Dict[int, ThresholdCounts],
    rank: int,
    is_home: bool,
) -> None:
    for threshold in THRESHOLDS:
        if rank <= threshold:
            target = counts[threshold]
            if is_home:
                target.home += 1
            else:
                target.away += 1


def rank_points(rank: int) -> float:
    return max(0.0, 26.0 - float(rank))


def weighted_score(
    preseason_rank: Optional[int],
    final_rank: Optional[int],
    is_home: bool,
) -> float:
    loc_factor = 1.15 if not is_home else 1.0  # slightly reward away difficulty
    score = 0.0
    if preseason_rank is not None:
        score += rank_points(preseason_rank) * 0.45
    if final_rank is not None:
        score += rank_points(final_rank) * 0.55
    return score * loc_factor


def process_team_seasons(
    display_name: str,
    api_name: str,
    years: Iterable[int],
    polls_by_year: Dict[int, List[dict]],
    progress: Progress,
    task_id: int,
) -> TeamResult:
    result = TeamResult()
    for year in years:
        progress.update(task_id, advance=1)
        polls = polls_by_year.get(year, [])
        if not polls:
            continue
        preseason_poll = polls[0]
        final_poll = polls[-1]
        preseason_map = rankings_to_map(preseason_poll)
        final_map = rankings_to_map(final_poll)

        games = fetch_games_for_team_year(api_name, year)
        for game in games:
            loc_info = location_and_opponent(game, api_name)
            if not loc_info:
                continue
            opponent, is_home = loc_info
            pre_rank = preseason_map.get(opponent)
            fin_rank = final_map.get(opponent)

            if pre_rank:
                update_counts(result.preseason, pre_rank, is_home)
            if fin_rank:
                update_counts(result.final, fin_rank, is_home)
            if pre_rank or fin_rank:
                result.score += weighted_score(pre_rank, fin_rank, is_home)
    return result


def build_table(console: Console, results: Dict[str, TeamResult]) -> None:
    table = Table(
        title="Quality Opponent Splits (Home vs Away) through 2025",
        box=box.MINIMAL_DOUBLE_HEAD,
        header_style="bold cyan",
    )
    table.add_column("Team", style="bold white")
    table.add_column("Pre AP5", justify="center")
    table.add_column("Final AP5", justify="center")
    table.add_column("Pre AP10", justify="center")
    table.add_column("Final AP10", justify="center")
    table.add_column("Pre AP15", justify="center")
    table.add_column("Final AP15", justify="center")
    table.add_column("Pre AP20", justify="center")
    table.add_column("Final AP20", justify="center")
    table.add_column("Pre AP25", justify="center")
    table.add_column("Final AP25", justify="center")
    table.add_column("Weighted Score", justify="right")

    sorted_items = sorted(
        results.items(), key=lambda item: item[1].score, reverse=True
    )

    for team, res in sorted_items:
        table.add_row(
            team,
            res.preseason[5].as_str(),
            res.final[5].as_str(),
            res.preseason[10].as_str(),
            res.final[10].as_str(),
            res.preseason[15].as_str(),
            res.final[15].as_str(),
            res.preseason[20].as_str(),
            res.final[20].as_str(),
            res.preseason[25].as_str(),
            res.final[25].as_str(),
            f"{res.score:7.2f}",
        )

    console.print(table)


def validate_year(start_year: int) -> None:
    current_year = END_YEAR
    if start_year > END_YEAR:
        raise ValueError(f"start_year cannot exceed {END_YEAR}")
    if start_year < 2000:
        raise ValueError("start_year must be 2000 or later for API completeness")
    if start_year > current_year:
        raise ValueError(f"start_year must be <= {current_year}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze home/away splits vs ranked opponents (AP Top 25)."
    )
    parser.add_argument(
        "start_year",
        type=int,
        help="First season to include (end year fixed at 2025).",
    )
    args = parser.parse_args()
    try:
        validate_year(args.start_year)
    except ValueError as exc:
        sys.stderr.write(f"[error] {exc}\n")
        sys.exit(1)

    years = list(range(args.start_year, END_YEAR + 1))
    console = Console()

    if not get_api_key():
        console.print(
            "[yellow]No CFBD_API_KEY found; the API may reject requests for heavy use.[/yellow]"
        )

    console.print(
        f"[bold green]Analyzing {len(TEAM_NAME_MAP)} teams from {years[0]} to {END_YEAR}[/bold green]"
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        poll_task = progress.add_task("Fetching polls", total=len(years))
        polls_by_year: Dict[int, List[dict]] = {}
        for year in years:
            polls_by_year[year] = fetch_polls_for_year(year)
            progress.update(poll_task, advance=1)

        sched_task = progress.add_task(
            "Processing schedules", total=len(years) * len(TEAM_NAME_MAP)
        )
        results: Dict[str, TeamResult] = {}
        for display_name, api_name in TEAM_NAME_MAP.items():
            result = process_team_seasons(
                display_name, api_name, years, polls_by_year, progress, sched_task
            )
            results[display_name] = result

    build_table(console, results)


if __name__ == "__main__":
    main()

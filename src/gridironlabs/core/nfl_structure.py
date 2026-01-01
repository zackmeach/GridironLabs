"""NFL structural metadata (conference/division/team mapping).

This is intentionally small and static for now so UI filters can work without
requiring upstream data enrichment.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TeamInfo:
    abbr: str
    name: str
    conference: str  # "AFC" | "NFC"
    division: str  # e.g. "AFC East"


# Canonical modern NFL alignment (32 teams).
TEAM_INFO: tuple[TeamInfo, ...] = (
    # AFC East
    TeamInfo("BUF", "Buffalo Bills", "AFC", "AFC East"),
    TeamInfo("MIA", "Miami Dolphins", "AFC", "AFC East"),
    TeamInfo("NE", "New England Patriots", "AFC", "AFC East"),
    TeamInfo("NYJ", "New York Jets", "AFC", "AFC East"),
    # AFC North
    TeamInfo("BAL", "Baltimore Ravens", "AFC", "AFC North"),
    TeamInfo("CIN", "Cincinnati Bengals", "AFC", "AFC North"),
    TeamInfo("CLE", "Cleveland Browns", "AFC", "AFC North"),
    TeamInfo("PIT", "Pittsburgh Steelers", "AFC", "AFC North"),
    # AFC South
    TeamInfo("HOU", "Houston Texans", "AFC", "AFC South"),
    TeamInfo("IND", "Indianapolis Colts", "AFC", "AFC South"),
    TeamInfo("JAX", "Jacksonville Jaguars", "AFC", "AFC South"),
    TeamInfo("TEN", "Tennessee Titans", "AFC", "AFC South"),
    # AFC West
    TeamInfo("DEN", "Denver Broncos", "AFC", "AFC West"),
    TeamInfo("KC", "Kansas City Chiefs", "AFC", "AFC West"),
    TeamInfo("LAC", "Los Angeles Chargers", "AFC", "AFC West"),
    TeamInfo("LV", "Las Vegas Raiders", "AFC", "AFC West"),
    # NFC East
    TeamInfo("DAL", "Dallas Cowboys", "NFC", "NFC East"),
    TeamInfo("NYG", "New York Giants", "NFC", "NFC East"),
    TeamInfo("PHI", "Philadelphia Eagles", "NFC", "NFC East"),
    TeamInfo("WAS", "Washington Commanders", "NFC", "NFC East"),
    # NFC North
    TeamInfo("CHI", "Chicago Bears", "NFC", "NFC North"),
    TeamInfo("DET", "Detroit Lions", "NFC", "NFC North"),
    TeamInfo("GB", "Green Bay Packers", "NFC", "NFC North"),
    TeamInfo("MIN", "Minnesota Vikings", "NFC", "NFC North"),
    # NFC South
    TeamInfo("ATL", "Atlanta Falcons", "NFC", "NFC South"),
    TeamInfo("CAR", "Carolina Panthers", "NFC", "NFC South"),
    TeamInfo("NO", "New Orleans Saints", "NFC", "NFC South"),
    TeamInfo("TB", "Tampa Bay Buccaneers", "NFC", "NFC South"),
    # NFC West
    TeamInfo("ARI", "Arizona Cardinals", "NFC", "NFC West"),
    TeamInfo("LAR", "Los Angeles Rams", "NFC", "NFC West"),
    TeamInfo("SEA", "Seattle Seahawks", "NFC", "NFC West"),
    TeamInfo("SF", "San Francisco 49ers", "NFC", "NFC West"),
)


TEAM_BY_ABBR: dict[str, TeamInfo] = {t.abbr: t for t in TEAM_INFO}
TEAM_BY_NAME: dict[str, TeamInfo] = {t.name.lower(): t for t in TEAM_INFO}


def normalize_team_abbr(raw: str | None) -> str | None:
    if raw is None:
        return None
    text = str(raw).strip()
    return text or None


def team_info_for_abbr(abbr: str | None) -> TeamInfo | None:
    key = normalize_team_abbr(abbr)
    if not key:
        return None
    return TEAM_BY_ABBR.get(key.upper())


def team_info_for_name(name: str | None) -> TeamInfo | None:
    if name is None:
        return None
    key = str(name).strip().lower()
    if not key:
        return None
    return TEAM_BY_NAME.get(key)


def team_abbr_for_name(name: str | None) -> str | None:
    info = team_info_for_name(name)
    return info.abbr if info else None


def team_name_for_abbr(abbr: str | None) -> str | None:
    info = team_info_for_abbr(abbr)
    return info.name if info else None


def list_conferences() -> tuple[str, str]:
    return ("AFC", "NFC")


def list_divisions(*, conference: str | None = None) -> list[str]:
    if conference is None:
        divs = {t.division for t in TEAM_INFO}
    else:
        conf = str(conference).strip().upper()
        divs = {t.division for t in TEAM_INFO if t.conference == conf}
    return sorted(divs)


def list_teams(
    *, conference: str | None = None, division: str | None = None
) -> list[TeamInfo]:
    conf = str(conference).strip().upper() if conference else None
    div = str(division).strip() if division else None

    teams = list(TEAM_INFO)
    if conf:
        teams = [t for t in teams if t.conference == conf]
    if div:
        teams = [t for t in teams if t.division == div]
    return sorted(teams, key=lambda t: t.name)


__all__ = [
    "TeamInfo",
    "TEAM_INFO",
    "TEAM_BY_ABBR",
    "TEAM_BY_NAME",
    "team_info_for_abbr",
    "team_info_for_name",
    "team_abbr_for_name",
    "team_name_for_abbr",
    "list_conferences",
    "list_divisions",
    "list_teams",
]


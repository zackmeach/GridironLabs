"""Adapter for sourcing data from nflreadpy with graceful fallbacks."""

from __future__ import annotations

from typing import Iterable

from gridironlabs.core.errors import MissingDependencyError
from gridironlabs.core.models import EntitySummary


class NFLReadPyAdapter:
    """Placeholder adapter to wrap nflreadpy usage."""

    def __init__(self, *, enabled: bool) -> None:
        self.enabled = enabled

    def fetch_players(self) -> Iterable[EntitySummary]:
        if not self.enabled:
            return []
        try:
            import nflreadpy  # type: ignore  # pragma: no cover
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise MissingDependencyError("nflreadpy is not installed") from exc
        _ = nflreadpy  # Prevent unused-import linting until integration lands.
        raise NotImplementedError("nflreadpy integration will be implemented later.")

    def fetch_teams(self) -> Iterable[EntitySummary]:
        if not self.enabled:
            return []
        try:
            import nflreadpy  # type: ignore  # pragma: no cover
            import requests
        except ImportError as exc:  # pragma: no cover
            raise MissingDependencyError("nflreadpy or requests is not installed") from exc

        from gridironlabs.core.config import AppPaths

        paths = AppPaths.from_env()
        logo_dir = paths.data_root / "external" / "logos"
        logo_dir.mkdir(parents=True, exist_ok=True)

        try:
            df = nflreadpy.load_teams()
        except Exception:
            # If nflreadpy fails (network, etc.), return empty
            return []

        summaries = []
        for row in df.to_dict(orient="records"):
            abbr = row.get("team_abbr")
            url = row.get("team_logo_espn")
            name = row.get("team_name")

            if not abbr or not name:
                continue

            local_path = logo_dir / f"{abbr}.png"
            if url and not local_path.exists():
                try:
                    resp = requests.get(url, timeout=10)
                    if resp.status_code == 200:
                        local_path.write_bytes(resp.content)
                except Exception:
                    # Log error but continue
                    pass

            summaries.append(
                EntitySummary(
                    id=f"team-{abbr}",
                    name=name,
                    entity_type="team",
                    team=abbr,
                    logo_url=url,
                    logo_path=str(local_path) if local_path.exists() else None,
                    source="nflreadpy",
                )
            )
        return summaries

    def fetch_coaches(self) -> Iterable[EntitySummary]:
        if not self.enabled:
            return []
        raise NotImplementedError("nflreadpy coach integration will be implemented later.")

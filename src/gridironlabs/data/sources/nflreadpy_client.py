 from __future__ import annotations
 
 from dataclasses import dataclass
 from typing import Any, Dict
 
 import pandas as pd
 
 try:
     import nflreadpy.api as nfl
 except Exception:  # pragma: no cover - dependency may be unavailable during scaffolding
     nfl = None  # type: ignore
 
 
 @dataclass
 class NFLReadClient:
     """
     Light wrapper around nflreadpy to centralize API usage.
     """
 
     def fetch_players(self) -> pd.DataFrame:
         if not nfl:
             raise RuntimeError("nflreadpy is not installed.")
         return nfl.load_players()
 
     def fetch_teams(self) -> pd.DataFrame:
         if not nfl:
             raise RuntimeError("nflreadpy is not installed.")
         return nfl.load_teams()
 
     def fetch_coaches(self) -> pd.DataFrame:
         if not nfl:
             raise RuntimeError("nflreadpy is not installed.")
         # nflreadpy may not expose coaches directly; placeholder for custom logic.
         return pd.DataFrame()
 
 
 def to_records(df: pd.DataFrame) -> Dict[str, Any]:
     """
     Convert a dataframe to record dict keyed by id for fast lookups.
     """
 
     if df.empty:
         return {}
     if "player_id" in df.columns:
         key = "player_id"
     elif "team_id" in df.columns:
         key = "team_id"
     else:
         key = df.columns[0]
     return {str(row[key]): row for _, row in df.iterrows()}

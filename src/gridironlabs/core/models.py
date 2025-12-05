 from __future__ import annotations
 
 from dataclasses import dataclass, field
 from datetime import date
 from typing import Dict, List, Optional
 
 RatingMap = Dict[str, int]
 
 
 @dataclass
 class PlayerSummary:
     player_id: str
     name: str
     position: str
     team: Optional[str] = None
     birth_date: Optional[date] = None
     ratings: RatingMap = field(default_factory=dict)
     stats: Dict[str, float] = field(default_factory=dict)
 
 
 @dataclass
 class TeamSummary:
     team_id: str
     name: str
     conference: Optional[str] = None
     division: Optional[str] = None
     ratings: RatingMap = field(default_factory=dict)
     stats: Dict[str, float] = field(default_factory=dict)
 
 
 @dataclass
 class CoachSummary:
     coach_id: str
     name: str
     role: str
     team: Optional[str] = None
     history: List[str] = field(default_factory=list)
     ratings: RatingMap = field(default_factory=dict)
     stats: Dict[str, float] = field(default_factory=dict)
 
 
 __all__ = [
     "PlayerSummary",
     "TeamSummary",
     "CoachSummary",
     "RatingMap",
 ]

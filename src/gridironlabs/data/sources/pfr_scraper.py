 from __future__ import annotations
 
 from dataclasses import dataclass
 from typing import Iterable
 
 import pandas as pd
 import requests
 from bs4 import BeautifulSoup
 
 
 @dataclass
 class PFRScraper:
     """
     Simplified placeholder scraper for Pro-Football-Reference.
     Intended to be replaced with fully robust scraping + caching.
     """
 
     base_url: str = "https://www.pro-football-reference.com"
     session: requests.Session | None = None
 
     def __post_init__(self) -> None:
         if self.session is None:
             self.session = requests.Session()
 
     def fetch_player_page(self, relative_path: str) -> str:
         url = f"{self.base_url}{relative_path}"
         response = self.session.get(url, timeout=30)
         response.raise_for_status()
         return response.text
 
     def parse_table(self, html: str, table_id: str) -> pd.DataFrame:
         soup = BeautifulSoup(html, "html.parser")
         table = soup.find("table", attrs={"id": table_id})
         if not table:
             return pd.DataFrame()
         headers = [th.get_text(strip=True) for th in table.find_all("th")]
         rows: list[list[str]] = []
         for tr in table.find_all("tr"):
             cells = [td.get_text(strip=True) for td in tr.find_all("td")]
             if cells:
                 rows.append(cells)
         return pd.DataFrame(rows, columns=headers[: len(rows[0])]) if rows else pd.DataFrame()
 
     def scrape_players(self, paths: Iterable[str]) -> pd.DataFrame:
         """
         Iterate through provided relative paths and concatenate basic tables.
         """
 
         frames = []
         for path in paths:
             html = self.fetch_player_page(path)
             frame = self.parse_table(html, table_id="stats")
             frames.append(frame)
         return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

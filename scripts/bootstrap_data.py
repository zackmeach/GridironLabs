 from __future__ import annotations
 
 from gridironlabs.core.config import load_config
 from gridironlabs.data.loaders.parquet_loader import save_parquet_table
 from gridironlabs.data.sources.nflreadpy_client import NFLReadClient
 from gridironlabs.data.sources.pfr_scraper import PFRScraper
 
 
 def main() -> None:
     config = load_config()
     client = NFLReadClient()
     scraper = PFRScraper()
 
     # TODO: extend with real scraping targets; this is a placeholder scaffold.
     players = client.fetch_players()
     teams = client.fetch_teams()
 
     save_parquet_table(players, config.paths.processed_data / "players.parquet")
     save_parquet_table(teams, config.paths.processed_data / "teams.parquet")
 
 
 if __name__ == "__main__":
     main()

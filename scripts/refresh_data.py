"""Placeholder data refresh script.

Intended responsibilities:
- Pull from nflreadpy and PFR adapters.
- Normalize/de-duplicate entity ids.
- Validate against Parquet schemas before writing to `data/processed`.
- Record provenance and schema version metadata.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import polars as pl
from gridironlabs.core.config import AppPaths, load_config
from gridironlabs.data.sources.nflreadpy_adapter import NFLReadPyAdapter


def main() -> int:
    paths = AppPaths.from_env()
    config = load_config(paths)
    
    # Respect the configured scraping flag (e.g., GRIDIRONLABS_ENABLE_SCRAPING).
    # If disabled, we skip remote pulls to keep the refresh script offline-friendly.
    scraping_enabled = config.enable_scraping
    
    nfl_source = NFLReadPyAdapter(enabled=scraping_enabled)
    
    print(f"Refreshing data...\n- Output: {paths.data_processed}")
    
    # 1. Fetch Teams (and Logos)
    print("Fetching teams and logos...")
    try:
        teams_list = list(nfl_source.fetch_teams())
        print(f"fetched {len(teams_list)} teams")
        
        # Verify logo paths exist
        logo_count = sum(1 for t in teams_list if t.logo_path and Path(t.logo_path).exists())
        print(f"Verified {logo_count} logos downloaded to {paths.data_external}/logos")

        # 2. Enrich existing teams.parquet with logo paths
        teams_parquet = paths.data_processed / "teams.parquet"
        if teams_parquet.exists():
            print(f"Updating {teams_parquet} with logo paths...")
            
            # Load existing synthetic data
            df_existing = pl.read_parquet(teams_parquet)
            
            # Create a mapping DataFrame from fetched teams
            # We only care about matching 'team' (abbr) -> 'logo_path', 'logo_url'
            updates = []
            for t in teams_list:
                if t.team and t.logo_path:
                    updates.append({
                        "team": t.team,
                        "new_logo_path": t.logo_path,
                        "new_logo_url": t.logo_url
                    })
            
            if updates:
                df_updates = pl.from_dicts(updates)
                
                # Join updates on 'team' column
                # We do a left join to preserve all existing rows (multiple seasons)
                df_enriched = df_existing.join(df_updates, on="team", how="left")
                
                # Coalesce: use new_logo_path if present, else keep existing (which is null)
                # Note: df_existing has 'logo_path' column which is all null.
                # We replace 'logo_path' with 'new_logo_path' where available.
                
                df_final = df_enriched.with_columns([
                    pl.col("new_logo_path").fill_null(pl.col("logo_path")).alias("logo_path"),
                    pl.col("new_logo_url").fill_null(pl.col("logo_url")).alias("logo_url")
                ]).drop(["new_logo_path", "new_logo_url"])
                
                # Write back
                df_final.write_parquet(teams_parquet, compression="zstd")
                print("Successfully updated teams.parquet with logos.")
            else:
                print("No updates to apply.")
        else:
            print(f"Warning: {teams_parquet} not found. Run generate_fake_nfl_data.py first.")
        
    except Exception as e:
        print(f"Error fetching teams: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    print("\nData refresh (partial) complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

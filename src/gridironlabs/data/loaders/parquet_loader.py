 from __future__ import annotations
 
from pathlib import Path
from typing import Literal
 
 import pandas as pd
 import pyarrow.parquet as pq
 
 Reader = Literal["pandas", "pyarrow"]
 
 
 def load_parquet_table(path: Path, reader: Reader = "pandas") -> pd.DataFrame:
     """
     Load a Parquet file into a DataFrame while keeping the UI responsive.
     """
 
     if reader == "pandas":
         return pd.read_parquet(path)
     if reader == "pyarrow":
         return pq.read_table(path).to_pandas()
     raise ValueError(f"Unsupported reader '{reader}'.")
 
 
 def ensure_directory(path: Path) -> None:
     """
     Create directory ancestors when missing (safe to call repeatedly).
     """
 
     path.mkdir(parents=True, exist_ok=True)
 
 
 def save_parquet_table(df: pd.DataFrame, path: Path, compression: str = "snappy") -> None:
     """
     Persist a DataFrame to Parquet with sensible defaults.
     """
 
     ensure_directory(path.parent)
     df.to_parquet(path, compression=compression, index=False)
 
 
 def has_parquet(path: Path) -> bool:
     return path.exists() and path.suffix == ".parquet"

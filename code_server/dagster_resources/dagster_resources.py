from dagster_polars import PolarsParquetIOManager
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"

POLARS_PARQUET_IO_MANAGER = PolarsParquetIOManager(base_dir=DATA_DIR)
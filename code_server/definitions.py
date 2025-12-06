from dagster import Definitions

from code_server.dagster_resources.dagster_resources import POLARS_PARQUET_IO_MANAGER
from code_server.data_pipeline import defs

resources = Definitions(resources={
    "polars_parquet_io_manager": POLARS_PARQUET_IO_MANAGER,
    
})
definitions = Definitions().merge(defs)


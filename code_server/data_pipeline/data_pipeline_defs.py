from code_server.data_pipeline.data_pipeline_assets import price_changes, stock_prices, send_stock_email
from code_server.data_pipeline.schedules.data_pipeline_schedule import daily_stock_schedule
from code_server.data_pipeline.data_pipeline_config import PARTITIONS_DEF
from dagster import Definitions, define_asset_job

data_pipeline_job = define_asset_job(
    name="data_pipeline_job",
    selection=["stock_prices", "price_changes", "send_stock_email"],
    partitions_def=PARTITIONS_DEF,
)

defs = Definitions(
    assets=[stock_prices, price_changes, send_stock_email],
    schedules=[daily_stock_schedule],
    jobs=[data_pipeline_job],
)
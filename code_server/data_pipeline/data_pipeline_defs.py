from code_server.data_pipeline.data_pipeline_assets import price_changes, stock_prices, send_stock_email
from code_server.data_pipeline.schedules.data_pipeline_schedule import daily_stock_schedule
from code_server.data_pipeline.data_pipeline_config import PARTITIONED_CONFIG
from dagster import Definitions, define_asset_job

data_pipeline_job = define_asset_job(
    name="data_pipeline_job",
    selection=["stock_prices", "price_changes", "send_stock_email"],
    config=PARTITIONED_CONFIG
)

defs = Definitions(
    assets=[stock_prices, price_changes, send_stock_email],
    schedules=[daily_stock_schedule],
    jobs=[data_pipeline_job],
)
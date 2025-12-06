from code_server.data_pipeline.data_pipeline_assets import price_changes, stock_prices, send_stock_email
from code_server.data_pipeline.schedules.data_pipeline_schedule import daily_stock_schedule
from dagster import Definitions

defs = Definitions(
    assets=[stock_prices, price_changes, send_stock_email],
    schedules=[daily_stock_schedule],
)
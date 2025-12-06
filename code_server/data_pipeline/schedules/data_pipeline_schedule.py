from dagster import ScheduleDefinition
from code_server.data_pipeline.data_pipeline_config import partitioned_config


daily_stock_schedule = ScheduleDefinition(
    name="daily_stock_price_update",
    job_name="data_pipeline_job",
    cron_schedule="0 17 * * 1-5",  # 5 PM on weekdays, Monday to Friday
    run_config_fn=partitioned_config,
    execution_timezone="America/Denver",
)
from dagster import ScheduleDefinition

daily_stock_schedule = ScheduleDefinition(
    name="daily_stock_price_update",
    target="*",  # Run all assets
    cron_schedule="0 17 * * 1-5",  # 5 PM on weekdays, Monday to Friday
)
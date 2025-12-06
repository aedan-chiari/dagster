from dagster import Config
from dagster import (
    PartitionedConfig,
    StaticPartitionsDefinition,
    static_partitioned_config,
    EnvVar
)
import os


class StockConfig(Config):
    """Configuration for stock symbols to track."""

    ticker: str
    api_key: str = EnvVar("ALPHA_VANTAGE_API_KEY")


class EmailConfig(Config):
    """Configuration for email notifications."""

    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender_email: str = ""
    sender_password: str = ""
    recipient_email: str = ""


PARTITIONS_DEF = StaticPartitionsDefinition(
    partition_keys=[
        "MSFT",
        "AAPL",
        "GOOGL",
        "TSLA",
        "AMZN",
        "FB",
        "NFLX",
        "NVDA",
        "AMD",
    ]
)


@static_partitioned_config(partition_keys=PARTITIONS_DEF.get_partition_keys())
def partitioned_config(partition_key: str) -> Config:
    """Partitioned configuration for the data pipeline."""

    return Config(
        stock_config=StockConfig(
            ticker=partition_key, api_key=os.getenv("ALPHA_VANTAGE_API_KEY", "")
        ),
        email_config=EmailConfig(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            sender_email="",  # Insert sender email
            sender_password="",  # Insert sender email password
            recipient_email="",  # Insert recipient email
        ),
    )


PARTITIONED_CONFIG = PartitionedConfig(partitions_def=PARTITIONS_DEF, run_config_for_partition_key_fn=partitioned_config)

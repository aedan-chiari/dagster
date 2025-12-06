from dagster import Config
from dagster import (
    PartitionedConfig,
    StaticPartitionsDefinition,
    static_partitioned_config,
    EnvVar
)
import os
import yaml
from pathlib import Path


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


def load_config():
    """Load configuration from YAML file."""
    config_path = Path(__file__).parent / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found at {config_path}. "
            "Please create config.yaml from config_example.yaml"
        )

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


# Load config and create partitions from stock tickers
_config = load_config()
PARTITIONS_DEF = StaticPartitionsDefinition(
    partition_keys=_config.get('stock_tickers', [])
)


@static_partitioned_config(partition_keys=PARTITIONS_DEF.get_partition_keys())
def partitioned_config(partition_key: str):
    """Partitioned configuration for the data pipeline."""

    # Load email config from YAML, with environment variable fallbacks
    email_config = _config.get('email', {})

    return {
        "ops": {
            "stock_prices": {
                "config": {
                    "ticker": partition_key,
                }
            },
            "price_changes": {
                "config": {
                    "ticker": partition_key,
                }
            },
            "send_stock_email": {
                "config": {
                    "smtp_server": email_config.get("smtp_server", "smtp.gmail.com"),
                    "smtp_port": email_config.get("smtp_port", 587),
                    "sender_email": email_config.get("sender_email") or os.getenv("SENDER_EMAIL", ""),
                    "sender_password": email_config.get("sender_password") or os.getenv("SENDER_PASSWORD", ""),
                    "recipient_email": email_config.get("recipient_email") or os.getenv("RECIPIENT_EMAIL", ""),
                }
            }
        }
    }


PARTITIONED_CONFIG = PartitionedConfig(partitions_def=PARTITIONS_DEF, run_config_for_partition_key_fn=partitioned_config)

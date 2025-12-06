"""
Dagster pipeline for fetching stock prices and sending email notifications.
"""

from datetime import datetime
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import polars as pl

from code_server.data_pipeline.data_pipeline_config import (
    PARTITIONS_DEF,
    EmailConfig,
    StockConfig,
)
from code_server.data_pipeline.data_pipeline_helpers import format_email_body
from dagster import (
    asset,
    AssetExecutionContext,
)

@asset(
    partitions_def=PARTITIONS_DEF,
    io_manager_key="polars_parquet_io_manager"
)
def stock_prices(
    context: AssetExecutionContext, config: StockConfig
) -> pl.DataFrame:
    """
    Fetch open and close prices for a single stock using Alpha Vantage API.

    Returns:
        Polars DataFrame with open/close prices and date for the ticker
    """
    # If no API key provided, raise error
    if not config.api_key:
        msg = "No API key provided. Please ensure ALPHA_VANTAGE_API_KEY is set in environment variables."
        context.log.warning(msg)
        raise ValueError(msg)

    if config.api_key == "ALPHA_VANTAGE_API_KEY":
        msg = "API key is set to placeholder value. Please set ALPHA_VANTAGE_API_KEY in environment variables."
        context.log.warning(msg)
        raise ValueError(msg)

    # Fetch real data from Alpha Vantage
    base_url = "https://www.alphavantage.co/query"

    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": config.ticker,
        "apikey": config.api_key,
    }

    response = requests.get(base_url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if "Time Series (Daily)" in data:
        latest_date = list(data["Time Series (Daily)"].keys())[0]
        latest_data = data["Time Series (Daily)"][latest_date]

        stock_data = {
            "open": float(latest_data["1. open"]),
            "close": float(latest_data["4. close"]),
            "date": latest_date,
        }

        context.log.info(
            f"Fetched data for {config.ticker}: Open=${stock_data['open']}, Close=${stock_data['close']}"
        )

        return pl.DataFrame([stock_data])
    else:
        error_msg = data.get('Note', data.get('Error Message', 'Unknown error'))
        context.log.error(f"Error fetching data for {config.ticker}: {error_msg}")
        raise ValueError(f"Failed to fetch data for {config.ticker}: {error_msg}")


@asset(
    partitions_def=PARTITIONS_DEF,
    io_manager_key="polars_parquet_io_manager"
)
def price_changes(
    context: AssetExecutionContext,
    stock_prices: pl.DataFrame,
    config: StockConfig
) -> pl.DataFrame:
    """
    Calculate price changes and percentage changes for the stock.

    Args:
        stock_prices: Stock price data from stock_prices asset
        config: Stock configuration to get ticker symbol

    Returns:
        Polars DataFrame with price changes and percentages
    """
    # Use Polars operations to calculate changes
    df = stock_prices.with_columns([
        pl.lit(config.ticker).alias("ticker"),
        (pl.col("close") - pl.col("open")).round(2).alias("change"),
        ((pl.col("close") - pl.col("open")) / pl.col("open") * 100).round(2).alias("change_percent"),
    ])

    # Log the results
    open_price = df["open"][0]
    close_price = df["close"][0]
    change = df["change"][0]
    change_percent = df["change_percent"][0]

    context.log.info(
        f"{config.ticker}: ${open_price} -> ${close_price} "
        f"(Change: ${change:.2f}, {change_percent:.2f}%)"
    )

    return df


@asset
def send_stock_email(
    context: AssetExecutionContext,
    price_changes: dict[str, pl.DataFrame],
    config: EmailConfig,
) -> str:
    """
    Send email notification with stock price updates for all stocks.

    Args:
        price_changes: Price change data from all partitions of price_changes asset (dict of DataFrames)
        config: Email configuration

    Returns:
        Status message
    """
    # Convert Polars DataFrames to dict format expected by format_email_body
    price_changes_dict = {}
    for partition_key, df in price_changes.items():
        # Convert the DataFrame row to a dictionary
        row_dict = df.to_dicts()[0]
        price_changes_dict[partition_key] = row_dict

    if not all([config.sender_email, config.sender_password, config.recipient_email]):
        context.log.warning("Email credentials not configured. Skipping email send.")
        context.log.info("Would have sent email with the following content:")
        context.log.info(format_email_body(price_changes_dict))
        return "Email skipped - no credentials configured"

    try:
        # Create email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Stock Price Update - {datetime.now().strftime('%Y-%m-%d')}"
        msg["From"] = config.sender_email
        msg["To"] = config.recipient_email

        # Create email body
        body = format_email_body(price_changes_dict)
        msg.attach(MIMEText(body, "html"))

        # Send email
        with smtplib.SMTP(config.smtp_server, config.smtp_port) as server:
            server.starttls()
            server.login(config.sender_email, config.sender_password)
            server.send_message(msg)

        context.log.info(f"Email sent successfully to {config.recipient_email}")
        return "Email sent successfully"

    except Exception as e:
        context.log.error(f"Failed to send email: {str(e)}")
        raise

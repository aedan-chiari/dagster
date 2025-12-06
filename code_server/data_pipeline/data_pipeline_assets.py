"""
Dagster pipeline for fetching stock prices and sending email notifications.
"""

from datetime import datetime
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

@asset(partitions_def=PARTITIONS_DEF)
def stock_prices(
    context: AssetExecutionContext, config: StockConfig
) -> dict[str, float]:
    """
    Fetch open and close prices for a single stock using Alpha Vantage API.

    Returns:
        Dictionary with open/close prices and date for the ticker
    """
    # If no API key provided, raise error
    if not config.api_key:
        msg = "No API key provided. Please ensure ALPHA_VANTAGE_API_KEY is set in environment variables."
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

        return stock_data
    else:
        error_msg = data.get('Note', data.get('Error Message', 'Unknown error'))
        context.log.error(f"Error fetching data for {config.ticker}: {error_msg}")
        raise ValueError(f"Failed to fetch data for {config.ticker}: {error_msg}")


@asset(partitions_def=PARTITIONS_DEF)
def price_changes(
    context: AssetExecutionContext,
    stock_prices: dict[str, float],
    config: StockConfig
):
    """
    Calculate price changes and percentage changes for the stock.

    Args:
        fetch_stock_prices: Stock price data from fetch_stock_prices asset
        config: Stock configuration to get ticker symbol

    Returns:
        Dictionary with price changes and percentages
    """
    open_price = stock_prices["open"]
    close_price = stock_prices["close"]
    change = close_price - open_price
    change_percent = (change / open_price) * 100 if open_price != 0 else 0

    price_changes = {
        "ticker": config.ticker,
        "open": open_price,
        "close": close_price,
        "change": round(change, 2),
        "change_percent": round(change_percent, 2),
        "date": stock_prices["date"],
    }

    context.log.info(
        f"{config.ticker}: ${open_price} -> ${close_price} "
        f"(Change: ${change:.2f}, {change_percent:.2f}%)"
    )

    return price_changes


@asset
def send_stock_email(
    context: AssetExecutionContext,
    price_changes: dict,
    config: EmailConfig,
) -> str:
    """
    Send email notification with stock price updates for all stocks.

    Args:
        price_changes: Price change data from all partitions of price_changes asset
        config: Email configuration

    Returns:
        Status message
    """
    if not all([config.sender_email, config.sender_password, config.recipient_email]):
        context.log.warning("Email credentials not configured. Skipping email send.")
        context.log.info("Would have sent email with the following content:")
        context.log.info(format_email_body(price_changes))
        return "Email skipped - no credentials configured"

    try:
        # Create email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Stock Price Update - {datetime.now().strftime('%Y-%m-%d')}"
        msg["From"] = config.sender_email
        msg["To"] = config.recipient_email

        # Create email body
        body = format_email_body(price_changes)
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

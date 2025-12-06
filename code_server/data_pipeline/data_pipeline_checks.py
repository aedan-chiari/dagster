"""
Asset checks for the stock price pipeline.

These checks validate data quality and business logic constraints.
"""

from dagster import (
    AssetCheckResult,
    AssetCheckSeverity,
    asset_check,
)
import polars as pl


@asset_check(asset="stock_prices")
def check_stock_prices_not_null(stock_prices: pl.DataFrame) -> AssetCheckResult:
    """Ensure that stock price data has no null values."""
    null_count = stock_prices.null_count().sum_horizontal()[0]

    return AssetCheckResult(
        passed=null_count == 0,
        metadata={
            "null_count": null_count,
            "row_count": len(stock_prices),
        },
    )


@asset_check(asset="stock_prices")
def check_stock_prices_positive(stock_prices: pl.DataFrame) -> AssetCheckResult:
    """Verify that all stock prices are positive numbers."""
    invalid_open = (stock_prices["open"] <= 0).sum()
    invalid_close = (stock_prices["close"] <= 0).sum()
    total_invalid = invalid_open + invalid_close

    return AssetCheckResult(
        passed=total_invalid == 0,
        metadata={
            "invalid_count": total_invalid,
            "min_open": stock_prices["open"].min(),
            "min_close": stock_prices["close"].min(),
        },
    )


@asset_check(asset="price_changes")
def check_price_change_calculation(price_changes: pl.DataFrame) -> AssetCheckResult:
    """Validate that price change calculations are mathematically correct."""
    # Calculate expected change
    expected_change = (price_changes["close"] - price_changes["open"]).round(2)
    actual_change = price_changes["change"]

    # Check if they match (allowing for tiny floating point differences)
    matches = (expected_change - actual_change).abs() < 0.01
    incorrect_calculations = (~matches).sum()

    return AssetCheckResult(
        passed=incorrect_calculations == 0,
        metadata={
            "incorrect_calculations": incorrect_calculations,
            "total_rows": len(price_changes),
        },
    )


@asset_check(asset="price_changes")
def check_extreme_price_changes(price_changes: pl.DataFrame) -> AssetCheckResult:
    """
    Flag extreme price changes that might indicate data quality issues.

    Warning-level check since extreme movements can be legitimate.
    """
    EXTREME_THRESHOLD = 50.0  # 50% change

    extreme_changes = (price_changes["change_percent"].abs() > EXTREME_THRESHOLD).sum()

    metadata = {
        "extreme_change_count": extreme_changes,
        "threshold_percent": EXTREME_THRESHOLD,
        "max_change_percent": price_changes["change_percent"].abs().max(),
    }

    if extreme_changes > 0:
        extreme_row = price_changes.filter(
            pl.col("change_percent").abs() > EXTREME_THRESHOLD
        )
        if len(extreme_row) > 0:
            metadata["extreme_ticker"] = extreme_row["ticker"][0]
            metadata["extreme_change_value"] = extreme_row["change_percent"][0]

    return AssetCheckResult(
        passed=extreme_changes == 0,
        severity=AssetCheckSeverity.WARN,
        metadata=metadata,
    )

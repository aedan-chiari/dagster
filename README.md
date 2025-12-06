# Stock Price Email Pipeline

A demonstration Dagster pipeline that showcases data orchestration patterns and best practices.

> **Note**: This is a learning/portfolio project designed to demonstrate Dagster capabilities, not a production trading tool. It fetches stock prices and sends email notifications to illustrate real-world data pipeline patterns.

## Features

- 📊 Fetches open and close prices for multiple stocks
- 📧 Sends formatted HTML email with price changes
- ⏰ Scheduled to run daily after market close (5 PM weekdays)
- 📈 Calculates price changes and percentage changes
- 🎨 Color-coded email (green for gains, red for losses)

## Setup

### 1. Install Dependencies

```bash
pip install -e .
```

### 2. Get API Key

Sign up for a free Alpha Vantage API key:
- Visit: https://www.alphavantage.co/support/#api-key
- Note: Free tier allows 25 requests/day

### 3. Configure Email (for Gmail)

If using Gmail, you need to create an App Password:
1. Go to your Google Account settings
2. Enable 2-factor authentication
3. Generate an App Password: https://support.google.com/accounts/answer/185833
4. Use this App Password (not your regular password)

### 4. Create Configuration

Copy the example config and fill in your details:

```bash
cp config_example.yaml config.yaml
```

Edit `config.yaml` with your:
- Stock symbols to track
- Alpha Vantage API key
- Email credentials

## Running the Pipeline

### Launch Dagster UI

There are two ways to launch Dagster:

#### Option 1: Using dagster dev (Recommended for Development)

From the project root directory:

```bash
dagster dev
```

This command:
- Automatically discovers the `Definitions` object in [code_server/definitions.py](code_server/definitions.py)
- Starts the Dagster web server
- Opens the UI at http://localhost:3000
- Enables hot-reloading for code changes

#### Option 2: Using dagster-webserver (Production-like)

```bash
dagster-webserver -m code_server.definitions
```

This approach is more similar to production deployments.

### Materialize Assets

Once the UI is running at http://localhost:3000:

1. Navigate to **Assets** in the left sidebar
2. You'll see three assets: `stock_prices`, `price_changes`, and `send_stock_email`
3. Click **Materialize all** to run the entire pipeline
4. Alternatively, select specific assets and click **Materialize selected**

The pipeline will use configuration from [code_server/config_example.yaml](code_server/config_example.yaml) and environment variables.

### Testing Without API Key or Email

The pipeline gracefully handles missing credentials:
- **No API key**: Uses mock stock data for testing
- **No email credentials**: Logs email content to console instead of sending

## Pipeline Architecture

The pipeline consists of three assets:

1. **stock_prices**: Fetches data from Alpha Vantage API
2. **price_changes**: Calculates price changes and percentages
3. **send_stock_email**: Formats and sends HTML email

### Data Quality Checks

The pipeline includes asset checks to ensure data quality:

- **check_stock_prices_not_null**: Validates no null values in price data
- **check_stock_prices_positive**: Ensures all prices are positive numbers
- **check_price_change_calculation**: Verifies mathematical accuracy of calculations
- **check_extreme_price_changes**: Flags unusual price movements (>50% change)

Asset checks run automatically when assets are materialized and can be viewed in the Dagster UI under the "Checks" tab.

## Schedule

The pipeline is configured to run automatically:
- **Time**: 5:00 PM (17:00)
- **Days**: Monday-Friday (weekdays only)
- **Cron**: `0 17 * * 1-5`

To enable the schedule:
1. Go to "Automation" in Dagster UI
2. Find "daily_stock_price_update"
3. Toggle it ON

## Customization

### Add More Stocks

Edit the `stock_symbols` list in your config:

```yaml
stock_symbols:
  - "AAPL"
  - "NVDA"
  - "META"
  # Add more symbols here
```

### Change Schedule

Modify the cron schedule in [code_server/data_pipeline/schedules/data_pipeline_schedule.py](code_server/data_pipeline/schedules/data_pipeline_schedule.py#L6):

```python
cron_schedule="0 17 * * 1-5",  # Format: minute hour day month weekday
```

### Email Format

Customize the HTML email formatting in the `send_stock_email` asset function in [code_server/data_pipeline/data_pipeline_assets.py](code_server/data_pipeline/data_pipeline_assets.py).

## Troubleshooting

**Import errors**: Run `pip install -e .` from the project root

**API rate limit**: Alpha Vantage free tier allows 25 requests/day. Reduce stock count or upgrade.

**Email not sending**:
- Verify SMTP settings for your provider
- For Gmail, ensure you're using an App Password
- Check firewall/antivirus isn't blocking port 587

**Schedule not running**: Make sure to enable the schedule in the Dagster UI under "Automation"

**Asset check errors (FileNotFoundError)**:
- Asset checks require the corresponding assets to be materialized first
- If you see errors about missing `.parquet` files, materialize the assets for those partitions before running checks
- In the UI, select specific partitions to materialize rather than trying to run all partitions at once
- Asset checks will only run successfully on partitions that have been materialized

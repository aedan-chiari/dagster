# Stock Price Email Pipeline

A Dagster pipeline that fetches stock prices and sends email notifications with daily price updates.

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

### Run Dagster UI

```bash
cd /Users/aedanchiari/Downloads/Repos/dagster/code_server/data_pipeline
dagster dev -f main.py
```

Then open http://localhost:3000 in your browser.

### Materialize Assets

In the Dagster UI:
1. Go to "Assets"
2. Select all three assets (or click "Materialize all")
3. Click "Launchpad" to configure settings
4. Paste your config.yaml content
5. Click "Launch Run"

### Testing Without API Key or Email

The pipeline works without credentials for testing:
- **No API key**: Uses mock data
- **No email credentials**: Logs email content instead of sending

## Pipeline Architecture

The pipeline consists of three assets:

1. **fetch_stock_prices**: Fetches data from Alpha Vantage API
2. **calculate_price_changes**: Calculates price changes and percentages
3. **send_stock_email**: Formats and sends HTML email

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

Modify the cron schedule in [main.py:205](main.py#L205):

```python
cron_schedule="0 17 * * 1-5",  # Format: minute hour day month weekday
```

### Email Format

Customize the HTML email in the `format_email_body()` function at [main.py:158](main.py#L158).

## Troubleshooting

**Import errors**: Run `pip install -e .` from the project root

**API rate limit**: Alpha Vantage free tier allows 25 requests/day. Reduce stock count or upgrade.

**Email not sending**:
- Verify SMTP settings for your provider
- For Gmail, ensure you're using an App Password
- Check firewall/antivirus isn't blocking port 587

**Schedule not running**: Make sure to enable the schedule in the Dagster UI under "Automation"

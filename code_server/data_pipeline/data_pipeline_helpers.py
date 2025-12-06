from datetime import datetime
from typing import Dict
from zoneinfo import ZoneInfo

def format_email_body(price_changes: Dict[str, Dict[str, str | float]]) -> str:
    """Format the email body with stock price information for all stocks."""
    tz = ZoneInfo("America/Denver")

    html = """
    <html>
      <head>
        <style>
          body {{ font-family: Arial, sans-serif; }}
          table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
          th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
          th {{ background-color: #4CAF50; color: white; }}
          .positive {{ color: green; font-weight: bold; }}
          .negative {{ color: red; font-weight: bold; }}
          .neutral {{ color: gray; }}
        </style>
      </head>
      <body>
        <h2>Daily Stock Price Update</h2>
        <p>Date: {date}</p>
        <table>
          <tr>
            <th>Symbol</th>
            <th>Open</th>
            <th>Close</th>
            <th>Change ($)</th>
            <th>Change (%)</th>
          </tr>
    """.format(date=datetime.now(tz).strftime("%Y-%m-%d"))

    # Sort by partition key (ticker symbol)
    for _, data in sorted(price_changes.items()):
        change = float(data["change"])
        change_percent = float(data["change_percent"])

        change_class = (
            "positive"
            if change > 0
            else "negative"
            if change < 0
            else "neutral"
        )
        change_symbol = (
            "↑" if change > 0 else "↓" if change < 0 else "→"
        )

        html += """
          <tr>
            <td><strong>{ticker}</strong></td>
            <td>${open_price:.2f}</td>
            <td>${close_price:.2f}</td>
            <td class="{change_class}">{change_symbol} ${abs_change:.2f}</td>
            <td class="{change_class}">{change_symbol} {abs_change_percent:.2f}%</td>
          </tr>
        """.format(
            ticker=data["ticker"],
            open_price=float(data["open"]),
            close_price=float(data["close"]),
            change_class=change_class,
            change_symbol=change_symbol,
            abs_change=abs(change),
            abs_change_percent=abs(change_percent)
        )

    html += """
        </table>
        <p style="color: #666; font-size: 12px;">
          This is an automated message from your Dagster stock price pipeline.
        </p>
      </body>
    </html>
    """

    return html

import csv
import io
import requests

BASE_URL = "https://stooq.com/q/d/l/"
SYMBOL = "IBM"


def to_stooq_symbol(symbol: str) -> str:
    cleaned = symbol.strip().lower()
    return cleaned if "." in cleaned else f"{cleaned}.us"


params = {
    "s": to_stooq_symbol(SYMBOL),
    "i": "d",
}

try:
    resp = requests.get(BASE_URL, params=params, timeout=20)
    print("Status code:", resp.status_code)
    resp.raise_for_status()
    reader = csv.DictReader(io.StringIO(resp.text))
    rows = [r for r in reader if r.get("Date") and r["Date"] != "null"]
    if not rows:
        raise RuntimeError("No rows returned.")
except Exception as exc:
    print(f"Data fetch failed, using sample rows. Reason: {exc}")
    rows = [
        {"Date": "2024-01-05", "Open": "184.3", "High": "186.9", "Low": "183.8", "Close": "186.2", "Volume": "43210000"},
        {"Date": "2024-01-04", "Open": "182.7", "High": "185.4", "Low": "182.2", "Close": "184.9", "Volume": "38950000"},
        {"Date": "2024-01-03", "Open": "181.2", "High": "183.6", "Low": "180.4", "Close": "182.5", "Volume": "40120000"},
    ]

rows = sorted(rows, key=lambda r: r["Date"], reverse=True)

print(f"Symbol: {SYMBOL}")
print(f"Rows returned: {len(rows)}")
print("First 12 rows (date, open, high, low, close, volume):")
for row in rows[:12]:
    print(row["Date"], row["Open"], row["High"], row["Low"], row["Close"], row["Volume"])

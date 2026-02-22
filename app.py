import os
import csv
import io
from typing import Tuple

import pandas as pd
import requests
import streamlit as st


def fetch_daily_timeseries(
    symbol: str, outputsize: str, rows_to_show: int
) -> Tuple[int, int, pd.DataFrame]:
    """Fetch Stooq daily time-series data and return parsed rows."""
    del outputsize  # kept for UI compatibility

    base_url = "https://stooq.com/q/d/l/"
    symbol_fmt = symbol.strip().lower()
    if "." not in symbol_fmt:
        symbol_fmt = f"{symbol_fmt}.us"
    params = {
        "s": symbol_fmt,
        "i": "d",
    }

    response = requests.get(base_url, params=params, timeout=20)
    status_code = response.status_code
    response.raise_for_status()

    reader = csv.DictReader(io.StringIO(response.text))
    rows = []
    for row in reader:
        if not row.get("Date") or row["Date"] == "null":
            continue
        rows.append(
            {
                "date": row["Date"],
                "open": row["Open"],
                "high": row["High"],
                "low": row["Low"],
                "close": row["Close"],
                "volume": row["Volume"],
            }
        )
    if not rows:
        raise ValueError("No data returned. Check symbol (example: IBM, AAPL, MSFT).")

    df = pd.DataFrame(rows)
    df = df.sort_values("date", ascending=False)
    df = df.head(rows_to_show).reset_index(drop=True)

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return status_code, len(dates), df


def main() -> None:
    st.set_page_config(page_title="Market Data Query", layout="wide")
    st.title("Market Data Query (Stooq Daily)")
    st.caption("Run a daily time-series query (no API key required) and preview rows.")

    with st.container():
        col1, col2, col3 = st.columns(3)
        symbol = col1.text_input("Stock symbol", value="IBM")
        outputsize = col2.selectbox("Output size", ["compact", "full"], index=0)
        rows_to_show = col3.number_input(
            "Rows to show", min_value=1, max_value=200, value=12, step=1
        )

        run = st.button("Run Query", type="primary")

    st.divider()

    if run:
        try:
            # Ensure outputsize is a string and not None for type safety
            outputsize_str = str(outputsize) if outputsize is not None else "compact"
            status_code, total_rows, df = fetch_daily_timeseries(
                symbol=symbol.strip().upper(),
                outputsize=outputsize_str,
                rows_to_show=int(rows_to_show),
            )
            st.success("Query completed.")
            kpi_col1, kpi_col2 = st.columns(2)
            kpi_col1.metric("Status code", status_code)
            kpi_col2.metric("Rows returned", total_rows)
            st.dataframe(df, use_container_width=True)
        except ValueError as exc:
            st.error(str(exc))
        except requests.RequestException as exc:
            st.error(f"Unexpected error: {exc}")


if __name__ == "__main__":
    main()

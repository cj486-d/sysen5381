#!/usr/bin/env python3
import argparse
import csv
import io
import json
import os
from datetime import datetime
from pathlib import Path
from statistics import mean, pstdev

import requests


STOOQ_URL = "https://stooq.com/q/d/l/"


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def ascii_only(text: str) -> str:
    return text.encode("ascii", "ignore").decode("ascii")


def to_stooq_symbol(symbol: str) -> str:
    cleaned = symbol.strip().lower()
    return cleaned if "." in cleaned else f"{cleaned}.us"


def fetch_stooq_rows(symbol: str, max_rows: int) -> list[dict]:
    params = {
        "s": to_stooq_symbol(symbol),
        "i": "d",
    }
    response = requests.get(STOOQ_URL, params=params, timeout=20)
    response.raise_for_status()
    reader = csv.DictReader(io.StringIO(response.text))
    rows = []
    for row in reader:
        if not row.get("Date") or row["Date"] == "null":
            continue
        rows.append(
            {
                "date": row["Date"],
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(float(row["Volume"])),
            }
        )
    rows = sorted(rows, key=lambda r: r["date"], reverse=True)
    if not rows:
        raise RuntimeError("No rows returned from Stooq.")
    return rows[:max_rows]


def sample_rows() -> list[dict]:
    return [
        {"date": "2024-01-05", "open": 184.3, "high": 186.9, "low": 183.8, "close": 186.2, "volume": 43210000},
        {"date": "2024-01-04", "open": 182.7, "high": 185.4, "low": 182.2, "close": 184.9, "volume": 38950000},
        {"date": "2024-01-03", "open": 181.2, "high": 183.6, "low": 180.4, "close": 182.5, "volume": 40120000},
        {"date": "2024-01-02", "open": 179.9, "high": 181.7, "low": 179.1, "close": 180.8, "volume": 37690000},
        {"date": "2023-12-29", "open": 178.8, "high": 180.5, "low": 178.1, "close": 179.6, "volume": 35840000},
        {"date": "2023-12-28", "open": 177.4, "high": 179.2, "low": 176.9, "close": 178.5, "volume": 34430000},
        {"date": "2023-12-27", "open": 176.1, "high": 178.3, "low": 175.6, "close": 177.8, "volume": 33280000},
        {"date": "2023-12-26", "open": 174.5, "high": 176.8, "low": 174.1, "close": 175.9, "volume": 32010000},
        {"date": "2023-12-22", "open": 173.2, "high": 175.1, "low": 172.6, "close": 174.7, "volume": 31100000},
        {"date": "2023-12-21", "open": 172.4, "high": 174.2, "low": 171.9, "close": 173.6, "volume": 30540000},
    ]


def compute_metrics(rows: list[dict]) -> dict:
    closes = [r["close"] for r in rows]
    opens = [r["open"] for r in rows]
    volumes = [r["volume"] for r in rows]
    daily_returns = [(c - o) / o for c, o in zip(closes, opens)]

    trend = (closes[0] - closes[-1]) / closes[-1] if closes[-1] else 0.0
    metrics = {
        "avg_close": mean(closes),
        "min_close": min(closes),
        "max_close": max(closes),
        "avg_volume": mean(volumes),
        "return_volatility": pstdev(daily_returns) if len(daily_returns) > 1 else 0.0,
        "trend_pct": trend,
        "latest_close": closes[0],
        "oldest_close": closes[-1],
    }
    return metrics


def build_report_data(symbol: str, rows: list[dict], source: str) -> dict:
    metrics = compute_metrics(rows)
    recent = rows[:7]
    for r in recent:
        r["daily_return_pct"] = (r["close"] - r["open"]) / r["open"]
    return {
        "symbol": symbol,
        "as_of": rows[0]["date"],
        "window_days": len(rows),
        "data_source": source,
        "summary_stats": metrics,
        "recent_rows": recent,
    }


def prompt_versions(report_data: dict) -> list[str]:
    data_json = json.dumps(report_data, ensure_ascii=True, indent=2)
    return [
        (
            "You are a financial analyst. Using the data below, write a short report "
            "with a title, one short paragraph, and 3 bullet points.\n\n"
            f"DATA (JSON):\n{data_json}\n"
        ),
        (
            "Using the data below, write a report with:\n"
            "1) A title line\n"
            "2) A summary in 2-3 sentences\n"
            "3) Exactly 3 bullet points of insights\n"
            "Avoid speculation, use numbers where possible, and keep it concise.\n\n"
            f"DATA (JSON):\n{data_json}\n"
        ),
        (
            "Write a report in this exact format:\n"
            "Title: <one line>\n"
            "Summary: <2 sentences>\n"
            "Insights:\n"
            "- <bullet 1>\n"
            "- <bullet 2>\n"
            "- <bullet 3>\n"
            "Recommendation: <1 sentence>\n"
            "Caveat: <1 sentence about data limits>\n"
            "Use ASCII only and avoid extra sections.\n\n"
            f"DATA (JSON):\n{data_json}\n"
        ),
    ]


def extract_ollama_text(response_json: dict) -> str:
    if "response" in response_json and isinstance(response_json["response"], str):
        return response_json["response"].strip()
    if "message" in response_json and isinstance(response_json["message"], dict):
        content = response_json["message"].get("content", "")
        if isinstance(content, str):
            return content.strip()
    return ""


def call_ollama(prompt: str, model: str, base_url: str, api_key: str = "") -> str:
    url = base_url.rstrip("/") + "/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    response = requests.post(url, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    text = extract_ollama_text(response.json())
    if not text:
        raise RuntimeError("Ollama response did not contain generated text.")
    return text


def local_fallback_report(report_data: dict) -> str:
    stats = report_data.get("summary_stats", {})
    symbol = report_data.get("symbol", "UNKNOWN")
    as_of = report_data.get("as_of", "N/A")
    avg_close = float(stats.get("avg_close", 0.0))
    min_close = float(stats.get("min_close", 0.0))
    max_close = float(stats.get("max_close", 0.0))
    trend_pct = float(stats.get("trend_pct", 0.0)) * 100.0
    latest_close = float(stats.get("latest_close", 0.0))

    return (
        f"Title: {symbol} Stock Snapshot (Fallback)\n\n"
        f"Summary: As of {as_of}, the latest close is {latest_close:.2f}. "
        f"Average close in this window is {avg_close:.2f}, with a trend of {trend_pct:.2f}%.\n\n"
        "Insights:\n"
        f"- Close range observed: {min_close:.2f} to {max_close:.2f}.\n"
        f"- Average close across the selected window: {avg_close:.2f}.\n"
        f"- Direction over the window: {trend_pct:.2f}%.\n\n"
        "Recommendation: Use this as a quick snapshot and validate with live market context.\n\n"
        "Caveat: This report was generated from local logic because online AI call was unavailable.\n"
    )


def save_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Final project data pipeline and AI report.")
    parser.add_argument("--symbol", default="IBM", help="Stock symbol.")
    parser.add_argument("--function", default="TIME_SERIES_DAILY", help="Kept for compatibility; not used.")
    parser.add_argument("--outputsize", default="compact", help="Kept for compatibility; not used.")
    parser.add_argument("--window", type=int, default=30, help="Number of recent rows to use.")
    parser.add_argument("--iterations", type=int, default=3, help="Number of prompt iterations.")
    args = parser.parse_args()

    env_path = Path(__file__).resolve().parent / ".env"
    load_env_file(env_path)
    ollama_model = os.environ.get("OLLAMA_MODEL", "llama3.1:latest").strip() or "llama3.1:latest"
    ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip() or "http://127.0.0.1:11434"
    ollama_api_key = os.environ.get("OLLAMA_API_KEY", "").strip()

    rows = []
    source = "stooq"
    try:
        rows = fetch_stooq_rows(args.symbol, args.window)
    except Exception as exc:
        print(f"Data fetch failed, using sample data. Reason: {exc}")
        rows = sample_rows()
        source = "sample"

    report_data = build_report_data(args.symbol, rows, source)
    data_path = Path(__file__).resolve().parent / "processed_data.json"
    save_text(data_path, json.dumps(report_data, ensure_ascii=True, indent=2))

    prompts = prompt_versions(report_data)
    outputs = []
    for i, prompt in enumerate(prompts[: args.iterations], start=1):
        try:
            text = call_ollama(prompt=prompt, model=ollama_model, base_url=ollama_base_url, api_key=ollama_api_key)
        except (requests.RequestException, RuntimeError) as exc:
            print(f"Ollama call failed on iteration {i}, using local fallback. Reason: {exc}")
            text = local_fallback_report(report_data)
        text = ascii_only(text)
        outputs.append(text)
        out_path = Path(__file__).resolve().parent / f"report_iter_{i}.md"
        save_text(out_path, text)

    final_text = outputs[-1] if outputs else ""
    final_path = Path(__file__).resolve().parent / "final_report.md"
    save_text(final_path, final_text)

    print(f"Saved processed data: {data_path}")
    print(f"Saved final report: {final_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

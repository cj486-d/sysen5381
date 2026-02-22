#!/usr/bin/env python3
import argparse
import json
import os
from html import escape
from pathlib import Path

import requests


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


def extract_ollama_text(response_json: dict) -> str:
    if "response" in response_json and isinstance(response_json["response"], str):
        return response_json["response"].strip()
    if "message" in response_json and isinstance(response_json["message"], dict):
        content = response_json["message"].get("content", "")
        if isinstance(content, str):
            return content.strip()
    return ""


def generate_report(base_url: str, model: str, api_key: str) -> str:
    if not base_url:
        return (
            "Productivity Report\n"
            "===================\n"
            "\n"
            "Summary:\n"
            "- Use a daily plan with 3 priorities.\n"
            "- Batch similar tasks to reduce context switching.\n"
            "- Review progress at the end of each day.\n"
            "\n"
            "Conclusion:\n"
            "Small, consistent habits create reliable progress.\n"
        )

    url = base_url.rstrip("/") + "/api/generate"
    payload = {
        "model": model,
        "prompt": (
            "Write a short productivity report for students. "
            "Include a title, a short summary paragraph, "
            "3 bullet points, and a one-sentence conclusion. "
            "Use ASCII characters only."
        ),
        "stream": False,
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
    except requests.RequestException:
        return (
            "Productivity Report\n"
            "===================\n"
            "\n"
            "Summary:\n"
            "- Keep tasks small and measurable.\n"
            "- Work in focused blocks with short breaks.\n"
            "- Track results to improve tomorrow.\n"
            "\n"
            "Conclusion:\n"
            "Clarity and consistency beat intensity.\n"
        )
    if not response.ok:
        return (
            "Productivity Report\n"
            "===================\n"
            "\n"
            "Summary:\n"
            "- Keep tasks small and measurable.\n"
            "- Work in focused blocks with short breaks.\n"
            "- Track results to improve tomorrow.\n"
            "\n"
            "Conclusion:\n"
            "Clarity and consistency beat intensity.\n"
        )

    data = response.json()
    text = extract_ollama_text(data)
    return text or (
        "Productivity Report\n"
        "===================\n"
        "\n"
        "Summary:\n"
        "- Write a simple plan before you start.\n"
        "- Protect focus time from interruptions.\n"
        "- Close the day with a quick review.\n"
        "\n"
        "Conclusion:\n"
        "Small steps compound into big gains.\n"
    )


def write_report(content: str, output_format: str) -> Path:
    output_path = Path(__file__).resolve().parent / f"report.{output_format}"
    if output_format == "html":
        html_content = (
            "<!doctype html>\n"
            "<html>\n"
            "<head><meta charset=\"utf-8\"><title>Report</title></head>\n"
            "<body>\n"
            "<pre>\n"
            f"{escape(content)}\n"
            "</pre>\n"
            "</body>\n"
            "</html>\n"
        )
        output_path.write_text(html_content, encoding="utf-8")
    else:
        output_path.write_text(content, encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a simple report file.")
    parser.add_argument(
        "--format",
        choices=["txt", "md", "html"],
        default="md",
        help="Output file format.",
    )
    args = parser.parse_args()

    env_path = Path(__file__).resolve().parent / ".env"
    load_env_file(env_path)
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip()
    model = os.environ.get("OLLAMA_MODEL", "llama3.1:latest").strip()
    api_key = os.environ.get("OLLAMA_API_KEY", "").strip()

    report_text = generate_report(base_url, model, api_key)
    report_text = ascii_only(report_text)

    output_path = write_report(report_text, args.format)
    print(f"Saved report: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

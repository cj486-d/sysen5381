# LAB: AI Reporter

## Main Script
- File: `06_final_project.py`
- Goal: Generate an AI-powered stock summary report

## Pipeline
1. Fetch daily rows from Stooq
2. Compute summary metrics
3. Build structured JSON (`processed_data.json`)
4. Send prompt to Ollama (`/api/generate`)
5. Save report outputs (`report_iter_*.md`, `final_report.md`)

## Run
```bash
python3 06_final_project.py --symbol IBM --window 30 --iterations 3
```

## Model Configuration
- `OLLAMA_MODEL` (default: `llama3.1:latest`)
- `OLLAMA_BASE_URL` (default: `http://127.0.0.1:11434`)
- `OLLAMA_API_KEY` (optional, only if endpoint requires auth)

## Reliability Design
- If Stooq fails: switch to sample market rows
- If Ollama fails: switch to local fallback report text
- Result: script still finishes and saves report files

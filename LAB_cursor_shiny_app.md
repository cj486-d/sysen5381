# LAB: Cursor Shiny App

## App File
- File: `02_productivity/shiny_app/app.py`
- Framework: Streamlit

## What It Does
- Accepts stock symbol input (example: `IBM`)
- Requests daily market data from Stooq
- Displays status code, row count, and preview table

## Run
```bash
cd 02_productivity/shiny_app
streamlit run app.py
```

## Input Controls
- `Stock symbol`
- `Output size` (kept for compatibility)
- `Rows to show`

## Error Handling
- Invalid/empty symbol: shows user-facing error
- Network issues: catches request exceptions and displays error message

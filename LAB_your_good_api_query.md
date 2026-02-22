# LAB: Your Good API Query

## Script
- File: `my_good_query.py`
- Purpose: Query daily stock data and print a clean preview table.

## Public API
- Provider: Stooq
- Endpoint: `https://stooq.com/q/d/l/`
- Params:
  - `s` symbol (example: `ibm.us`)
  - `i=d` daily interval

## Output Fields
- `Date`, `Open`, `High`, `Low`, `Close`, `Volume`

## Run
```bash
python3 my_good_query.py
```

## Error Handling
- If network or endpoint access fails, the script switches to sample rows.
- This keeps the lab demo runnable during submission.

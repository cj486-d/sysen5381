import json
import pandas as pd
import functions as fn
import os

_here = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(_here, "data", "hw2_course_notes.csv")


def search_course_notes(query: str, limit: int = 5) -> str:
    """Search local homework knowledge base and return matched rows as JSON."""
    df = pd.read_csv(DATA_FILE)
    terms = [t.strip() for t in query.split() if t.strip()]
    if not terms:
        terms = [query]

    mask = False
    for t in terms:
        mask = (
            mask
            | df["topic"].str.contains(t, case=False, na=False)
            | df["module"].str.contains(t, case=False, na=False)
            | df["summary"].str.contains(t, case=False, na=False)
            | df["tags"].str.contains(t, case=False, na=False)
            | df["difficulty"].str.contains(t, case=False, na=False)
        )
    rows = df.loc[mask].head(limit).to_dict(orient="records")
    return json.dumps(rows, indent=2)


def compute_study_priority() -> str:
    """Return a small priority table by difficulty for planning next study steps."""
    df = pd.read_csv(DATA_FILE)
    counts = (
        df.groupby("difficulty")["id"]
        .count()
        .rename("count")
        .reset_index()
        .sort_values("count", ascending=False)
    )
    rows = counts.to_dict(orient="records")
    return json.dumps(rows, indent=2)


# Register tools into functions module scope so agent_run wrapper can execute them.
fn.search_course_notes = search_course_notes
fn.compute_study_priority = compute_study_priority


tool_search_course_notes = {
    "type": "function",
    "function": {
        "name": "search_course_notes",
        "description": "Search the local course knowledge base and return relevant rows.",
        "parameters": {
            "type": "object",
            "required": ["query", "limit"],
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Keyword or phrase to search (e.g., 'RAG', 'tools', 'MCP').",
                },
                "limit": {
                    "type": "number",
                    "description": "Maximum number of rows to return.",
                },
            },
        },
    },
}


tool_compute_study_priority = {
    "type": "function",
    "function": {
        "name": "compute_study_priority",
        "description": "Compute count of topics by difficulty level for prioritization.",
        "parameters": {
            "type": "object",
            "required": [],
            "properties": {},
        },
    },
}

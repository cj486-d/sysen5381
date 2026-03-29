import os
import sys
from pprint import pprint

_here = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_here)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from functions import agent_run
from homework2.hw2_rag_tools import tool_search_course_notes, tool_compute_study_priority

MODEL = "smollm2:1.7b"


def main():
    role = (
        "You are a tool-using assistant. "
        "Call search_course_notes with query='RAG tools MCP' and limit=4."
    )
    task = "Find relevant notes for RAG + tools + MCP."

    resp1 = agent_run(role=role, task=task, model=MODEL, output="tools", tools=[tool_search_course_notes])
    print("=== Tool Call Demo 1: search_course_notes ===")
    pprint(resp1)
    print()

    role2 = "Call compute_study_priority and return tool output."
    resp2 = agent_run(role=role2, task="Compute priorities.", model=MODEL, output="tools", tools=[tool_compute_study_priority])
    print("=== Tool Call Demo 2: compute_study_priority ===")
    pprint(resp2)


if __name__ == "__main__":
    main()

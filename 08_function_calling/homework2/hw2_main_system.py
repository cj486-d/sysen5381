import json
from datetime import datetime
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_here)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from functions import agent_run
from homework2.hw2_rag_tools import (
    search_course_notes,
    compute_study_priority,
    tool_search_course_notes,
    tool_compute_study_priority,
)

MODEL = "smollm2:1.7b"


def run_homework2_pipeline(student_goal: str, query: str = "RAG and tools"):
    """Run 3-agent workflow: retrieval/tooling -> analysis -> action plan."""

    # Agent 1 (tool-enabled): make two explicit tool-enabled calls.
    role1_notes = (
        "You are Agent 1 (Retriever). "
        "Call search_course_notes with the user's query and limit=6. "
        "Return tool output."
    )
    role1_priority = (
        "You are Agent 1 (Planner). "
        "Call compute_study_priority and return tool output."
    )

    notes_tool_output = agent_run(
        role=role1_notes,
        task=f"Search query is: {query}",
        model=MODEL,
        output="text",
        tools=[tool_search_course_notes],
    )
    priority_tool_output = agent_run(
        role=role1_priority,
        task="Compute difficulty priority now.",
        model=MODEL,
        output="text",
        tools=[tool_compute_study_priority],
    )

    # Fallback if a model skips a tool call.
    if not isinstance(notes_tool_output, str) or "[" not in notes_tool_output:
        notes_tool_output = search_course_notes(query, 6)
    if not isinstance(priority_tool_output, str) or "[" not in priority_tool_output:
        priority_tool_output = compute_study_priority()

    agent1_payload = {
        "goal": student_goal,
        "query": query,
        "retrieved_notes": json.loads(notes_tool_output),
        "difficulty_priority": json.loads(priority_tool_output),
    }
    agent1_output = json.dumps(agent1_payload, indent=2)

    # Agent 2: synthesize RAG evidence into insights
    role2 = (
        "You are Agent 2 (Analyst). "
        "From the JSON evidence, write markdown with sections: "
        "Summary, Key Evidence (table), Risks, and Recommended Focus Areas."
    )

    agent2_output = agent_run(
        role=role2,
        task=agent1_output,
        model=MODEL,
        output="text",
        tools=None,
    )

    # Agent 3: produce a one-week execution plan
    role3 = (
        "You are Agent 3 (Execution Coach). "
        "Using Agent 2 analysis, output a 7-day plan with daily task bullets and one measurable checkpoint per day."
    )

    agent3_output = agent_run(
        role=role3,
        task=agent2_output,
        model=MODEL,
        output="text",
        tools=None,
    )

    return agent1_output, agent2_output, agent3_output


if __name__ == "__main__":
    goal = "Build a complete AI agent system for Homework 2 with strong RAG and tool integration."
    a1, a2, a3 = run_homework2_pipeline(goal, query="RAG tools MCP")

    print("=== HOMEWORK 2 RUN ===")
    print(f"Timestamp: {datetime.now().isoformat(timespec='seconds')}")
    print()

    print("=== Agent 1 Output (Tool + RAG Retrieval) ===")
    print(a1)
    print()

    print("=== Agent 2 Output (Integrated Analysis) ===")
    print(a2)
    print()

    print("=== Agent 3 Output (Execution Plan) ===")
    print(a3)

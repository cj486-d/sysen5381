# Homework 2: AI Agent System with RAG and Tools
Student: Chunlin Jiang

## 1. Writing Component (3+ paragraphs)
This project implements a complete AI agent system that combines multi-agent orchestration, retrieval-augmented generation (RAG), and function-calling tools. The system is designed to support course-planning decisions for DSAI coursework by retrieving relevant notes from a local knowledge base and transforming that evidence into actionable recommendations. Instead of asking one model to do everything at once, I separated the workflow into specialized agents so each step has a clear responsibility.

The first agent is a retrieval/tool-use agent. It calls custom tools to query a structured CSV data source and to compute a priority summary by difficulty level. This gives the pipeline grounded context in JSON format rather than relying on model memory alone. The second agent converts that structured evidence into an integrated analysis, including summary statements and recommended focus areas. The third agent turns the analysis into a time-bound execution plan, so the final output is not just descriptive but operational.

A key design choice was to keep tool functions deterministic and local. This reduced API dependency issues and made outputs reproducible for grading. I also added a fallback path so retrieval data is still produced even if the model does not trigger a tool call in a specific run. The main challenge was aligning output format consistency across agents; I improved this by tightening role prompts and explicitly constraining each agent’s expected output structure.

## 2. Code Links (Git Repository Links)
- Multi-agent orchestration script:
  - `https://github.com/cj486-d/sysen5381/blob/main/08_function_calling/homework2/hw2_main_system.py`
- RAG implementation:
  - `https://github.com/cj486-d/sysen5381/blob/main/08_function_calling/homework2/hw2_rag_tools.py`
- Function-calling/tool definitions:
  - `https://github.com/cj486-d/sysen5381/blob/main/08_function_calling/homework2/hw2_rag_tools.py`
- Main system file:
  - `https://github.com/cj486-d/sysen5381/blob/main/08_function_calling/homework2/hw2_main_system.py`

Local file references used in this project:
- `/Users/jiangchunlin/dsai/08_function_calling/homework2/hw2_main_system.py`
- `/Users/jiangchunlin/dsai/08_function_calling/homework2/hw2_rag_tools.py`
- `/Users/jiangchunlin/dsai/08_function_calling/homework2/data/hw2_course_notes.csv`

## 3. Screenshots/Outputs (3–4 total)
Use these outputs for screenshots:

1. Multi-agent workflow in action:
- File: `/Users/jiangchunlin/dsai/08_function_calling/homework2/outputs/hw2_main_system_output.txt`
- Capture sections:
  - `=== Agent 1 Output (Tool + RAG Retrieval) ===`
  - `=== Agent 2 Output (Integrated Analysis) ===`
  - `=== Agent 3 Output (Execution Plan) ===`

2. RAG retrieval and response:
- File: `/Users/jiangchunlin/dsai/08_function_calling/homework2/outputs/hw2_main_system_output.txt`
- Capture where `retrieved_notes` JSON appears plus the Agent 2 summary/analysis.

3. Function calling/tool usage:
- File: `/Users/jiangchunlin/dsai/08_function_calling/homework2/outputs/hw2_tool_call_demo_output.txt`
- Capture:
  - `=== Tool Call Demo 1: search_course_notes ===`
  - `=== Tool Call Demo 2: compute_study_priority ===`

4. Optional extra evidence screenshot:
- Show `hw2_rag_tools.py` with tool schemas and function definitions.

## 4. Documentation
### System Architecture
- Agent 1 (Retriever/Tool User): calls custom tools to fetch RAG evidence and compute planning stats.
- Agent 2 (Analyst): synthesizes JSON evidence into structured interpretation.
- Agent 3 (Execution Coach): generates a weekly action plan from Agent 2 output.

Flow:
1. User goal + query -> Agent 1
2. Agent 1 tool output (JSON evidence) -> Agent 2
3. Agent 2 analysis (markdown narrative) -> Agent 3
4. Agent 3 outputs implementation plan

### RAG Data Source
- Data source: `hw2_course_notes.csv` (12 records)
- Fields: `topic`, `module`, `difficulty`, `summary`, `tags`
- Search function: `search_course_notes(query, limit)`
  - Tokenizes query by spaces
  - Matches terms across multiple columns
  - Returns top N rows as JSON

### Tool Functions
| Tool Name | Purpose | Parameters | Returns |
|---|---|---|---|
| `search_course_notes` | Retrieve relevant course notes for RAG context | `query` (string), `limit` (number) | JSON list of matched rows |
| `compute_study_priority` | Summarize note counts by difficulty | none | JSON list: difficulty vs. count |

### Technical Details
- Language: Python 3
- Core package: local `functions.py` wrapper (`agent_run`)
- Model endpoint: local Ollama (`smollm2:1.7b`)
- Key files:
  - `08_function_calling/homework2/hw2_main_system.py`
  - `08_function_calling/homework2/hw2_rag_tools.py`
  - `08_function_calling/homework2/data/hw2_course_notes.csv`
  - `08_function_calling/homework2/outputs/*.txt`

### Usage Instructions
1. Go to project folder:
   - `cd /Users/jiangchunlin/dsai/08_function_calling`
2. Ensure Ollama is running and model exists:
   - `ollama list`
   - if needed: `ollama pull smollm2:1.7b`
3. Run integrated system:
   - `python homework2/hw2_main_system.py > homework2/outputs/hw2_main_system_output.txt`
4. Run tool-call evidence script:
   - `python homework2/hw2_tool_call_demo.py > homework2/outputs/hw2_tool_call_demo_output.txt`
5. Take 3–4 screenshots from output files and place them in the final `.docx`.

## Appendix: Output Files
- `/Users/jiangchunlin/dsai/08_function_calling/homework2/outputs/hw2_main_system_output.txt`
- `/Users/jiangchunlin/dsai/08_function_calling/homework2/outputs/hw2_tool_call_demo_output.txt`

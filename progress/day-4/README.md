# Day 4 — Agent orchestration & PO generation

**Status:** Not started.

## Planned work

- ROP / EOQ logic.
- LangChain ReAct agent with tools: inventory query, forecast run, PO draft, risk search.
- End-to-end: low stock → agent reasoning → draft PO.

## Deliverables checklist

- [ ] Agent uses tools without crashing on bad/missing data (graceful warnings).
- [ ] PO draft includes supplier choice rationale (price, lead time, reliability).

Commit example: `feat: day-4 langchain react agent + po generation`

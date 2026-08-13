# Delta Report

**Old:** `research/agent-discovery` (first pass, manual) — 5 findings, 0 rejected
**New:** `research/agent-discovery/runs/2026-08-12-deepseek` (DeepSeek run) — 38 findings, 74 rejected, 0 pending (HIGH/MEDIUM but over the Pass 2 budget cap — not a rejection)

_Matching uses normalized names (parentheticals/punctuation stripped) so e.g. "PII Sanitization Agent (TrustBoost)" and "PII Sanitization Agent" count as the same project._

## Projects added (DeepSeek found, first pass missed)

- 24/7 AI Chatbot (Customer Service)
- AgentEval: Multi-Agent Assessment System (AutoGen)
- Async Sequential Task-Solving (AutoGen)
- Auto Build Multi-agent System with AgentBuilder (AutoGen)
- Chatbot Simulation Evaluation (LangGraph)
- Complex Task Solving by Group Chat (6 members) (AutoGen)
- Customer Support Agent (LangGraph)
- Email Auto Responder Flow (CrewAI)
- Extraction with Retries (LangGraph)
- Group Chat (3 members, 1 manager) (AutoGen)
- Group Chat with Custom Speaker Selection (AutoGen)
- Hierarchical Agent Teams (LangGraph)
- Instagram Post Generator (CrewAI)
- Job Posting Generator (CrewAI)
- Landing Page Generator (CrewAI)
- Lead Score Flow (CrewAI)
- Marketing Strategy Generator (CrewAI)
- Match Profile to Positions (CrewAI)
- Meeting Assistant Flow (CrewAI)
- Multi-Agent Collaboration (LangGraph)
- Multi-Agent Workflow (Supervisor) LangGraph
- Plan-and-Execute Agent (LangGraph)
- Real-Time Threat Detection Agent
- Recruitment Recommendation Agent
- Recruitment Workflow (CrewAI)
- Reflection Agent (LangGraph)
- Reflexion Agent (LangGraph)
- Self Evaluation Loop Flow (CrewAI)
- Sequence of Nested Chats (AutoGen)
- Sequential Chats with Different Initiating Agents (AutoGen)
- Sequential Task-Solving (single initiating agent) (AutoGen)
- Solving Complex Tasks with Nested Chats (AutoGen)
- Task Solving with Graph Transition Paths (AutoGen)
- Track LLM Calls and Errors using AgentOps (AutoGen)
- TrustBoost PII Sanitizer
- Vibe Hacking Agent

## Projects removed — DeepSeek actively dropped (LOW/REJECT this run)

- CrewAI Examples — Lead Score Flow
- GenAI_Agents (NirDiamant)
- PII Sanitization Agent (TrustBoost)

## Projects removed — NOT dropped, just over Pass 2 budget this run (see shortlist_pending.json)

_none_

## Recommendation (treatment) changes

- **Agent Memory Guard**: `REUSE` → `ADAPT`
- **Citadel**: `ADAPT` → `STUDY ONLY`

## Priority changes

_none_

## License verification differences

_none_

## DeepSeek token/cost usage (this run)

- Models: Pass 1 = deepseek-chat | Pass 2 = deepseek-reasoner
- Tokens: in=47,063 out=44,150 total=91,213
- Estimated cost: ~$0.1112 USD
- Duration: 392.8s
- Sources analyzed: 1  |  Pass 1 candidates: 112  |  Pass 2 deep-analysed: 38

## Claude work avoided (estimate)

- DeepSeek classified 112 candidates from 1 source(s) and deep-analysed 38 of them — comparable volume of README reading + comparison that the first pass had Claude do directly.
- Zero Claude tokens were spent on this run's classification/analysis passes; Claude's role here is limited to running this diff and reviewing the result.

## Recommendation

This report does NOT auto-promote the DeepSeek run to canonical. Review the sections above, then decide by hand whether these artifacts should replace `research/agent-discovery/shortlist.json` etc., or whether a follow-up pass is needed.
# Specification: hello-world-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [x] Read `product-requirements-document.md` and `intent.md` for full context.
- [x] Bootstrap agent code in `assets/hello-world-agent/` using instructions from the sap-agent-bootstrap section. (invoke from inside `assets/hello-world-agent/`, use copy commands — do NOT create files manually)
- [x] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

No runtime skills are required for this agent. The response is static ("hello world").

---

## Project-Specific Tasks

## Hello World Response

- [x] Open `assets/hello-world-agent/app/agent.py`
- [x] Set the system prompt (via `@prompt_section`) to instruct the agent to respond with "hello world" to any incoming message
- [x] Ensure the agent's `stream()` method returns the string "hello world" as the response regardless of the input message
- [x] Verify the agent card (`/.well-known/agent.json`) correctly describes the agent's capability: "Responds with hello world to any message"

---

## Business Instrumentation

- [x] Implement business step instrumentation for each milestone from the PRD: structured logging with pattern `[MILESTONE_ID].[achieved|missed]: [description]` and OpenTelemetry custom spans:
  - `M1.achieved: agent project scaffolded successfully` / `M1.missed: agent project scaffolding did not complete`
  - `M2.achieved: hello world response verified` / `M2.missed: agent response did not return hello world`
  - `M3.achieved: agent deployed and endpoint reachable` / `M3.missed: deployment failed or endpoint unreachable`
- [x] Verify `bootstrap(app)` is called after `app = server.build()` in `main.py`

---

## MCP Tool Integration

No MCP tool integration is required for this agent. It has no external API dependencies.

---

## Testing

- [x] `conftest.py` only sets `IBD_TESTING=true`
- [x] Write one integration test executing end-to-end agent flow: send any message → verify response contains "hello world"
- [x] Run `pytest` from `assets/hello-world-agent/` (no args) — coverage: 72% ✓ (above 70% threshold)
- [x] Run `pytest` again from `assets/hello-world-agent/` (no args) to generate final `test_report.json`
- [x] Verify `test_report.json` exists in `assets/hello-world-agent/`

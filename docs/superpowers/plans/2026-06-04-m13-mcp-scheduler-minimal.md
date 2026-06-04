# M13 MCP Scheduler Minimal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the minimal internal MCP scheduler for dry-run research orchestration, audit logging, and ToolPolicy safety checks.

**Architecture:** Add small orchestration modules under `src/quant_mas/orchestration`: message bus, audit JSONL helpers, and a mock-first scheduler. The CLI `scripts/run_mcp_pipeline.py` exposes dry-run smoke recipes without replacing M4 ResearchWorkflow or SupervisorAgent.

**Tech Stack:** Python dataclasses, pathlib, JSONL, argparse, pytest, existing `ToolPolicy`.

---

### Task 1: Tests First

**Files:**
- Create: `tests/test_mcp_scheduler.py`

- [ ] Write tests covering message bus publish/subscribe, audit JSONL append/read/summarize, dry-run scheduler node order, policy denial, CLI help, and list recipes.
- [ ] Run `python -m pytest tests/test_mcp_scheduler.py -v`.
- [ ] Expected: fail because `quant_mas.orchestration.agent_communication`, `mcp_scheduler`, and `audit_log` do not exist yet.

### Task 2: Core Modules

**Files:**
- Create: `src/quant_mas/orchestration/agent_communication.py`
- Create: `src/quant_mas/orchestration/audit_log.py`
- Create: `src/quant_mas/orchestration/mcp_scheduler.py`
- Modify: `src/quant_mas/orchestration/__init__.py`

- [ ] Implement immutable message dataclasses and `InMemoryMessageBus`.
- [ ] Implement append-only audit JSONL helpers.
- [ ] Implement `MCPScheduler` with built-in dry-run recipes and ToolPolicy checks.
- [ ] Export new public classes from `orchestration.__init__`.
- [ ] Run `python -m pytest tests/test_mcp_scheduler.py -v`.
- [ ] Expected: pass core tests except CLI tests if CLI is not implemented yet.

### Task 3: CLI

**Files:**
- Create: `scripts/run_mcp_pipeline.py`

- [ ] Implement `--help`, `--list-recipes`, `--recipe`, `--output-dir`, and dry-run default behavior.
- [ ] Run `python scripts/run_mcp_pipeline.py --help`.
- [ ] Run `python scripts/run_mcp_pipeline.py --list-recipes`.
- [ ] Run `python -m pytest tests/test_mcp_scheduler.py -v`.
- [ ] Expected: pass.

### Task 4: Verification

**Files:**
- No code changes expected.

- [ ] Run `python -m pytest -v`.
- [ ] Update project docs only if implementation details differ from `docs/mcp_protocol.md`.
- [ ] Report changed files and test results.

---
name: Bug report
about: Report a reproducible bug in Quant MAS
title: "[Bug] "
labels: bug
assignees: ""
---

## Summary

Briefly describe the bug.

## Environment

- OS:
- Python version:
- Quant MAS commit:
- Install command:
- Optional extras installed: `data` / `ml` / `orchestration` / `text` / none

## Command

```bash
# Paste the exact command
```

## Configs and Data Source

- Config path:
- Storage config:
- Data source: synthetic / yfinance / stooq / alpha_vantage / finnhub / fred / sec_edgar / other
- Data size or date range:

## LLM / Agent

- LLM enabled: yes / no
- LLM provider: mock / openai_compatible / other
- Agent used: none / SupervisorAgent / ResearchAgent / ReportAgent / other

## Expected Behavior

What should happen?

## Actual Behavior

What happened instead?

## Logs or Traceback

```text
Paste relevant logs. Do not include API keys.
```

## Acceptance Criteria

- [ ] Bug is reproduced by a small test or command
- [ ] Fix does not require real network calls in pytest
- [ ] `python -m pytest -v` passes

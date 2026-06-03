---
name: Feature request
about: Suggest a new feature or extension
title: "[Feature] "
labels: enhancement
assignees: ""
---

## Motivation

What research or engineering problem does this solve?

## Proposed Design

Describe the intended module, CLI, config, or API.

## Affected Layer

- [ ] Quant Engine
- [ ] Strategy / Backtest / Risk
- [ ] ML / Text Signals
- [ ] Tool Layer
- [ ] Agent Layer
- [ ] Memory / RAG
- [ ] LangGraph / Workflow
- [ ] Docs

## Data Source

- Source:
- Expected schema:
- Network/API needed: yes / no
- Mock strategy for tests:

## LLM / Agent

- Does this use an LLM? yes / no
- Provider: mock / openai_compatible / local / not applicable
- How will tests avoid real LLM calls?

## Acceptance Criteria

- [ ] Includes tests with synthetic or mocked data
- [ ] Does not allow LLM Agent direct live trading
- [ ] Does not commit API keys or large artifacts
- [ ] Documentation/config examples updated

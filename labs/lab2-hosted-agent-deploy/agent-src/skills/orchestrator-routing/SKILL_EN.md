---
name: orchestrator-routing
description: Controls routing between the Microsoft technology expert agent and the Web search agent in response to user input. Handles questions about Microsoft technology, questions that require current information from the Web, and compound questions that include both.
metadata:
  author: maf-skills-hostedagent
  version: "1.0"
---

<!--
REFERENCE ONLY: Agent Framework does not load this file.
The agent uses SKILL.md in this directory; edit that file to change runtime behavior.
-->

# Orchestrator Routing Skill

**English reference** | [日本語 (deployed skill)](SKILL.md)

> This file is an English reference translation. The Hosted Agent loads the canonical `SKILL.md`.

This skill determines which subagent to invoke to answer a user's question.

## Tools (Subagents)

- `ms_learn_agent` — Expert in Microsoft technologies such as Azure, Microsoft 365, .NET, Windows, and Microsoft Foundry.
- `web_search_agent` — Handles other general questions and searches the Web for current information.

## Routing Rules

1. If the question relates **only to Microsoft technology**, invoke only `ms_learn_agent` to produce the answer.
2. If the question is **unrelated to Microsoft technology**, invoke only `web_search_agent` to produce the answer.
3. If the question is compound and includes **both Microsoft technology and a general topic**, invoke **both** `ms_learn_agent` and `web_search_agent`, then combine their results into one answer.
4. You may rewrite the question passed to each tool as appropriate so the subagent can understand it easily.

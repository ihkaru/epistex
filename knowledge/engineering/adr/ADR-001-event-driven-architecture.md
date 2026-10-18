---
title: "ADR-001: Event-Driven Architecture and Dependency Inversion"
status: "active"
category: "architecture-decision"
owner: "@platform-eng"
tags:
  - "architecture"
  - "eda"
  - "solid"
---

# ADR-001: Event-Driven Architecture and Dependency Inversion

## Context and Problem Statement
Knowledge base CLI tooling must serve dual audiences: human operators and autonomous coding agents.
When autonomous agents interact with tooling, hardcoded couplings, unhandled side-effects, and silent failures lead to corrupted workspaces. We need an extensible, decoupled architecture where commands emit domain events and dependencies are passed through contracts.

## Decision
1. **Dependency Inversion Principle (DIP)**: All business logic, code runners, and secret managers depend on abstract interfaces (`src/contracts/`), never concrete implementations.
2. **Event-Driven Architecture (EDA)**: All major lifecycle actions (document creation, frontmatter extraction, code execution, health check completion) publish typed domain events through an `EventDispatcher`.
3. **Pluggable Secret Backends**: First-party Infisical support with graceful zero-crash fallback to environment variables.

## Consequences & Blast Radius
- **Positive**: New commands, audit listeners, or secret providers can be added without modifying existing core code (Open/Closed Principle).
- **Positive**: Complete hermetic testing with zero reliance on network or external binaries.
- **Trade-off**: Requires explicit contracts and event definitions, but guarantees long-term enterprise maintainability.

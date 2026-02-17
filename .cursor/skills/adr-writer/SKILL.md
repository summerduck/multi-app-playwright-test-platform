---
name: adr-writer
description: Write Architecture Decision Records in the project's Cognitect ADR format with Status, Context, Decision, and Consequences sections. Use when documenting architecture decisions, recording technical choices, writing ADRs, or when the user mentions ADR, architecture decision, or technical decision.
---

# ADR Writer

Generate Architecture Decision Records consistent with the existing ADRs in `docs/arch/`.

## Before Writing

1. List existing ADRs in `docs/arch/` to determine the next sequential number
2. Read at least one existing ADR to match the established voice and depth
3. Gather alternatives that were considered (at least 2)
4. Think through consequences — both positive and negative

## File Placement and Naming

```
docs/arch/ard-<NNN>-<slug>.md
```

- Prefix: `ard-` (this project's convention — not the standard `adr-`)
- Number: zero-padded to 3 digits, sequential
- Slug: lowercase, hyphen-separated summary

Examples: `ard-005-ci-cd-design.md`, `ard-006-docker-strategy.md`

## ADR Template

```markdown
# ADR <N>: <Title>

## Status

Proposed

## Context

<Describe the problem or situation requiring a decision. Include:>
<- What triggered this decision?>
<- What are the constraints?>
<- What requirements must be met?>

Alternatives considered: <list alternatives separated by commas>.

## Decision

<State the decision clearly. Explain what will be used/done and how.>

Reasons:

- <Reason 1 — concrete, not vague>
- <Reason 2>
- <Reason 3>
- <Reason 4>

## Consequences

- <Positive consequence 1>
- <Positive consequence 2>
- <Negative consequence or tradeoff 1>
- <Negative consequence or tradeoff 2>
```

## Status Values

| Status | When to use |
|--------|-------------|
| `Proposed` | Initial state for new ADRs awaiting review |
| `Accepted` | Decision approved and in effect |
| `Deprecated` | Decision no longer applies |
| `Superseded by ADR <N>` | Replaced by a newer decision |

## Writing Guidelines

### Context Section
- Open with a project-level problem: "The framework needs...", "The 3-app test platform requires..."
- Name specific project constraints: Python 3.12 ecosystem, Playwright 1.51.0, pytest-xdist parallelism, 3 target apps (SauceDemo, The Internet, UI Playground), GitHub Actions CI
- Always list alternatives considered in a single line at the end
- Reference the roadmap (`/.notes/roadmap.md`) when the decision relates to a planned milestone

### Decision Section
- Open with: "The framework uses [X]" or "Tests are structured using [Y]"
- Include a link to the tool/library/pattern when relevant
- List reasons as bullet points — each reason should be specific and verifiable
- Aim for 4-6 reasons
- Reference existing project tooling when the decision interacts with it (e.g., "integrates with the existing Ruff + mypy + Bandit pipeline")

### Consequences Section
- Mix positive and negative consequences
- Be specific to the project: "CI matrix runs tests across 3 browsers per application (9 jobs)" not "Tests run in CI"
- Include operational impact: setup requirements, maintenance burden, learning curve
- Mention fallback or escape hatches when applicable

## Existing ADRs

Before writing, list `docs/arch/` to get the current set. The table below is a snapshot — update it when new ADRs are merged:

| ADR | Title | Status | Key Pattern |
|-----|-------|--------|-------------|
| 001 | Playwright selection | Accepted | 4 alternatives, 6 reasons, benefits + costs |
| 002 | Code quality infrastructure | Accepted | Full toolchain, quantified impact ("Ruff 10-100x faster") |
| 003 | Git strategy | Accepted | Branching strategy specifics |
| 004 | Cursor AI Skills | Proposed | AI-augmented development documentation |

Match the depth and specificity of ADR 001 and 002 — they set the bar.

## Planned ADRs (from roadmap)

- ADR: Page Object Pattern — BasePage, method chaining, component composition
- ADR: CI/CD Design — matrix strategy, quality gates, artifact management
- ADR: Docker Strategy — multi-stage builds, browser images, Compose services
- ADR: Performance Testing Integration — Locust, load shapes, thresholds

## Rules

- Keep each section concise — an ADR should be readable in under 2 minutes
- Do not repeat information between sections
- Consequences must include at least one negative/tradeoff item
- Always list alternatives in the Context section
- Use present tense for decisions: "uses", "runs", "requires"
- Do not include implementation details — ADRs document *what* and *why*, not *how*

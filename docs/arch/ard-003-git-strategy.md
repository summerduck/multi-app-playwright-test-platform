# ADR 3: Git Branching Strategy

## Status

Accepted

## Context

The project is a test automation framework, not a deployed product — there are no staged environments or versioned releases to manage. The codebase is maintained by a solo developer with CI checks running on every pull request. A branching strategy needs to balance process discipline with low overhead.

Alternatives considered: Git Flow (too complex — `develop`/`release`/`hotfix` branches add ceremony with no benefit for a non-deployed tool), Trunk-Based Development (no PR audit trail for portfolio visibility), GitLab Flow (environment branches are irrelevant without deployment targets).

## Decision

Use [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow) with the following conventions:

- **Single long-lived branch:** `main` (always stable, protected via `no-commit-to-branch` hook)
- **Short-lived feature branches** off `main`, named `<type>/<description>` using [Conventional Commits](https://www.conventionalcommits.org/) types: `feat/`, `fix/`, `chore/`, `docs/`, `refactor/`, `test/`, `perf/`
- **Squash merge** to keep `main` history clean — one commit per feature/change
- **CI must pass** before merge (code quality + test workflows)

Branch protection on `main` enforces the workflow at the GitHub level:

- Pull request required before merging (no direct pushes)
- Status checks must pass ("Code Quality Checks")
- Branch must be up to date before merging

Reasons:

- GitHub Flow is the simplest strategy that provides PR-based review and CI gating
- Squash merges keep `main` history readable — one commit per change, no merge noise
- Conventional Commits branch prefixes (`feat/`, `fix/`, `chore/`) make branch purpose visible at a glance
- Branch protection enforces the workflow server-side — it cannot be bypassed locally
- Short-lived branches reduce merge conflicts and keep changes focused

## Consequences

- Clean, linear `main` history where each commit maps to one completed change
- PR trail provides an auditable record of every decision
- Branch lifetime kept short (ideally < 1 week) to avoid merge conflicts
- Milestone tags (`v0.1.0`, `v0.2.0`) can mark roadmap progress without release branches
- Protection rules are enforced server-side — local hooks (`no-commit-to-branch`) act as an early warning, GitHub enforces the gate

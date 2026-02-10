# ADR 1: Playwright as the E2E Testing Framework

## Status

Accepted

## Context

The project needs a browser automation framework for E2E testing across three web applications (SauceDemo, The Internet, UI Testing Playground). Requirements include multi-browser support (Chromium, Firefox, WebKit), reliable handling of dynamic elements, and Python ecosystem compatibility.

Alternatives considered: Selenium, Cypress, Puppeteer.

## Decision

The framework uses [Playwright](https://playwright.dev/python/) with Python, integrated via pytest-playwright.

Reasons:

- Native multi-browser support (Chromium, Firefox, WebKit) from a single API
- Auto-wait mechanism reduces flaky tests caused by timing issues
- Built-in tracing, screenshots, and video capture for debugging
- First-class Python support with async capabilities
- pytest integration via pytest-playwright plugin
- Parallel execution support via pytest-xdist

## Consequences

- All E2E tests use the Page Object Model on top of Playwright's API
- CI matrix runs tests across 3 browsers per application (9 jobs)
- Local setup requires `playwright install` to download browsers
- Playwright's auto-wait reduces the need for explicit waits and sleep calls

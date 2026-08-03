# Testing Strategy

## Pyramid

1. **Unit tests** — fast, isolated, many.
2. **Integration tests** — service + repository with real or test DB.
3. **End-to-end tests** — full user journeys in a browser.
4. **Accessibility tests** — automated a11y checks and manual screen-reader validation.
5. **Security tests** — SAST, dependency scanning, manual penetration tests.

## Frontend

- **Vitest + React Testing Library**: components, hooks, utilities.
- **Playwright**: critical user flows on desktop and mobile.
- **Coverage**: 60% line/function with branch awareness.

## Backend

- **pytest + pytest-asyncio**: services, repositories, API endpoints.
- **httpx ASGITransport**: integration tests through FastAPI.
- **Factories**: use `polyfactory` or simple builders to create test data.
- **Coverage**: 70% line/function with branch awareness.

## Accessibility

- Run `axe-core` in Playwright for each page.
- Validate keyboard navigation for all interactive components.
- Verify reduced-motion behavior.

## Performance

- Lighthouse CI in PRs to catch regressions.
- Playwright timing APIs for critical path measurement.

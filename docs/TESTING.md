# Detection and Testing Guide

## Automated Validation Commands

```bash
pytest tests/ -v --cov=navil --cov-report=term-missing
ruff check navil tests scripts
mypy navil tests scripts
pip-audit
```

## Coverage Intent

- Scope policy validation
- Crawler parsing and endpoint extraction
- Scanner plugin signal detection
- Adaptive brain update behavior
- Payload mutation correctness
- Chain construction from findings
- SQLite persistence integrity
- API health and auth access
- CLI invocation sanity

## Manual Verification Checklist

1. Launch desktop GUI with `python -m navil`.
2. Start a scan and verify live status/event updates.
3. Confirm findings table and severity rendering.
4. Export JSON/HTML/PDF report from GUI and inspect evidence.
5. Validate out-of-scope target is blocked.
6. Validate CLI mode still works with `navil scan ...`.

## QA Report (2026-04-07)

| Check | Status | Notes |
|---|---|---|
| Unit tests | Passed | `12 passed` |
| Coverage | Passed | `58% total` (`--cov-fail-under=55` in CI) |
| Linting | Passed | `ruff check navil tests scripts` |
| Type checks | Passed | `Success: no issues found in 100 source files` |
| Dependency audit | Passed | `No known vulnerabilities found` |
| Docker build | Passed | Multi-stage image build completed successfully |

### Notes on Coverage

The current coverage baseline focuses on core safety and scan logic paths. Remaining untested areas are primarily optional integrations and some orchestration branches. Next iteration should prioritize:

1. WebSocket event stream route coverage
2. End-to-end engine orchestration scenarios
3. Integration adapter mocks for Burp/Nuclei/Metasploit

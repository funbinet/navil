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

1. Run `python3 -m navil --help` and confirm CLI command registration.
2. Start a scan and verify status transitions until completion.
3. Generate JSON/HTML/PDF reports from CLI and inspect evidence.
4. Validate out-of-scope target is blocked.
5. Validate API health and auth-protected endpoints.

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

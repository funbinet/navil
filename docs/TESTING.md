# Detection and Testing Guide

This guide defines repeatable quality gates for Navil across linting, typing, unit tests, runtime smoke checks, and dependency hygiene.

## 1. Automated Validation Commands

Run from repository root:

```bash
python3 -m ruff check .
python3 -m mypy navil
python3 -m pytest -q
python3 -m pip_audit
```

## 2. Coverage Intent

Current test strategy prioritizes operational safety and deterministic core behavior.

Targeted areas:

- scope policy parsing and validation
- recon extraction and crawl behavior
- plugin execution and finding normalization
- adaptive-brain updates
- chain graph construction
- persistence and retrieval flow
- CLI/menu entrypoint behavior

## 3. Manual Operator Verification

Perform after significant UI/engine changes:

1. `python3 -m navil --help` renders expected commands
2. `navil` enters menu shell with stable panel rendering
3. selecting action shows help panel and proceed confirmation
4. foreground scan stream displays status updates
5. background jobs can be inspected and cleaned
6. report generation succeeds for at least one completed scan

## 4. API Verification Checklist

1. start API server
2. create scan with bearer token
3. poll scan status
4. fetch findings
5. verify unauthorized request rejection without token

## 5. Failure Injection Checklist

- invalid scope path (directory instead of file)
- out-of-scope target URLs
- unsupported report format requests
- missing optional external adapters

Expected behavior:

- explicit error message
- no silent failure
- no process crash for recoverable operator input errors

## 6. Current QA Snapshot

| Check | Status | Notes |
|---|---|---|
| Lint | Passing | `python3 -m ruff check .` |
| Typing | Passing | `python3 -m mypy navil` |
| Tests | Passing | `python3 -m pytest -q` |
| Dependency audit | Passing | `python3 -m pip_audit` |

## 7. CI Expectations

PR readiness criteria:

- lint clean
- mypy clean
- test suite green
- docs updated for operator-facing behavior changes

## 8. Next Coverage Priorities

1. richer engine orchestration integration tests
2. websocket event sequence coverage
3. adapter mocks for third-party tool connectors
4. report generation edge-case tests for malformed finding payloads

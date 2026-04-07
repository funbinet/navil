# API Reference

This document defines the Navil HTTP and WebSocket surface for automation, integration, and operational monitoring.

## Base URL

- local: `http://localhost:8080`
- API namespace: `/api`

## Authentication

All `/api/*` routes require a bearer token.

```http
Authorization: Bearer <token>
```

Default local token:

- `local-dev-token`

## Common Response Behavior

- Success responses are JSON objects or arrays.
- Validation failures return 4xx with details.
- Internal faults return 5xx.
- Long-running scans should be tracked by polling status or subscribing to WebSocket events.

## Endpoint Catalog

### POST /api/scans

Creates a scan job and returns scan metadata.

Request body:

```json
{
  "target_urls": ["https://example.com"],
  "scope_path": ".navil-scope.yml",
  "plugin_names": ["headers", "cors"],
  "max_depth": 3
}
```

Key fields:

- `target_urls`: required list of target URLs
- `scope_path`: required path to scope policy file
- `plugin_names`: optional plugin subset
- `max_depth`: optional depth override

### GET /api/scans/{scan_id}

Returns the current state for a scan.

Typical fields include:

- scan id
- status (`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELED`)
- runtime metrics
- summary data

### GET /api/scans/{scan_id}/findings

Returns findings associated with a scan id.

### DELETE /api/scans/{scan_id}

Requests cancellation of a running scan.

### GET /api/findings

Queries findings globally.

Optional query:

- `scan_id`: filter findings to one scan

### GET /api/brain/status

Returns adaptive brain state and reward profile snapshot.

### POST /api/brain/train

Applies reward updates to policy memory.

Request body:

```json
{
  "plugin_rewards": {
    "xss": 4.0,
    "sqli": 3.5
  }
}
```

### GET /api/config/scope/validate?path=.navil-scope.yml

Validates scope file syntax and policy shape.

### WS /ws/scan/{scan_id}

Streams scan events for real-time operators.

Event use cases:

- progress updates
- status transitions
- completion signal

## End-to-End cURL Workflow

Create scan:

```bash
curl -X POST http://localhost:8080/api/scans \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'Content-Type: application/json' \
  -d '{"target_urls":["https://example.com"],"scope_path":".navil-scope.yml"}'
```

Get status:

```bash
curl -H 'Authorization: Bearer local-dev-token' \
  http://localhost:8080/api/scans/<SCAN_ID>
```

Get findings:

```bash
curl -H 'Authorization: Bearer local-dev-token' \
  http://localhost:8080/api/scans/<SCAN_ID>/findings
```

## Integration Notes

- Keep token handling in secure secret stores.
- Treat scan ids as campaign identifiers for report archival.
- For dashboards, combine polling with WebSocket events.

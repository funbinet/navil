# API Reference

## Authentication

All `/api/*` endpoints require bearer token:

```http
Authorization: Bearer <token>
```

Default token for local development: `local-dev-token`.

## Endpoints

### POST /api/scans
Start a scan.

```json
{
  "target_urls": ["https://example.com"],
  "scope_path": ".navil-scope.yml",
  "plugin_names": ["headers", "cors"],
  "max_depth": 3
}
```

### GET /api/scans/{scan_id}
Get scan status and metrics.

### GET /api/scans/{scan_id}/findings
Get findings for one scan.

### DELETE /api/scans/{scan_id}
Cancel running scan.

### GET /api/findings
Query all findings (optionally `?scan_id=...`).

### GET /api/brain/status
Get adaptive brain snapshot.

### POST /api/brain/train
Update plugin rewards.

```json
{
  "plugin_rewards": {
    "xss": 4.0,
    "sqli": 3.5
  }
}
```

### GET /api/config/scope/validate?path=.navil-scope.yml
Validate and return scope file.

### WS /ws/scan/{scan_id}
Real-time scan events.

## Example cURL

```bash
curl -X POST http://localhost:8080/api/scans \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'Content-Type: application/json' \
  -d '{"target_urls":["https://example.com"],"scope_path":".navil-scope.yml"}'
```

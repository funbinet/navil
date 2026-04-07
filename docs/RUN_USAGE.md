# Run and Usage Guide

This guide explains how to install, run, and operate Navil through CLI and API workflows.

## 1. Install

From the repository root:

```bash
./scripts/setup.sh
```

Default behavior:
- Uses `python3`
- Installs dev dependencies to user site (`--user`)
- Does not require a virtual environment

Optional isolated environment:

```bash
./scripts/setup.sh --venv
```

## 2. Prepare Scope

Copy and edit your scope definition before scanning:

```bash
cp .navil-scope.example.yml .navil-scope.yml
navil scope validate .navil-scope.yml
```

Always keep only authorized targets inside this scope file.

## 3. Run Modes

### CLI

```bash
navil --help
python3 -m navil --help
```

### API Server

```bash
uvicorn navil.api.server:app --host 0.0.0.0 --port 8080 --reload
```

Default bearer token for local development:

- `local-dev-token`

## 4. CLI Workflow

Start a scan and wait for completion:

```bash
navil scan https://example.com --scope .navil-scope.yml --plugins headers,cors,info_disclosure
```

Start a scan without waiting:

```bash
navil scan https://example.com --scope .navil-scope.yml --no-wait
```

Generate reports:

```bash
navil report --scan-id <SCAN_ID> --format html
navil report --scan-id <SCAN_ID> --format pdf --output reports/final.pdf
```

Inspect and train adaptive policy:

```bash
navil brain status
navil brain train --episodes 200
```

Show runtime config:

```bash
navil config
```

## 5. API Workflow

Start scan:

```bash
curl -X POST http://localhost:8080/api/scans \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'Content-Type: application/json' \
  -d '{"target_urls":["https://example.com"],"scope_path":".navil-scope.yml"}'
```

Get scan status:

```bash
curl -H 'Authorization: Bearer local-dev-token' \
  http://localhost:8080/api/scans/<SCAN_ID>
```

Get findings:

```bash
curl -H 'Authorization: Bearer local-dev-token' \
  http://localhost:8080/api/scans/<SCAN_ID>/findings
```

## 6. Report Outputs

Reports can be generated in:
- `json`
- `html`
- `md`
- `pdf`

Common locations:
- CLI output path from `--output`
- Default generator output in local workspace

## 7. Troubleshooting

- Command not found for `navil`: reinstall with `./scripts/setup.sh` and ensure user site scripts are on `PATH`.
- Invalid scope errors: run `navil scope validate .navil-scope.yml` and correct schema values.
- API auth errors: send `Authorization: Bearer local-dev-token` (or your configured token).

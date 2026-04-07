# Run and Usage Guide

This guide describes production-style local operation of Navil with a strict no-virtual-environment model.

## 1. Runtime Policy

Navil in this repository is intentionally configured for real system Python.

- Use python3 from the host system
- Do not create or activate virtual environments
- Install to user site and run directly from shell

## 2. Installation

From repository root:

```bash
./scripts/setup.sh
```

The setup flow:

- Upgrades pip (with fallback for externally managed Python)
- Installs requirements-dev.txt to user site
- Installs Navil in editable mode with CLI entrypoints

Expected commands after install:

- navil
- navel
- navil-api

If shell cannot locate commands:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## 3. Scope Preparation

Create local scope file:

```bash
cp .navil-scope.example.yml .navil-scope.yml
```

Validate before scanning:

```bash
navil scope validate .navil-scope.yml
```

Scope guidance:

- Keep target domains explicit and minimal
- Restrict methods to authorized verbs
- Keep request and crawl budgets conservative at first pass
- Enforce TLS and allowed ports where possible

## 4. Execution Surfaces

### 4.1 Menu-Driven Shell

Launch:

```bash
navil
```

Equivalent explicit command:

```bash
navil start
```

Prompt grammar:

```text
navil [menu]> Option:
navil [Web Scan]> Targets comma URLs:
navil [Reports]> Format [html(h)/json(j)/md(m)/pdf(p)]:
```

Menu behavior:

- Uniform panel layout
- Help panel before actions (purpose + expected inputs + effect)
- Proceed gate using short approvals (y/n, f/b)
- Foreground stream visualization for long tasks
- Background queue with inspect and clear flows

### 4.2 Command Mode

Discover commands:

```bash
navil --help
```

Common sequence:

```bash
navil scope validate .navil-scope.yml
navil scan https://example.com --scope .navil-scope.yml --plugins headers,cors,info_disclosure
navil report --scan-id <SCAN_ID> --format html
```

Adaptive brain controls:

```bash
navil brain status
navil brain train --episodes 200
```

### 4.3 API Mode (Optional)

Start server:

```bash
uvicorn navil.api.server:app --host 0.0.0.0 --port 8080 --reload
```

Authentication header:

```http
Authorization: Bearer local-dev-token
```

## 5. Action Playbooks

### 5.1 Web Scan

Required inputs:

- Targets comma URLs
- Scope path (file, not directory)

Optional inputs:

- Plugin list
- Max depth override

Foreground mode:

- Streams scan progress and state transitions
- Returns summary payload with findings and reward score

Background mode:

- Returns job id immediately
- Output is available under Background Jobs menu

### 5.2 Path Audit

Use when evaluating local folder/file hygiene quickly.

Inputs:

- Path file or folder
- Max depth
- Max entries

Output:

- Summary counts
- Top extension histogram
- Findings sample

### 5.3 System Audit

Use when evaluating system-level file hygiene baseline.

Inputs:

- Max depth
- Max entries
- Mode (foreground/background)

Behavior:

- Audits from /
- Skips volatile pseudo-filesystems (proc/sys/dev/run/tmp)

### 5.4 Reports

Sources:

- Direct scan id
- Recent saved scan selection

Formats:

- html
- json
- md
- pdf

### 5.5 History and Presets

Capabilities:

- Command input history snapshot
- Save last scan profile as preset
- Activate/delete presets

## 6. API Workflow Examples

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

## 7. Troubleshooting Matrix

- navil not found:
  - re-run ./scripts/setup.sh
  - export PATH with ~/.local/bin
- Scope path error (is a directory):
  - provide .navil-scope.yml file path
- Missing dependency in plain shell:
  - re-run ./scripts/setup.sh and confirm user-site install
- API unauthorized:
  - verify bearer token in request header

## 8. Operational Guardrails

- Run only against approved assets
- Keep scope policy under version control
- Archive reports per scan campaign
- Track policy training updates with commit history

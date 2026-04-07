# Creation Guide

This guide provides the canonical repository bootstrap flow for Navil using system Python only.

## 1. Prerequisites

- Linux/macOS shell environment
- `python3` 3.11+
- network access for dependency installation
- optional: Docker for containerized service runs

## 2. Clone and Initialize

```bash
git clone https://github.com/funbinet/navil.git
cd navil
./scripts/setup.sh
```

Important runtime policy:

- this repository does not use virtual environments
- installation targets user site via system python

## 3. Verify Runtime Surface

```bash
python3 -m navil --help
navil --help
navel --help
```

If command resolution fails:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## 4. Scope Bootstrap

Create scope file:

```bash
cp .navil-scope.example.yml .navil-scope.yml
```

Validate scope:

```bash
navil scope validate .navil-scope.yml
```

Recommended policy setup:

- define explicit authorized domains
- restrict HTTP methods to approved list
- set depth and request budgets conservatively
- enforce TLS and allowed ports where required

## 5. First Operational Run

Menu-shell path:

```bash
navil
```

Command-line path:

```bash
navil scan https://target.example --scope .navil-scope.yml --plugins headers,cors,info_disclosure
```

Generate report:

```bash
navil report --scan-id <SCAN_ID> --format html
```

## 6. API Service (Optional)

```bash
uvicorn navil.api.server:app --host 0.0.0.0 --port 8080 --reload
```

Default local token:

- `local-dev-token`

## 7. Docker Service (Optional)

```bash
docker compose -f docker/docker-compose.yml up --build
```

## 8. Brain Strategy Warmup

```bash
navil brain status
navil brain train --episodes 200
```

## 9. Completion Checklist

- setup script completed without missing packages
- CLI entrypoints resolve from shell
- scope validation passes
- one scan executed in-scope
- one report generated and archived

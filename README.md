# Navil

Navil is an autonomous, scope-enforced application security assessment platform built for authorized testing workflows. It combines crawling, plugin-based vulnerability detection, adaptive strategy learning, exploit-chain modeling, API/CLI interfaces, and production-ready DevOps support.

## Legal Notice

Navil must only be used on systems where you have explicit permission to test.

## Core Capabilities

- Strict scope guardrails from `.navil-scope.yml`
- Async crawler with form/link discovery and technology fingerprinting
- 12 built-in vulnerability detectors
- Adaptive plugin prioritization engine (epsilon-greedy RL-style policy)
- Payload mutation pipeline with corpus + genetic evolution
- Chain analysis for multi-finding attack paths
- Native PyQt6 desktop GUI plus FastAPI API and WebSocket live feed
- Typer + Rich CLI for terminal-first operations
- Structured reporting (JSON, HTML, Markdown, PDF)
- CI/CD workflow, Docker runtime, automated tests
- Optional integrations: Burp export, Nuclei execution, Metasploit check mode

## Architecture Snapshot

```mermaid
flowchart LR
    CLI[CLI] --> Engine[Navil Engine]
    UI[Desktop GUI/API] --> Engine
    Engine --> Scope[Scope Enforcer]
    Engine --> Recon[Recon Crawler]
    Engine --> Scan[Plugin Scanner]
    Engine --> Brain[Adaptive Brain]
    Engine --> Mutator[Payload Mutator]
    Engine --> Chains[Chain Builder]
    Engine --> KB[SQLite + Vector Store]
    Engine --> Report[Report Generator]
```

## Quick Start

1. Install dependencies:

```bash
./scripts/setup.sh
```

The default setup installs packages for your local user with `python3`.
For an isolated environment, run `./scripts/setup.sh --venv`.

2. Create scope file:

```bash
cp .navil-scope.example.yml .navil-scope.yml
```

3. Launch desktop GUI:

```bash
python3 -m navil
```

4. Start API service (optional):

```bash
uvicorn navil.api.server:app --host 0.0.0.0 --port 8080 --reload
```

5. Start a scan with CLI:

```bash
navil scan https://example.com --scope .navil-scope.yml --plugins headers,cors,info_disclosure
```

6. Generate report:

```bash
navil report --scan-id <SCAN_ID> --format html
```

## Desktop GUI

- Primary GUI entrypoint: `python3 -m navil`
- Explicit GUI command: `navil gui` or `navil-gui`
- Explicit CLI mode from module runner: `python3 -m navil --cli --help`

## Testing and QA

```bash
pytest tests/ -v --cov=navil
ruff check navil tests scripts
mypy navil tests scripts
pip-audit
```

### Current QA Snapshot (2026-04-07)

- Tests: `12 passed`
- Coverage: `58%` total
- Lint: `All checks passed`
- Typing: `Success: no issues found in 100 source files`
- Dependency audit: `No known vulnerabilities found`
- Docker: build verified with `docker build -f docker/Dockerfile .`

Detailed QA process is documented in `docs/TESTING.md`.

## Documentation Map

- `docs/README.md`
- `docs/CREATION_GUIDE.md`
- `docs/ARCHITECTURE.md`
- `docs/IMPLEMENTATION.md`
- `docs/TESTING.md`
- `docs/RESEARCH.md`
- `docs/PRODUCT_PLAN.md`
- `docs/API.md`

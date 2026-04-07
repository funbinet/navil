# Creation Guide

## 1. Prerequisites

- Python 3.11+
- Docker (optional, for container deployment)
- GNU Make (optional)

## 2. Repository Setup

```bash
git clone https://github.com/funbinet/navil.git
cd navil
./scripts/setup.sh
cp .navil-scope.example.yml .navil-scope.yml
```

## 3. Scope and Safety Configuration

Edit `.navil-scope.yml` to define:

- allowed domains
- allowed methods
- max depth and request budgets
- required TLS and allowed ports
- optional authentication environment variables

## 4. Run Modes

For a full operational walkthrough, see `docs/RUN_USAGE.md`.

### CLI

```bash
python3 -m navil --help
navil scan https://target.example --scope .navil-scope.yml
```

### API Service (optional)

```bash
uvicorn navil.api.server:app --host 0.0.0.0 --port 8080 --reload
```

### Docker Compose

```bash
docker compose -f docker/docker-compose.yml up --build
```

## 5. Pretraining the Brain

```bash
python3 scripts/train.py --rounds 200 --model models/brain.json
```

## 6. Generate Reports

```bash
navil report --scan-id <SCAN_ID> --format html
navil report --scan-id <SCAN_ID> --format pdf
```

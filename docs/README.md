# Navil Documentation Index

This documentation set is written for operator-first delivery, with strict scope safety and real-system-Python execution.

## Recommended Reading Order

1. CREATION_GUIDE.md: install, bootstrap, and first-run workflow
2. RUN_USAGE.md: end-to-end runtime operations for CLI, menu shell, and API
3. ARCHITECTURE.md: service boundaries, module interactions, and data flow
4. IMPLEMENTATION.md: extension points and internal contracts
5. API.md: endpoint contracts and request/response examples
6. TESTING.md: quality gates, CI expectations, and manual verification
7. RESEARCH.md: design rationale and strategy notes
8. PRODUCT_PLAN.md: roadmap and KPI direction

## Operational Baseline

- Python execution model: system python3 (no virtual environments)
- Installation model: user-site dependencies and editable package install
- Primary interface: navil / navel CLI
- Optional interface: FastAPI + WebSocket

## Fast Links

- Creation Guide: ./CREATION_GUIDE.md
- Run and Usage Guide: ./RUN_USAGE.md
- API Reference: ./API.md
- Testing Guide: ./TESTING.md

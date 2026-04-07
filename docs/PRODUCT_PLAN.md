# Product Plan

## Vision

Build a high-assurance security assessment platform that combines strict scope governance with adaptive detection strategy and practical terminal-first operations.

## Product Principles

- safety before automation
- operator clarity over opaque behavior
- extensibility through stable plugin contracts
- local-first deployability with system Python runtime
- measurable improvement across repeated scan campaigns

## Release Themes

### v0.1 Delivered Foundation

- core scan orchestration and persistence
- scope policy enforcement
- recon and detector plugin architecture
- adaptive reward loop
- CLI + menu shell + API surfaces
- multi-format reporting
- CI and baseline QA workflow

### v0.2 Operational Maturity

- richer scan comparison and trend workflows
- improved auth and secret handling patterns
- expanded adapter layer for external tooling
- stronger report interoperability (security platform ingestion)

### v0.3 Scale and Governance

- distributed execution model
- tenant-aware policy models
- enterprise auth integration patterns
- workflow automation for remediation coordination

## KPI Framework

Primary metrics:

- plugin precision by category
- false-positive ratio trend
- mean time to first high-confidence finding
- average scan completion duration
- findings-to-remediation conversion rate (integrated teams)

Secondary metrics:

- operator interaction efficiency in menu shell
- report generation success rate by format
- adaptive-brain convergence stability

## Quality Objectives

- keep lint/type/test gates green on all releases
- maintain explicit scope controls with zero bypass paths
- preserve deterministic report schema stability across versions

## Roadmap Risks

- overfitting reward updates to narrow target classes
- integration complexity across heterogeneous external tooling
- balancing detection depth against runtime budgets

## Mitigation Tracks

- broaden replay scenarios for adaptive strategy
- maintain strict adapter contracts and isolation boundaries
- track and tune budget/depth defaults with empirical campaign data

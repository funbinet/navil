# Research Notes

This document captures design rationale behind Navil strategy choices and identifies high-value research tracks.

## 1. Problem Statement

Traditional scanners are often static and rule-heavy, which limits adaptation during long-running campaigns. Navil introduces a feedback loop where observed signal quality influences subsequent scan prioritization.

## 2. Core Design Principles

- authorization-first operation
- strict scope controls before active probing
- async execution for practical throughput
- explainable outputs for security teams
- modular detector architecture for incremental evolution

## 3. Adaptive Strategy Rationale

Current adaptive brain uses an epsilon-greedy policy with replay memory rather than heavyweight RL frameworks.

Reasons:

- low operational overhead
- CPU-friendly execution profile
- deterministic enough for audit and reproducibility
- simple parameterization for operator tuning

## 4. Signal Quality Considerations

Reward shaping should reflect:

- finding relevance
- verification confidence
- false-positive reduction
- execution cost sensitivity

Future tuning should include plugin-level precision/recall telemetry as direct reward factors.

## 5. Payload Mutation Strategy

Mutation engine currently blends:

- corpus-driven seeds
- encoding transformations
- crossover and mutation operators

This balances novelty exploration with deterministic fallback payloads suitable for reproducible testing.

## 6. Chain Modeling Rationale

Chain construction provides operator value by linking isolated findings into attack-path narratives.

Research direction:

- stronger relation inference
- confidence scoring for multi-step chains
- evidence-backed chain pruning to suppress weak edges

## 7. Practical Constraints

- must remain lightweight enough for local execution
- must keep outputs auditable for security governance
- must avoid unsafe autonomous behavior outside declared scope policy

## 8. Future Research Tracks

1. contextual model-assisted payload ranking
2. semantic clustering across scan campaigns
3. privacy-preserving strategy transfer between teams
4. remediation recommendation ranking by blast radius and fix cost
5. adaptive depth-budget policies based on early recon density

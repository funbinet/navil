# Research Notes

## Problem Statement

Most scanners are deterministic and static. Navil introduces a feedback loop where scan outcomes influence future scan strategy.

## Design Principles

- Authorization-first operations
- Fast local deployment and portability
- Async-by-default execution model
- Explainable outputs over opaque automation
- Modular plugin architecture for extensibility

## RL Strategy Choice

Instead of heavyweight RL dependencies for initial release, Navil uses an epsilon-greedy adaptive policy with replay memory. This provides low-latency policy adaptation and easier production operation on CPU-only hosts.

## Mutation Strategy

Payload generation combines:

- base corpus
- encoding transformations
- crossover + mutation

This allows discovery-oriented variation with stable deterministic fallbacks.

## Future Research Directions

- contextual LLM-assisted payload ranking
- richer semantic clustering across campaigns
- policy transfer between organizations with privacy-preserving summaries
- automated remediation recommendation ranking by fix cost

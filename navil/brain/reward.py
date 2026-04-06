"""Reward function utilities."""

from __future__ import annotations


def calculate_reward(
    *,
    unique_findings: int,
    suspicious_behaviors: int,
    new_endpoints: int,
    waf_bypasses: int,
    duplicate_findings: int,
    timeouts_or_errors: int,
    out_of_scope_attempts: int,
) -> float:
    return (
        10.0 * unique_findings
        + 5.0 * suspicious_behaviors
        + 3.0 * new_endpoints
        + 1.0 * waf_bypasses
        - 0.5 * duplicate_findings
        - 1.0 * timeouts_or_errors
        - 5.0 * out_of_scope_attempts
    )

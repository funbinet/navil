"""State representation for adaptive strategy learning."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ScanState:
    endpoint_count: int
    avg_response_code: float
    waf_detected: bool
    previous_findings: int
    technology_count: int

    def as_vector(self) -> list[float]:
        return [
            float(self.endpoint_count),
            float(self.avg_response_code),
            1.0 if self.waf_detected else 0.0,
            float(self.previous_findings),
            float(self.technology_count),
        ]

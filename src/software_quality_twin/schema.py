from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class QualityTelemetry:
    version: str
    coverage: float
    complexity: float
    failing_tests: int
    defect_count: int
    change_size: int
    tests_changed: bool


@dataclass(frozen=True)
class QualityState:
    version: str
    quality_score: float
    risk: RiskLevel
    evidence: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class DriftAssessment:
    from_version: str
    to_version: str
    score_delta: float
    degraded: bool
    explanation: str


@dataclass(frozen=True)
class ReleaseForecast:
    version: str
    risk: RiskLevel
    confidence: float
    recommendation: str
    explanation: str

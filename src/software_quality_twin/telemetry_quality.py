from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .schema import QualityTelemetry


_SIGNAL_FIELDS = (
    "coverage",
    "complexity",
    "failing_tests",
    "defect_count",
    "change_size",
    "tests_changed",
)


@dataclass(frozen=True)
class TelemetryQualityReport:
    version: str
    observed_fields: tuple[str, ...]
    imputed_fields: tuple[str, ...]
    completeness: float


def materialize_telemetry(
    record: Mapping[str, object],
    *,
    previous: QualityTelemetry | None = None,
) -> tuple[QualityTelemetry, TelemetryQualityReport]:
    """Build complete telemetry from a possibly incomplete record.

    Missing signals are filled using last-observation-carried-forward when a
    previous version is available. The function refuses to silently invent a
    value when no previous observation exists, keeping imputation explicit and
    auditable for robustness experiments.
    """
    if "version" not in record:
        raise ValueError("telemetry record must include a version")

    version = str(record["version"])
    values: dict[str, object] = {}
    observed: list[str] = []
    imputed: list[str] = []

    for field in _SIGNAL_FIELDS:
        if field in record and record[field] is not None:
            values[field] = record[field]
            observed.append(field)
            continue

        if previous is None:
            raise ValueError(
                f"missing telemetry field '{field}' for {version} and no previous observation is available"
            )

        values[field] = getattr(previous, field)
        imputed.append(field)

    telemetry = QualityTelemetry(
        version=version,
        coverage=float(values["coverage"]),
        complexity=float(values["complexity"]),
        failing_tests=int(values["failing_tests"]),
        defect_count=int(values["defect_count"]),
        change_size=int(values["change_size"]),
        tests_changed=bool(values["tests_changed"]),
    )
    report = TelemetryQualityReport(
        version=version,
        observed_fields=tuple(observed),
        imputed_fields=tuple(imputed),
        completeness=len(observed) / len(_SIGNAL_FIELDS),
    )
    return telemetry, report


def add_numeric_noise(
    telemetry: QualityTelemetry,
    *,
    coverage_delta: float = 0.0,
    complexity_delta: float = 0.0,
    failing_tests_delta: int = 0,
    defect_count_delta: int = 0,
    change_size_delta: int = 0,
) -> QualityTelemetry:
    """Create a deterministic noisy telemetry sample for sensitivity studies."""
    return QualityTelemetry(
        version=telemetry.version,
        coverage=max(0.0, min(100.0, telemetry.coverage + coverage_delta)),
        complexity=max(0.0, telemetry.complexity + complexity_delta),
        failing_tests=max(0, telemetry.failing_tests + failing_tests_delta),
        defect_count=max(0, telemetry.defect_count + defect_count_delta),
        change_size=max(0, telemetry.change_size + change_size_delta),
        tests_changed=telemetry.tests_changed,
    )

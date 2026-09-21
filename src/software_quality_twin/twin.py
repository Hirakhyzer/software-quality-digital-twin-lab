from __future__ import annotations

from .drift import assess_drift
from .forecasting import forecast_release
from .schema import (
    DriftAssessment,
    QualityState,
    QualityTelemetry,
    ReleaseForecast,
    TrendAssessment,
)
from .state_estimator import estimate_quality_state
from .trend import assess_trend


class SoftwareQualityDigitalTwin:
    """Maintains versioned quality states for longitudinal SQA experiments."""

    def __init__(self) -> None:
        self._states: list[QualityState] = []

    @property
    def history(self) -> tuple[QualityState, ...]:
        return tuple(self._states)

    @property
    def current_state(self) -> QualityState | None:
        return self._states[-1] if self._states else None

    def update(self, telemetry: QualityTelemetry) -> QualityState:
        state = estimate_quality_state(telemetry)
        self._states.append(state)
        return state

    def drift(self, threshold: float = 8.0) -> DriftAssessment | None:
        if len(self._states) < 2:
            return None
        return assess_drift(self._states[-2], self._states[-1], threshold=threshold)

    def trend(self, window: int = 4) -> TrendAssessment:
        return assess_trend(self._states, window=window)

    def forecast(self, window: int = 4) -> ReleaseForecast:
        if not self._states:
            raise ValueError("digital twin has no quality state")
        trend = self.trend(window=window)
        return forecast_release(self._states[-1], trend=trend)

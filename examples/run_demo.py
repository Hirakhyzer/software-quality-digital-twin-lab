from software_quality_twin import QualityTelemetry, SoftwareQualityDigitalTwin


def main() -> None:
    twin = SoftwareQualityDigitalTwin()

    versions = [
        QualityTelemetry("1.0.0", 92.0, 8.0, 0, 0, 120, True),
        QualityTelemetry("1.1.0", 81.0, 11.0, 0, 1, 350, True),
        QualityTelemetry("1.2.0", 70.0, 17.0, 2, 3, 850, False),
    ]

    for telemetry in versions:
        state = twin.update(telemetry)
        forecast = twin.forecast()
        print(
            f"{state.version}: score={state.quality_score:.2f}, "
            f"risk={state.risk.value}, recommendation={forecast.recommendation}"
        )
        drift = twin.drift()
        if drift is not None:
            print(f"  drift={drift.score_delta:.2f}, degraded={drift.degraded}")


if __name__ == "__main__":
    main()

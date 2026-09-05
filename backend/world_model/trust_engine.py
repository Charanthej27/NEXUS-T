from typing import Dict


class TrustEngine:
    """
    Dynamic, context-aware source trust with normalized learning.
    """

    def __init__(self):
        self.trust: Dict[str, float] = {
            "CCTV": 0.90,
            "V2X": 0.95,
            "IoT": 0.90,
            "GPS": 0.85,
        }

    def reset(self):
        self.trust = {
            "CCTV": 0.90,
            "V2X": 0.95,
            "IoT": 0.90,
            "GPS": 0.85,
        }

    def apply_context(
        self,
        context: Dict[str, bool],
    ):

        if context.get("rain", False):
            self.trust["CCTV"] *= 0.70

        if context.get("fog", False):
            self.trust["CCTV"] *= 0.75

        if context.get(
            "v2x_packet_loss",
            False,
        ):
            self.trust["V2X"] *= 0.80

        if context.get(
            "iot_failure",
            False,
        ):
            self.trust["IoT"] *= 0.60

        self.trust = {
            source: round(
                max(
                    0.0,
                    min(
                        value,
                        1.0,
                    ),
                ),
                3,
            )
            for source, value
            in self.trust.items()
        }

    def update_from_agreement(
        self,
        source: str,
        predicted: float,
        actual: float,
    ):

        if source not in self.trust:
            self.trust[source] = 0.50

        denominator = max(
            abs(float(predicted)),
            abs(float(actual)),
            1.0,
        )

        relative_error = (
            abs(
                float(predicted)
                - float(actual)
            )
            / denominator
        )

        agreement = max(
            0.0,
            min(
                1.0,
                1.0 - relative_error,
            ),
        )

        old_trust = self.trust[source]

        self.trust[source] = round(
            (
                old_trust * 0.80
            )
            + (
                agreement * 0.20
            ),
            3,
        )

    def get_trust(
        self,
        source: str,
    ) -> float:

        return round(
            self.trust.get(
                source,
                0.50,
            ),
            3,
        )

    def fuse_confidence(
        self,
        observations: Dict[str, float],
    ) -> float:

        if not observations:
            return 0.0

        weighted_sum = 0.0
        trust_sum = 0.0

        for source, confidence in (
            observations.items()
        ):

            trust = self.get_trust(
                source
            )

            weighted_sum += (
                confidence * trust
            )

            trust_sum += trust

        if trust_sum == 0:
            return 0.0

        return round(
            weighted_sum / trust_sum,
            3,
        )

    def snapshot(
        self,
    ) -> Dict[str, float]:

        return dict(self.trust)
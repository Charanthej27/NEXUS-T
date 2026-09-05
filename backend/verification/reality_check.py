from typing import Dict, Any


class RealityChecker:
    """Compare predictions with observed digital-twin simulation outcomes."""

    def verify(
        self,
        predicted: Dict[str, float],
        observed: Dict[str, float],
    ) -> Dict[str, Any]:
        results = {}

        for metric in predicted:
            if metric not in observed:
                continue

            predicted_value = float(predicted[metric])
            observed_value = float(observed[metric])
            error = abs(predicted_value - observed_value)

            if predicted_value == 0:
                accuracy = 1.0 if observed_value == 0 else 0.0
            else:
                accuracy = max(0.0, 1.0 - (error / abs(predicted_value)))

            results[metric] = {
                "predicted": predicted_value,
                "observed": observed_value,
                "error": round(error, 3),
                "accuracy": round(accuracy, 3),
            }

        overall_accuracy = (
            sum(item["accuracy"] for item in results.values()) / len(results)
            if results else 0.0
        )

        return {
            "metrics": results,
            "overall_accuracy": round(overall_accuracy, 3),
            "verified": overall_accuracy >= 0.70,
            "verification_type": "DIGITAL_TWIN_SIMULATION",
        }

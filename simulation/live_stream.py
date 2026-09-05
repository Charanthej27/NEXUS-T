import math
import time
from typing import Dict, Any


class LiveMultimodalStream:
    """
    Scenario-aware deterministic multimodal traffic stream.

    Represents the interface that would receive real CCTV, V2X,
    IoT and GPS telemetry in deployment. For the hackathon,
    values are deterministic and bounded so the demo remains
    reproducible and internally consistent with the selected
    decision scenario.
    """

    PROFILES = {
        "normal": {
            "vehicle_base": 275,
            "connected_base": 40,
            "speed_base": 34.0,
            "queue_base": 95.0,
            "accident": 0.05,
            "emergency": 0.06,
            "pedestrian": 0.12,
            "cctv": 0.90,
            "v2x": 0.95,
            "iot": 0.90,
            "gps": 0.85,
            "world": "STABLE_TRAFFIC",
        },

        "accident": {
            "vehicle_base": 295,
            "connected_base": 52,
            "speed_base": 22.0,
            "queue_base": 155.0,
            "accident": 0.91,
            "emergency": 0.58,
            "pedestrian": 0.24,
            "cctv": 0.91,
            "v2x": 0.96,
            "iot": 0.91,
            "gps": 0.86,
            "world": "INCIDENT_DETECTED",
        },

        "ambulance": {
            "vehicle_base": 285,
            "connected_base": 58,
            "speed_base": 25.0,
            "queue_base": 145.0,
            "accident": 0.28,
            "emergency": 0.92,
            "pedestrian": 0.16,
            "cctv": 0.92,
            "v2x": 0.97,
            "iot": 0.91,
            "gps": 0.87,
            "world": "EMERGENCY_PRIORITY",
        },

        "rain": {
            "vehicle_base": 270,
            "connected_base": 43,
            "speed_base": 24.0,
            "queue_base": 150.0,
            "accident": 0.18,
            "emergency": 0.12,
            "pedestrian": 0.20,
            "cctv": 0.63,
            "v2x": 0.93,
            "iot": 0.91,
            "gps": 0.84,
            "world": "WEATHER_DEGRADED",
        },

        "low_confidence": {
            "vehicle_base": 265,
            "connected_base": 20,
            "speed_base": 20.0,
            "queue_base": 165.0,
            "accident": 0.24,
            "emergency": 0.21,
            "pedestrian": 0.28,
            "cctv": 0.42,
            "v2x": 0.48,
            "iot": 0.36,
            "gps": 0.55,
            "world": "EVIDENCE_DEGRADED",
        },
    }

    def __init__(self):
        self.frame_id = 0

    @staticmethod
    def _clamp(value, low, high):
        return max(low, min(value, high))

    def get_stream(
        self,
        scenario: str = "normal",
    ) -> Dict[str, Any]:

        scenario = (
            scenario
            if scenario in self.PROFILES
            else "normal"
        )

        profile = self.PROFILES[scenario]

        self.frame_id += 1

        wave = math.sin(
            self.frame_id * 0.55
        )

        wave2 = math.cos(
            self.frame_id * 0.31
        )

        vehicles = int(
            self._clamp(
                profile["vehicle_base"]
                + wave * 8
                + wave2 * 5,
                40,
                500,
            )
        )

        connected = int(
            self._clamp(
                profile["connected_base"]
                + wave2 * 4,
                5,
                max(6, vehicles - 5),
            )
        )

        queue = round(
            self._clamp(
                profile["queue_base"]
                + wave * 8
                + wave2 * 4,
                15,
                220,
            ),
            1,
        )

        speed = round(
            self._clamp(
                profile["speed_base"]
                + wave2 * 1.5
                - wave * 0.7,
                8,
                60,
            ),
            1,
        )

        accident = round(
            self._clamp(
                profile["accident"]
                + wave * 0.015,
                0,
                1,
            ),
            3,
        )

        emergency = round(
            self._clamp(
                profile["emergency"]
                + wave2 * 0.015,
                0,
                1,
            ),
            3,
        )

        pedestrian = round(
            self._clamp(
                profile["pedestrian"]
                + wave * 0.012,
                0,
                1,
            ),
            3,
        )

        source_confidence = {
            "CCTV": round(
                self._clamp(
                    profile["cctv"]
                    + wave2 * 0.008,
                    0,
                    1,
                ),
                3,
            ),

            "V2X": round(
                self._clamp(
                    profile["v2x"]
                    + wave * 0.006,
                    0,
                    1,
                ),
                3,
            ),

            "IoT": round(
                self._clamp(
                    profile["iot"]
                    + wave2 * 0.006,
                    0,
                    1,
                ),
                3,
            ),

            "GPS": round(
                self._clamp(
                    profile["gps"]
                    + wave * 0.006,
                    0,
                    1,
                ),
                3,
            ),
        }

        trust = dict(
            source_confidence
        )

        trust_sum = sum(
            trust.values()
        )

        fused_confidence = round(
            (
                sum(
                    source_confidence[source]
                    * trust[source]
                    for source in source_confidence
                )
                / trust_sum
            )
            if trust_sum
            else 0.0,
            3,
        )

        connected_ratio = round(
            connected / vehicles
            if vehicles
            else 0,
            3,
        )

        return {
            "stream": "LIVE_MULTIMODAL",

            "frame_id": self.frame_id,

            "timestamp": time.time(),

            "scenario": scenario,

            "junction": "J2",

            "traffic": {
                "vehicle_count": vehicles,

                "connected_vehicles": connected,

                "non_connected_vehicles": (
                    vehicles - connected
                ),

                "average_speed": speed,

                "queue_length": queue,

                "accident_probability": accident,

                "emergency_probability": emergency,

                "pedestrian_risk": pedestrian,

                "connected_ratio": connected_ratio,
            },

            "sources": {
                "CCTV": {
                    "status": "ACTIVE",
                    "confidence": source_confidence[
                        "CCTV"
                    ],
                    "detected_vehicles": vehicles,
                    "observation": (
                        "Visual traffic perception"
                    ),
                },

                "V2X": {
                    "status": "ACTIVE",
                    "confidence": source_confidence[
                        "V2X"
                    ],
                    "connected_vehicles": connected,
                    "observation": (
                        "Connected vehicle telemetry"
                    ),
                },

                "IoT": {
                    "status": "ACTIVE",
                    "confidence": source_confidence[
                        "IoT"
                    ],
                    "queue_estimate": queue,
                    "observation": (
                        "Roadside sensor measurements"
                    ),
                },

                "GPS": {
                    "status": "ACTIVE",
                    "confidence": source_confidence[
                        "GPS"
                    ],
                    "average_speed": speed,
                    "observation": (
                        "Probe vehicle positioning"
                    ),
                },
            },

            "trust": trust,

            "fused_confidence": fused_confidence,

            "world_model": {
                "state": profile["world"],

                "uncertainty": round(
                    1 - fused_confidence,
                    3,
                ),

                "mixed_traffic": (
                    connected_ratio < 0.50
                ),

                "v2x_coverage": connected_ratio,

                "evidence_quality": (
                    "SUFFICIENT"
                    if fused_confidence >= 0.70
                    else "INSUFFICIENT"
                ),
            },

            "demo_alignment": {
                "scenario_controlled": True,

                "decision_and_live_world_aligned": True,

                "note": (
                    "Scenario-aware deterministic "
                    "telemetry for reproducible "
                    "demonstration."
                ),
            },
        }
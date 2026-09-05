from typing import Dict
from backend.schemas import TrafficState
from backend.world_model.trust_engine import TrustEngine


class BeliefState:
    """Builds a trust-weighted belief from all available sources, including GPS."""

    def __init__(self, trust_engine: TrustEngine):
        self.trust_engine = trust_engine

    def build(
        self,
        junction_id: str,
        observations: Dict[str, float],
        vehicle_count: int,
        queue_length: float,
        average_speed: float,
        accident_probability: float = 0.0,
        emergency_probability: float = 0.0,
        pedestrian_risk: float = 0.0,
    ) -> TrafficState:
        confidence = self.trust_engine.fuse_confidence(observations)

        congestion = min(
            1.0,
            (queue_length / 100.0) * 0.6
            + (1.0 - min(average_speed / 60.0, 1.0)) * 0.4,
        )

        return TrafficState(
            junction_id=junction_id,
            timestamp=__import__("time").time(),
            vehicle_count=vehicle_count,
            queue_length=queue_length,
            average_speed=average_speed,
            congestion=round(congestion, 3),
            accident_probability=accident_probability,
            emergency_probability=emergency_probability,
            pedestrian_risk=pedestrian_risk,
            source_confidence={
                source: self.trust_engine.get_trust(source)
                for source in observations
            },
            connected_vehicles=0,
            total_vehicles=vehicle_count,
        )

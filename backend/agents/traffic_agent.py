from backend.schemas import AgentProposal, Evidence
from backend.world_model.belief_state import BeliefState


class TrafficAgent:

    def propose(self, state) -> AgentProposal:

        if state.congestion >= 0.7:
            action = "EXTEND_GREEN"
            delay_reduction = 0.25
        else:
            action = "OPTIMIZE_SIGNAL"
            delay_reduction = 0.10

        return AgentProposal(
            agent="TrafficAgent",
            action=action,
            target_junction=state.junction_id,
            expected_delay_reduction=delay_reduction,
            emergency_eta_reduction=0.0,
            predicted_risk=0.15,
            confidence=0.88,
            evidence=[
                Evidence(
                    source="CCTV",
                    confidence=state.source_confidence.get("CCTV", 0.5),
                    observation=f"Detected {state.vehicle_count} vehicles with queue length {state.queue_length}",
                ),
                Evidence(
                    source="V2X",
                    confidence=state.source_confidence.get("V2X", 0.5),
                    observation="Connected-vehicle traffic state available",
                ),
            ],
        )
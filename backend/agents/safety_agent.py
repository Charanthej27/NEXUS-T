from backend.schemas import AgentProposal, Evidence


class SafetyAgent:

    def propose(self, state) -> AgentProposal:

        risk = state.pedestrian_risk

        if risk >= 0.7:
            action = "HOLD_SIGNAL_CHANGE"
            predicted_risk = 0.90
            confidence = 0.95
        elif state.accident_probability >= 0.6:
            action = "PROTECT_INCIDENT_ZONE"
            predicted_risk = 0.20
            confidence = 0.91
        else:
            action = "ALLOW_CONTROL_CHANGE"
            predicted_risk = 0.08
            confidence = 0.87

        return AgentProposal(
            agent="SafetyAgent",
            action=action,
            target_junction=state.junction_id,
            expected_delay_reduction=0.0,
            emergency_eta_reduction=0.0,
            predicted_risk=predicted_risk,
            confidence=confidence,
            evidence=[
                Evidence(
                    source="CCTV",
                    confidence=state.source_confidence.get("CCTV", 0.5),
                    observation=f"Pedestrian risk: {state.pedestrian_risk:.2f}",
                ),
                Evidence(
                    source="CCTV",
                    confidence=state.source_confidence.get("CCTV", 0.5),
                    observation=f"Accident probability: {state.accident_probability:.2f}",
                ),
            ],
        )
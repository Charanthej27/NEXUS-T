from backend.schemas import AgentProposal, Evidence


class EmergencyAgent:

    def propose(self, state) -> AgentProposal:

        if state.emergency_probability >= 0.6:
            action = "CREATE_EMERGENCY_CORRIDOR"
            eta_reduction = 0.35
            confidence = 0.92
        else:
            action = "MONITOR_EMERGENCY_ROUTE"
            eta_reduction = 0.05
            confidence = 0.70

        return AgentProposal(
            agent="EmergencyAgent",
            action=action,
            target_junction=state.junction_id,
            expected_delay_reduction=0.0,
            emergency_eta_reduction=eta_reduction,
            predicted_risk=0.10,
            confidence=confidence,
            evidence=[
                Evidence(
                    source="V2X",
                    confidence=state.source_confidence.get("V2X", 0.5),
                    observation=f"Emergency probability: {state.emergency_probability:.2f}",
                )
            ],
        )
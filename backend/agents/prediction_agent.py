from backend.schemas import AgentProposal, Evidence


class PredictionAgent:

    def propose(self, state) -> AgentProposal:

        if state.congestion >= 0.8:
            action = "PREVENT_QUEUE_SPILLOVER"
            delay_reduction = 0.30
            confidence = 0.90

        elif state.congestion >= 0.5:
            action = "BALANCE_UPSTREAM_FLOW"
            delay_reduction = 0.18
            confidence = 0.84

        else:
            action = "MAINTAIN_CURRENT_PLAN"
            delay_reduction = 0.03
            confidence = 0.78

        return AgentProposal(
            agent="PredictionAgent",
            action=action,
            target_junction=state.junction_id,
            expected_delay_reduction=delay_reduction,
            emergency_eta_reduction=0.0,
            predicted_risk=0.12,
            confidence=confidence,
            evidence=[
                Evidence(
                    source="CCTV",
                    confidence=state.source_confidence.get("CCTV", 0.5),
                    observation=f"Current congestion level: {state.congestion:.2f}",
                )
            ],
        )
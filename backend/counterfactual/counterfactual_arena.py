from typing import List, Dict
from backend.schemas import AgentProposal


class CounterfactualArena:

    def evaluate(
        self,
        proposals: List[AgentProposal],
        congestion: float,
        emergency_probability: float,
        pedestrian_risk: float,
    ) -> List[Dict]:

        results = []

        for proposal in proposals:

            benefit = (
                proposal.expected_delay_reduction
                + proposal.emergency_eta_reduction
            )

            risk_penalty = proposal.predicted_risk

            if pedestrian_risk >= 0.7:
                risk_penalty += 0.40

            if emergency_probability >= 0.6:
                if proposal.agent == "EmergencyAgent":
                    benefit += 0.25

            network_score = round(
                (benefit * 0.60)
                + (proposal.confidence * 0.30)
                - (risk_penalty * 0.70),
                3,
            )

            results.append({
                "agent": proposal.agent,
                "action": proposal.action,
                "junction": proposal.target_junction,
                "benefit": round(benefit, 3),
                "predicted_risk": round(risk_penalty, 3),
                "confidence": proposal.confidence,
                "network_score": network_score,
            })

        return sorted(
            results,
            key=lambda x: x["network_score"],
            reverse=True,
        )
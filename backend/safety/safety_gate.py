from typing import Dict

from backend.schemas import Decision


class SafetyGate:
    """
    NEXUS-T Evidence Gate

    An agent proposal can never directly execute an intervention.

    Every proposal must pass:

        1. Hard safety constraint
        2. Confidence requirement
        3. Evidence score
        4. Safety score

    This is the final authorization layer before autonomous action.
    """

    def evaluate(self, candidate: Dict) -> Decision:

        confidence = float(
            candidate.get("confidence", 0.0)
        )

        predicted_risk = float(
            candidate.get("predicted_risk", 1.0)
        )

        benefit = float(
            candidate.get("benefit", 0.0)
        )

        # ----------------------------------------------------
        # NORMALIZE BENEFIT
        # ----------------------------------------------------

        benefit_component = max(
            0.0,
            min(1.0, benefit)
        )

        # ----------------------------------------------------
        # SAFETY COMPONENT
        # ----------------------------------------------------

        safety_component = max(
            0.0,
            min(
                1.0,
                1.0 - predicted_risk
            )
        )

        # ----------------------------------------------------
        # EVIDENCE SCORE
        #
        # Evidence is NOT confidence alone.
        #
        # confidence  = how certain the agents are
        # safety      = how safe the intervention is
        # benefit     = expected network improvement
        #
        # ----------------------------------------------------

        evidence_score = round(
            (
                confidence * 0.45
                +
                safety_component * 0.35
                +
                benefit_component * 0.20
            ),
            3,
        )

        # ----------------------------------------------------
        # HARD SAFETY BLOCK
        #
        # No amount of confidence can override this.
        # ----------------------------------------------------

        if predicted_risk >= 0.70:

            return Decision(
                action=candidate["action"],
                junction=candidate["junction"],
                approved=False,
                confidence=confidence,
                safety_score=round(
                    safety_component,
                    3,
                ),
                evidence_score=evidence_score,
                reason=(
                    "Action rejected by hard safety constraint."
                ),
                rejected_reason=(
                    "Predicted risk exceeds the "
                    "maximum autonomous risk threshold."
                ),
            )

        # ----------------------------------------------------
        # LOW CONFIDENCE BLOCK
        # ----------------------------------------------------

        if confidence < 0.60:

            return Decision(
                action=candidate["action"],
                junction=candidate["junction"],
                approved=False,
                confidence=confidence,
                safety_score=round(
                    safety_component,
                    3,
                ),
                evidence_score=evidence_score,
                reason=(
                    "Insufficient evidence for autonomous execution."
                ),
                rejected_reason=(
                    "Confidence below autonomous execution threshold."
                ),
            )

        # ----------------------------------------------------
        # FINAL SAFETY SCORE
        # ----------------------------------------------------

        safety_score = round(
            (
                confidence * 0.60
                +
                safety_component * 0.40
            ),
            3,
        )

        # ----------------------------------------------------
        # FINAL EVIDENCE GATE
        # ----------------------------------------------------

        approved = (
            evidence_score >= 0.70
            and
            safety_score >= 0.70
        )

        # ----------------------------------------------------
        # APPROVED
        # ----------------------------------------------------

        if approved:

            return Decision(
                action=candidate["action"],
                junction=candidate["junction"],
                approved=True,
                confidence=confidence,
                safety_score=safety_score,
                evidence_score=evidence_score,
                reason=(
                    "Evidence, expected benefit and "
                    "safety constraints passed."
                ),
                rejected_reason=None,
            )

        # ----------------------------------------------------
        # REJECTED BY EVIDENCE GATE
        # ----------------------------------------------------

        return Decision(
            action=candidate["action"],
            junction=candidate["junction"],
            approved=False,
            confidence=confidence,
            safety_score=safety_score,
            evidence_score=evidence_score,
            reason=(
                "Evidence score below autonomous "
                "execution threshold."
            ),
            rejected_reason=(
                "Candidate did not satisfy the "
                "combined evidence and safety gate."
            ),
        )
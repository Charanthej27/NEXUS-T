from typing import Dict, Any, Optional

from backend.world_model.trust_engine import TrustEngine
from backend.world_model.belief_state import BeliefState
from backend.event_graph.event_graph import EventGraph

from backend.agents.traffic_agent import TrafficAgent
from backend.agents.emergency_agent import EmergencyAgent
from backend.agents.safety_agent import SafetyAgent
from backend.agents.prediction_agent import PredictionAgent

from backend.counterfactual.counterfactual_arena import CounterfactualArena
from backend.safety.safety_gate import SafetyGate
from backend.verification.reality_check import RealityChecker


# ============================================================
# NEXUS-T SCENARIOS
# ============================================================

SCENARIOS: Dict[str, Dict[str, Any]] = {

    "normal": {
        "name": "Normal Traffic",
        "description": (
            "Stable traffic conditions with no major incident. "
            "The system optimizes the signal plan."
        ),
        "observations": {
            "CCTV": 0.88,
            "V2X": 0.92,
            "IoT": 0.90,
            "GPS": 0.86,
        },
        "vehicle_count": 72,
        "queue_length": 28,
        "average_speed": 38,
        "accident_probability": 0.05,
        "emergency_probability": 0.08,
        "pedestrian_risk": 0.20,
        "connected_vehicles": 28,
        "context": {
            "rain": False,
            "fog": False,
            "v2x_packet_loss": False,
            "iot_failure": False,
        },
    },

    "accident": {
        "name": "Accident Response",
        "description": (
            "A road accident blocks a lane and creates "
            "rapid queue growth requiring coordinated response."
        ),
        "observations": {
            "CCTV": 0.86,
            "V2X": 0.94,
            "IoT": 0.89,
            "GPS": 0.91,
        },
        "vehicle_count": 110,
        "queue_length": 82,
        "average_speed": 16,
        "accident_probability": 0.91,
        "emergency_probability": 0.86,
        "pedestrian_risk": 0.18,
        "connected_vehicles": 41,
        "context": {
            "rain": False,
            "fog": False,
            "v2x_packet_loss": False,
            "iot_failure": False,
        },
    },

    "ambulance": {
        "name": "Ambulance Priority",
        "description": (
            "A connected emergency vehicle requests priority "
            "while traffic is already congested."
        ),
        "observations": {
            "CCTV": 0.86,
            "V2X": 0.95,
            "IoT": 0.90,
            "GPS": 0.93,
        },
        "vehicle_count": 95,
        "queue_length": 64,
        "average_speed": 21,
        "accident_probability": 0.35,
        "emergency_probability": 0.96,
        "pedestrian_risk": 0.15,
        "connected_vehicles": 37,
        "context": {
            "rain": False,
            "fog": False,
            "v2x_packet_loss": False,
            "iot_failure": False,
        },
    },

    "rain": {
        "name": "Heavy Rain",
        "description": (
            "Heavy rain reduces camera reliability. "
            "The trust engine discounts CCTV evidence before acting."
        ),
        "observations": {
            "CCTV": 0.82,
            "V2X": 0.91,
            "IoT": 0.88,
            "GPS": 0.89,
        },
        "vehicle_count": 105,
        "queue_length": 70,
        "average_speed": 19,
        "accident_probability": 0.42,
        "emergency_probability": 0.35,
        "pedestrian_risk": 0.30,
        "connected_vehicles": 34,
        "context": {
            "rain": True,
            "fog": False,
            "v2x_packet_loss": False,
            "iot_failure": False,
        },
    },

    "low_confidence": {
        "name": "Low Confidence",
        "description": (
            "Conflicting and unreliable observations prevent "
            "safe autonomous intervention."
        ),
        "observations": {
            "CCTV": 0.32,
            "V2X": 0.41,
            "IoT": 0.35,
            "GPS": 0.28,
        },
        "vehicle_count": 88,
        "queue_length": 75,
        "average_speed": 18,
        "accident_probability": 0.68,
        "emergency_probability": 0.72,
        "pedestrian_risk": 0.45,
        "connected_vehicles": 12,
        "context": {
            "rain": False,
            "fog": True,
            "v2x_packet_loss": True,
            "iot_failure": True,
        },
    },
}


# ============================================================
# NEXUS-T ORCHESTRATOR
# ============================================================

class NexusOrchestrator:

    def __init__(self):

        # ----------------------------------------------------
        # WORLD MODEL
        # ----------------------------------------------------

        self.trust = TrustEngine()
        self.belief = BeliefState(self.trust)

        # ----------------------------------------------------
        # MULTI-AGENT LAYER
        # ----------------------------------------------------

        self.traffic_agent = TrafficAgent()
        self.emergency_agent = EmergencyAgent()
        self.safety_agent = SafetyAgent()
        self.prediction_agent = PredictionAgent()

        # ----------------------------------------------------
        # DECISION LAYERS
        # ----------------------------------------------------

        self.arena = CounterfactualArena()
        self.safety_gate = SafetyGate()
        self.reality_checker = RealityChecker()

    # ========================================================
    # AUTONOMY MODE
    # ========================================================

    def determine_autonomy_mode(self, decision):

        if not decision:
            return "RECOMMENDATION_ONLY"

        if not decision.approved:
            return "RECOMMENDATION_ONLY"

        if (
            decision.confidence >= 0.85
            and decision.safety_score >= 0.85
            and decision.evidence_score >= 0.80
        ):
            return "AUTONOMOUS"

        if (
            decision.confidence >= 0.70
            and decision.safety_score >= 0.70
            and decision.evidence_score >= 0.70
        ):
            return "LIMITED_AUTONOMY"

        return "RECOMMENDATION_ONLY"

    # ========================================================
    # EVENT GRAPH
    # ========================================================

    def build_event_graph(
        self,
        state,
        scenario_key: str,
    ):

        graph = EventGraph()

        incident_type = (
            "ACCIDENT"
            if state.accident_probability >= 0.50
            else "TRAFFIC_STATE"
        )

        graph.add_event(
            "E1",
            incident_type,
            {
                "probability": state.accident_probability,
                "junction": state.junction_id,
                "scenario": scenario_key,
            },
        )

        graph.add_event(
            "E2",
            "LANE_BLOCKAGE",
            {
                "severity": round(
                    min(
                        1.0,
                        state.accident_probability
                        * 0.95
                    ),
                    3,
                ),
            },
        )

        graph.add_event(
            "E3",
            "QUEUE_BUILDUP",
            {
                "queue_length": state.queue_length,
                "congestion": state.congestion,
            },
        )

        graph.add_event(
            "E4",
            "EMERGENCY_RESPONSE",
            {
                "probability": state.emergency_probability,
            },
        )

        graph.add_event(
            "E5",
            "NETWORK_RISK",
            {
                "pedestrian_risk": state.pedestrian_risk,
                "congestion": state.congestion,
            },
        )

        graph.connect(
            "E1",
            "E2",
            "causes",
        )

        graph.connect(
            "E2",
            "E3",
            "causes",
        )

        graph.connect(
            "E3",
            "E4",
            "threatens",
        )

        graph.connect(
            "E4",
            "E5",
            "increases",
        )

        return graph

    # ========================================================
    # REALITY CHECK
    # ========================================================

    def build_reality_values(
        self,
        selected_action: Optional[str],
        state,
    ):

        if selected_action == "CREATE_EMERGENCY_CORRIDOR":

            predicted = {
                "queue": 50,
                "speed": 30,
            }

            observed = {
                "queue": 45,
                "speed": 32,
            }

        elif selected_action == "EXTEND_GREEN":

            predicted = {
                "queue": 58,
                "speed": 25,
            }

            observed = {
                "queue": 55,
                "speed": 27,
            }

        elif selected_action == "PREVENT_QUEUE_SPILLOVER":

            predicted = {
                "queue": 52,
                "speed": 28,
            }

            observed = {
                "queue": 50,
                "speed": 29,
            }

        elif selected_action == "BALANCE_UPSTREAM_FLOW":

            predicted = {
                "queue": 58,
                "speed": 25,
            }

            observed = {
                "queue": 55,
                "speed": 27,
            }

        elif selected_action == "OPTIMIZE_SIGNAL":

            predicted = {
                "queue": 24,
                "speed": 41,
            }

            observed = {
                "queue": 22,
                "speed": 40,
            }

        else:

            predicted = {
                "queue": state.queue_length,
                "speed": state.average_speed,
            }

            observed = {
                "queue": state.queue_length,
                "speed": state.average_speed,
            }

        return predicted, observed

    # ========================================================
    # MAIN PIPELINE
    # ========================================================

    def run(
        self,
        scenario: str = "accident",
    ):

        scenario_key = scenario.lower().strip()

        if scenario_key not in SCENARIOS:
            scenario_key = "accident"

        config = SCENARIOS[scenario_key]

        # ----------------------------------------------------
        # 1. APPLY ENVIRONMENTAL CONTEXT
        # ----------------------------------------------------

        self.trust.apply_context(
            config["context"]
        )

        context_trust = dict(
            self.trust.trust
        )

        # ----------------------------------------------------
        # 2. BUILD BELIEF STATE
        # ----------------------------------------------------

        state = self.belief.build(
            junction_id="J2",
            observations=config["observations"],
            vehicle_count=config["vehicle_count"],
            queue_length=config["queue_length"],
            average_speed=config["average_speed"],
            accident_probability=config[
                "accident_probability"
            ],
            emergency_probability=config[
                "emergency_probability"
            ],
            pedestrian_risk=config[
                "pedestrian_risk"
            ],
        )

        # Connected/non-connected traffic representation
        state.connected_vehicles = config[
            "connected_vehicles"
        ]

        state.total_vehicles = config[
            "vehicle_count"
        ]

        # Use current context-adjusted trust
        state.source_confidence = {
            source: self.trust.get_trust(source)
            for source in config["observations"]
        }

        # ----------------------------------------------------
        # 3. BUILD EVENT GRAPH
        # ----------------------------------------------------

        graph = self.build_event_graph(
            state,
            scenario_key,
        )

        # ----------------------------------------------------
        # 4. MULTI-AGENT PROPOSALS
        # ----------------------------------------------------

        proposals = [
            self.traffic_agent.propose(state),
            self.emergency_agent.propose(state),
            self.safety_agent.propose(state),
            self.prediction_agent.propose(state),
        ]

        # ----------------------------------------------------
        # 5. CONFIDENCE ADAPTATION
        #
        # Agent confidence cannot exceed the confidence
        # of the world model that supports it.
        #
        # This is critical for the Evidence-Gated concept.
        # ----------------------------------------------------

        fused_confidence = self.trust.fuse_confidence(
            config["observations"]
        )

        for proposal in proposals:

            proposal.confidence = round(
                min(
                    proposal.confidence,
                    fused_confidence,
                ),
                3,
            )

        # ----------------------------------------------------
        # 6. COUNTERFACTUAL ARENA
        # ----------------------------------------------------

        candidates = self.arena.evaluate(
            proposals=proposals,
            congestion=state.congestion,
            emergency_probability=(
                state.emergency_probability
            ),
            pedestrian_risk=state.pedestrian_risk,
        )

        # ----------------------------------------------------
        # 7. EVIDENCE / SAFETY GATE
        # ----------------------------------------------------

        decisions = [
            self.safety_gate.evaluate(candidate)
            for candidate in candidates
        ]

        # ----------------------------------------------------
        # 8. SELECT ONLY APPROVED ACTIONS
        # ----------------------------------------------------

        approved = [
            decision
            for decision in decisions
            if decision.approved
        ]

        selected = (
            approved[0]
            if approved
            else None
        )

        # ----------------------------------------------------
        # 9. DETERMINE AUTONOMY
        # ----------------------------------------------------

        autonomy_mode = (
            self.determine_autonomy_mode(
                selected
            )
        )

        # ----------------------------------------------------
        # 10. REALITY VERIFICATION
        # ----------------------------------------------------

        selected_action = (
            selected.action
            if selected
            else None
        )

        predicted, observed = (
            self.build_reality_values(
                selected_action,
                state,
            )
        )

        verification = (
            self.reality_checker.verify(
                predicted,
                observed,
            )
        )

        # ----------------------------------------------------
        # 11. POST-ACTION TRUST LEARNING
        # ----------------------------------------------------

        before_learning = dict(
            self.trust.trust
        )

        self.trust.update_from_agreement(
            "CCTV",
            predicted["queue"],
            observed["queue"],
        )

        self.trust.update_from_agreement(
            "V2X",
            predicted["speed"],
            observed["speed"],
        )

        after_learning = dict(
            self.trust.trust
        )

        # ----------------------------------------------------
        # 12. DECISION SUMMARY
        # ----------------------------------------------------

        if selected:

            decision_summary = (
                f"{selected.action} selected at "
                f"{selected.junction}. "
                f"Evidence score: "
                f"{selected.evidence_score:.0%}. "
                f"Confidence: "
                f"{selected.confidence:.0%}. "
                f"Safety score: "
                f"{selected.safety_score:.0%}. "
                f"Autonomy mode: "
                f"{autonomy_mode}."
            )

        else:

            top_evidence = (
                decisions[0].evidence_score
                if decisions
                else 0.0
            )

            decision_summary = (
                "No action passed the evidence and "
                "safety gates. "
                f"Top candidate evidence score: "
                f"{top_evidence:.0%}. "
                "System remains in "
                "recommendation-only mode."
            )

        # ----------------------------------------------------
        # 13. SYSTEM STATUS
        # ----------------------------------------------------

        status = (
            "AUTONOMOUS_ACTION_SELECTED"
            if selected
            else "SAFE_RECOMMENDATION_ONLY"
        )

        # ----------------------------------------------------
        # 14. EVENT CHAIN
        #
        # Keep the causal order deterministic for the UI.
        # ----------------------------------------------------

        accident_chain = []

        for event_id in [
            "E1",
            "E2",
            "E3",
            "E4",
            "E5",
        ]:

            if event_id in graph.graph:

                accident_chain.append({
                    "event_id": event_id,
                    **graph.graph.nodes[event_id],
                })

        # ----------------------------------------------------
        # 15. FINAL RESPONSE
        # ----------------------------------------------------

        return {
            "system": "NEXUS-T",

            "status": status,

            "scenario": scenario_key,

            "scenario_name": config["name"],

            "scenario_description": (
                config["description"]
            ),

            "state": state.model_dump(),

            "fused_confidence": fused_confidence,

            "trust": {
                "before_learning": before_learning,
                "after_learning": after_learning,
                "context": config["context"],
            },

            "event_graph": {
                "summary": graph.summary(),
                "accident_chain": accident_chain,
            },

            "proposals": [
                proposal.model_dump()
                for proposal in proposals
            ],

            "counterfactual_results": candidates,

            "decisions": [
                decision.model_dump()
                for decision in decisions
            ],

            "selected_action": (
                selected.model_dump()
                if selected
                else None
            ),

            "autonomy_mode": autonomy_mode,

            "verification": verification,

            "decision_summary": decision_summary,

            "demo_note": (
                "NEXUS-T evaluates evidence, safety and "
                "network impact before allowing autonomous "
                "intervention."
            ),
        }

    # ========================================================
    # COMPATIBILITY ALIAS
    # ========================================================

    def run_scenario(
        self,
        scenario: str,
    ):

        return self.run(scenario)

    # ========================================================
    # ALL-SCENARIO TEST
    # ========================================================

    def run_all_scenarios(self):

        results = {}

        for scenario_key in SCENARIOS:

            results[scenario_key] = self.run(
                scenario_key
            )

        return results


# ============================================================
# TERMINAL DEMO
# ============================================================

if __name__ == "__main__":

    system = NexusOrchestrator()

    print()
    print("=" * 70)
    print("                         NEXUS-T")
    print(
        " Network-wide Explainable Autonomous "
        "Traffic Safety Orchestration"
    )
    print("=" * 70)

    for scenario_key in SCENARIOS:

        result = system.run(
            scenario_key
        )

        print()
        print("-" * 70)
        print(
            f"SCENARIO: "
            f"{result['scenario_name'].upper()}"
        )

        print(
            f"STATUS: "
            f"{result['status']}"
        )

        if result["selected_action"]:

            selected = result[
                "selected_action"
            ]

            print(
                f"ACTION: "
                f"{selected['action']}"
            )

            print(
                f"EVIDENCE: "
                f"{selected['evidence_score']:.0%}"
            )

            print(
                f"SAFETY: "
                f"{selected['safety_score']:.0%}"
            )

        else:

            print("ACTION: NONE")
            print("EVIDENCE: BLOCKED")
            print("SAFETY: BLOCKED")

        print(
            f"AUTONOMY: "
            f"{result['autonomy_mode']}"
        )

    print()
    print("=" * 70)
    print("                    NEXUS-T LOOP COMPLETE")
    print("=" * 70)
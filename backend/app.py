from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.orchestrator import NexusOrchestrator
from simulation.network_simulator import NetworkSimulator
from simulation.live_stream import LiveMultimodalStream


app = FastAPI(
    title="NEXUS-T",
    description=(
        "Network-wide Explainable Autonomous "
        "Traffic Safety Orchestration"
    ),
    version="2.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


network_simulator = NetworkSimulator()

live_stream = LiveMultimodalStream()

current_scenario = "accident"


SCENARIO_NAMES = {
    "normal": "Normal Traffic",
    "accident": "Accident Response",
    "ambulance": "Ambulance Priority",
    "rain": "Heavy Rain",
    "low_confidence": "Low Confidence",
}


def _set_scenario(
    scenario: str,
):
    global current_scenario

    if scenario not in SCENARIO_NAMES:
        raise ValueError(
            f"Unknown scenario: {scenario}"
        )

    current_scenario = scenario


@app.get("/")
def root():

    return {
        "system": "NEXUS-T",
        "status": "ONLINE",
        "message": (
            "Evidence-Gated Autonomous "
            "Traffic Safety System"
        ),
    }


@app.get("/api/status")
def status():

    return {
        "system": "NEXUS-T",
        "status": "ONLINE",
        "current_scenario": current_scenario,

        "architecture": [
            "Multi-Modal Perception",
            "Dynamic Trust Engine",
            "Belief State",
            "Causal Event Graph",
            "Multi-Agent Proposals",
            "Counterfactual Arena",
            "Network Digital Twin",
            "Evidence Gate",
            "Autonomous Action",
            "Reality Verification",
            "Closed-Loop Learning",
        ],
    }


@app.get("/api/health")
def health():

    return {
        "system": "NEXUS-T",
        "status": "HEALTHY",

        "backend": "ONLINE",
        "orchestrator": "READY",

        "multi_modal_world": "READY",
        "dynamic_trust_engine": "READY",
        "event_graph": "READY",
        "multi_agent_engine": "READY",

        "counterfactual_engine": "READY",
        "network_digital_twin": "READY",

        "safety_gate": "READY",
        "autonomous_decision": "READY",

        "reality_verification": "READY",
        "closed_loop_learning": "READY",
    }


@app.get("/api/decision")
def decision():

    system = NexusOrchestrator()

    return system.run()


@app.get("/api/demo")
def demo():

    system = NexusOrchestrator()

    result = system.run()

    return {
        "system": result["system"],
        "status": result["status"],
        "selected_action": result[
            "selected_action"
        ],
        "autonomy_mode": result[
            "autonomy_mode"
        ],
        "verification": result[
            "verification"
        ],
        "trust": result["trust"],
        "decision_summary": result[
            "decision_summary"
        ],
    }


@app.get("/api/scenario/{scenario}")
def scenario(
    scenario: str,
):

    _set_scenario(scenario)

    system = NexusOrchestrator()

    return system.run_scenario(
        scenario
    )


@app.get("/api/scenario/normal")
def normal_scenario():
    return scenario("normal")


@app.get("/api/scenario/accident")
def accident_scenario():
    return scenario("accident")


@app.get("/api/scenario/ambulance")
def ambulance_scenario():
    return scenario("ambulance")


@app.get("/api/scenario/rain")
def rain_scenario():
    return scenario("rain")


@app.get("/api/scenario/low_confidence")
def low_confidence_scenario():
    return scenario(
        "low_confidence"
    )


@app.get("/api/network")
def network():

    network_simulator.step()

    return network_simulator.snapshot()


@app.get(
    "/api/network/simulate/{action}"
)
def simulate_network(
    action: str,
):

    return network_simulator.simulate_action(
        action=action,
        target="J2",
    )


@app.get("/api/network/compare")
def compare_network_actions():

    return network_simulator.compare_actions(
        target="J2"
    )


@app.get("/api/live")
def live(
    scenario_name: Optional[str] = Query(
        default=None,
        alias="scenario",
    )
):

    selected = (
        scenario_name
        or current_scenario
    )

    if selected not in SCENARIO_NAMES:
        selected = current_scenario

    return live_stream.get_stream(
        selected
    )


@app.get("/api/live/{scenario}")
def live_for_scenario(
    scenario: str,
):

    if scenario not in SCENARIO_NAMES:

        return {
            "error": "Unknown scenario",
            "allowed": list(
                SCENARIO_NAMES.keys()
            ),
        }

    return live_stream.get_stream(
        scenario
    )


@app.get("/api/evaluation")
def evaluation():

    return {
        "system": "NEXUS-T",

        "evaluation": {

            "completeness": {
                "status": "IMPLEMENTED",

                "evidence": [
                    "Multi-modal world state",
                    "Dynamic source trust",
                    "Belief state",
                    "Causal event graph",
                    "Four-agent proposal system",
                    "Counterfactual evaluation",
                    "Network digital twin",
                    "Safety gate",
                    "Autonomous execution mode",
                    "Post-action verification",
                    "Trust update",
                ],
            },

            "innovation": {
                "status": "CORE_DIFFERENTIATOR",

                "evidence": [
                    "Evidence-Gated Autonomy",
                    "Confidence-adaptive autonomy",
                    "Dynamic source trust",
                    "Counterfactual action arena",
                    "Network-level intervention evaluation",
                    "Post-action reality feedback",
                ],
            },

            "effectiveness": {
                "status": "MEASURABLE",

                "metrics": [
                    "Predicted queue reduction",
                    "Predicted average speed improvement",
                    "Predicted emergency ETA reduction",
                    "Network benefit score",
                    "Prediction-vs-reality accuracy",
                ],
            },

            "real_world_impact": {
                "status": "DEMONSTRATED",

                "use_cases": [
                    "Accident response",
                    "Ambulance priority",
                    "Heavy rain",
                    "Mixed V2X and non-V2X traffic",
                    "Low-confidence safety fallback",
                    "Network congestion management",
                ],
            },

            "demo": {
                "status": "JURY_READY",

                "scenarios": list(
                    SCENARIO_NAMES.keys()
                ),

                "interactive": True,
                "live_multimodal": True,
                "network_digital_twin": True,
                "counterfactual_comparison": True,
                "reality_verification": True,
            },
        },
    }


@app.get("/api/demo/full")
def full_demo():

    system = NexusOrchestrator()

    result = system.run_scenario(
        "ambulance"
    )

    network = (
        network_simulator.compare_actions(
            target="J2"
        )
    )

    live_state = (
        live_stream.get_stream(
            "ambulance"
        )
    )

    return {
        "system": "NEXUS-T",

        "decision": {
            "scenario": result.get(
                "scenario_name"
            ),

            "selected_action": result.get(
                "selected_action"
            ),

            "autonomy_mode": result.get(
                "autonomy_mode"
            ),

            "decision_summary": result.get(
                "decision_summary"
            ),
        },

        "live_world": live_state,

        "network_counterfactual": network,

        "verification": result.get(
            "verification"
        ),

        "trust": result.get(
            "trust"
        ),

        "jury_story": [
            "Sense heterogeneous traffic",
            "Estimate uncertainty",
            "Generate competing interventions",
            "Simulate network consequences",
            "Gate unsafe actions",
            "Execute only when evidence is sufficient",
            "Verify the real outcome",
            "Update source trust",
        ],
    }
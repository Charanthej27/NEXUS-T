import math
import time
from typing import Dict, Any


class NetworkSimulator:
    """
    NEXUS-T Network Digital Twin.

    Simulates traffic propagation across a small connected
    junction network and evaluates candidate interventions
    before execution.

    The simulator is intentionally deterministic and bounded
    so the jury demo remains reproducible and realistic.
    """

    ACTIONS = [
        "CREATE_EMERGENCY_CORRIDOR",
        "EXTEND_GREEN",
        "BALANCE_UPSTREAM_FLOW",
        "OPTIMIZE_SIGNAL",
        "NO_CHANGE",
    ]

    def __init__(self):
        self.tick = 0

        self.junctions = {
            "J1": {
                "vehicles": 58,
                "queue": 22.0,
                "speed": 36.0,
                "signal": "NORMAL",
            },
            "J2": {
                "vehicles": 95,
                "queue": 64.0,
                "speed": 21.0,
                "signal": "NORMAL",
            },
            "J3": {
                "vehicles": 71,
                "queue": 39.0,
                "speed": 31.0,
                "signal": "NORMAL",
            },
            "J4": {
                "vehicles": 46,
                "queue": 18.0,
                "speed": 40.0,
                "signal": "NORMAL",
            },
        }

        self.connections = {
            "J1": ["J2"],
            "J2": ["J1", "J3", "J4"],
            "J3": ["J2"],
            "J4": ["J2"],
        }

    # =====================================================
    # HELPERS
    # =====================================================

    @staticmethod
    def _clamp(value, minimum, maximum):
        return max(minimum, min(value, maximum))

    def sync_scenario(self, scenario: str) -> Dict[str, Any]:
        """Synchronize the digital twin with the orchestrator scenario."""
        profiles = {
            "normal": {"vehicles": 72, "queue": 28.0, "speed": 38.0},
            "accident": {"vehicles": 110, "queue": 82.0, "speed": 16.0},
            "ambulance": {"vehicles": 95, "queue": 64.0, "speed": 21.0},
            "rain": {"vehicles": 105, "queue": 70.0, "speed": 19.0},
            "low_confidence": {"vehicles": 88, "queue": 75.0, "speed": 18.0},
        }
        profile = profiles.get(scenario.lower().strip(), profiles["accident"])

        self.junctions["J2"].update({
            "vehicles": profile["vehicles"],
            "queue": profile["queue"],
            "speed": profile["speed"],
            "signal": "NORMAL",
        })
        self.junctions["J1"].update({
            "vehicles": int(profile["vehicles"] * 0.61),
            "queue": round(profile["queue"] * 0.52, 1),
            "speed": round(min(60.0, profile["speed"] + 15.0), 1),
            "signal": "NORMAL",
        })
        self.junctions["J3"].update({
            "vehicles": int(profile["vehicles"] * 0.75),
            "queue": round(profile["queue"] * 0.58, 1),
            "speed": round(min(60.0, profile["speed"] + 10.0), 1),
            "signal": "NORMAL",
        })
        self.junctions["J4"].update({
            "vehicles": int(profile["vehicles"] * 0.48),
            "queue": round(profile["queue"] * 0.34, 1),
            "speed": round(min(60.0, profile["speed"] + 19.0), 1),
            "signal": "NORMAL",
        })
        return self.snapshot()

    def _network_metrics(
        self,
        junctions: Dict[str, Dict[str, Any]],
    ) -> Dict[str, float]:

        total_vehicles = sum(
            item["vehicles"]
            for item in junctions.values()
        )

        total_queue = sum(
            item["queue"]
            for item in junctions.values()
        )

        average_speed = (
            sum(
                item["speed"]
                for item in junctions.values()
            )
            / len(junctions)
        )

        return {
            "total_vehicles": total_vehicles,
            "total_queue": round(total_queue, 2),
            "average_speed": round(average_speed, 2),
        }

    # =====================================================
    # LIVE DIGITAL TWIN
    # =====================================================

    def snapshot(self) -> Dict[str, Any]:

        metrics = self._network_metrics(
            self.junctions
        )

        return {
            "tick": self.tick,
            "timestamp": time.time(),

            "junctions": self.junctions,

            "connections": self.connections,

            "network": metrics,

            "digital_twin": {
                "mode": "LIVE_SIMULATION",
                "junction_count": len(self.junctions),
                "network_connected": True,
                "deterministic_demo": True,
            },
        }

    def step(self) -> Dict[str, Any]:

        self.tick += 1

        # Bounded deterministic traffic variation.
        # This prevents the demo from drifting into
        # physically implausible states.

        for index, junction_id in enumerate(
            self.junctions
        ):

            junction = self.junctions[junction_id]

            wave = math.sin(
                (self.tick * 0.55)
                + index
            )

            demand_wave = math.cos(
                (self.tick * 0.35)
                + index
            )

            vehicle_delta = round(
                wave * 2.0
                + demand_wave * 1.5
            )

            queue_delta = round(
                wave * 2.2
                + demand_wave * 1.4,
                1,
            )

            speed_delta = round(
                demand_wave * 0.8
                - wave * 0.4,
                1,
            )

            junction["vehicles"] = int(
                self._clamp(
                    junction["vehicles"]
                    + vehicle_delta,
                    20,
                    180,
                )
            )

            junction["queue"] = round(
                self._clamp(
                    junction["queue"]
                    + queue_delta,
                    5,
                    140,
                ),
                1,
            )

            junction["speed"] = round(
                self._clamp(
                    junction["speed"]
                    + speed_delta,
                    8,
                    60,
                ),
                1,
            )

        return self.snapshot()

    # =====================================================
    # COUNTERFACTUAL ACTION SIMULATION
    # =====================================================

    def simulate_action(
        self,
        action: str,
        target: str = "J2",
    ) -> Dict[str, Any]:

        if action not in self.ACTIONS:
            return {
                "error": "Unsupported action",
                "allowed_actions": self.ACTIONS,
            }

        if target not in self.junctions:
            return {
                "error": "Unknown target junction",
                "target": target,
            }

        before = self.snapshot()

        simulated_junctions = {
            key: dict(value)
            for key, value
            in self.junctions.items()
        }

        target_state = simulated_junctions[target]

        # -------------------------------------------------
        # EMERGENCY CORRIDOR
        # -------------------------------------------------

        if action == "CREATE_EMERGENCY_CORRIDOR":

            target_state["queue"] = max(
                0,
                target_state["queue"] - 18,
            )

            target_state["speed"] = min(
                60,
                target_state["speed"] + 9,
            )

            target_state["signal"] = (
                "EMERGENCY_PRIORITY"
            )

            for node in self.connections.get(
                target,
                [],
            ):
                simulated_junctions[node]["queue"] = round(
                    max(
                        0,
                        simulated_junctions[node]["queue"]
                        - 4,
                    ),
                    1,
                )

        # -------------------------------------------------
        # EXTEND GREEN
        # -------------------------------------------------

        elif action == "EXTEND_GREEN":

            target_state["queue"] = max(
                0,
                target_state["queue"] - 12,
            )

            target_state["speed"] = min(
                60,
                target_state["speed"] + 6,
            )

            target_state["signal"] = (
                "GREEN_EXTENDED"
            )

        # -------------------------------------------------
        # BALANCE UPSTREAM FLOW
        # -------------------------------------------------

        elif action == "BALANCE_UPSTREAM_FLOW":

            target_state["queue"] = max(
                0,
                target_state["queue"] - 10,
            )

            target_state["speed"] = min(
                60,
                target_state["speed"] + 5,
            )

            target_state["signal"] = (
                "FLOW_BALANCED"
            )

            for node in self.connections.get(
                target,
                [],
            ):
                simulated_junctions[node]["queue"] = round(
                    max(
                        0,
                        simulated_junctions[node]["queue"]
                        - 2,
                    ),
                    1,
                )

        # -------------------------------------------------
        # OPTIMIZE SIGNAL
        # -------------------------------------------------

        elif action == "OPTIMIZE_SIGNAL":

            target_state["queue"] = max(
                0,
                target_state["queue"] - 7,
            )

            target_state["speed"] = min(
                60,
                target_state["speed"] + 3,
            )

            target_state["signal"] = (
                "SIGNAL_OPTIMIZED"
            )

        # -------------------------------------------------
        # NO CHANGE
        # -------------------------------------------------

        else:

            target_state["signal"] = "NO_CHANGE"

        after_metrics = self._network_metrics(
            simulated_junctions
        )

        before_queue = (
            before["network"]["total_queue"]
        )

        before_speed = (
            before["network"]["average_speed"]
        )

        after_queue = (
            after_metrics["total_queue"]
        )

        after_speed = (
            after_metrics["average_speed"]
        )

        queue_reduction = max(
            0,
            before_queue - after_queue,
        )

        speed_gain = max(
            0,
            after_speed - before_speed,
        )

        queue_reduction_percent = (
            queue_reduction / before_queue
            if before_queue > 0
            else 0
        )

        # Estimated emergency response benefit.
        emergency_eta_reduction = {
            "CREATE_EMERGENCY_CORRIDOR": 0.35,
            "EXTEND_GREEN": 0.15,
            "BALANCE_UPSTREAM_FLOW": 0.10,
            "OPTIMIZE_SIGNAL": 0.05,
            "NO_CHANGE": 0.0,
        }[action]

        network_benefit = round(
            (
                queue_reduction_percent
                * 0.45
            )
            + (
                speed_gain / 60.0
                * 0.30
            )
            + (
                emergency_eta_reduction
                * 0.25
            ),
            3,
        )

        return {
            "action": action,
            "target": target,

            "before": before["network"],

            "after": {
                **after_metrics,
            },

            "queue_reduction": round(
                queue_reduction,
                2,
            ),

            "queue_reduction_percent": round(
                queue_reduction_percent,
                3,
            ),

            "speed_gain": round(
                speed_gain,
                2,
            ),

            "emergency_eta_reduction": round(
                emergency_eta_reduction,
                3,
            ),

            "network_benefit": network_benefit,

            "impact": {
                "queue": (
                    f"{before_queue:.1f}m → "
                    f"{after_queue:.1f}m"
                ),
                "speed": (
                    f"{before_speed:.1f} → "
                    f"{after_speed:.1f} km/h"
                ),
                "queue_reduction": (
                    f"{queue_reduction:.1f}m"
                ),
                "speed_gain": (
                    f"+{speed_gain:.1f} km/h"
                ),
                "emergency_eta": (
                    f"{emergency_eta_reduction * 100:.0f}%"
                ),
            },

            "simulated": True,
        }

    # =====================================================
    # COMPARE ALL ACTIONS
    # =====================================================

    def compare_actions(
        self,
        target: str = "J2",
    ) -> Dict[str, Any]:

        simulations = [
            self.simulate_action(
                action,
                target,
            )
            for action in self.ACTIONS
        ]

        ranked = sorted(
            simulations,
            key=lambda item: (
                item["network_benefit"]
            ),
            reverse=True,
        )

        return {
            "target": target,
            "candidates": ranked,
            "best_action": (
                ranked[0]["action"]
                if ranked
                else None
            ),
            "comparison_complete": True,
        }
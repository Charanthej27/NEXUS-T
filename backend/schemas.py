from pydantic import BaseModel, Field
from typing import Dict, List, Optional


# ============================================================
# TRAFFIC BELIEF STATE
# ============================================================

class TrafficState(BaseModel):

    junction_id: str

    timestamp: float

    vehicle_count: int = 0

    queue_length: float = 0.0

    average_speed: float = 0.0

    congestion: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
    )

    accident_probability: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
    )

    emergency_probability: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
    )

    pedestrian_risk: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
    )

    source_confidence: Dict[str, float] = {}

    connected_vehicles: int = 0

    total_vehicles: int = 0


# ============================================================
# EVIDENCE
# ============================================================

class Evidence(BaseModel):

    source: str

    confidence: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
    )

    observation: str


# ============================================================
# AGENT PROPOSAL
# ============================================================

class AgentProposal(BaseModel):

    agent: str

    action: str

    target_junction: str

    expected_delay_reduction: float = 0.0

    emergency_eta_reduction: float = 0.0

    predicted_risk: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
    )

    confidence: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
    )

    evidence: List[Evidence] = []


# ============================================================
# FINAL SAFETY / EVIDENCE DECISION
# ============================================================

class Decision(BaseModel):

    action: str

    junction: str

    approved: bool

    confidence: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
    )

    safety_score: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
    )

    # NEXUS-T NOVELTY LAYER
    # Measures whether evidence is sufficient
    # for autonomous intervention.
    evidence_score: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
    )

    reason: str

    rejected_reason: Optional[str] = None


# ============================================================
# COUNTERFACTUAL RESULT
# ============================================================

class CounterfactualResult(BaseModel):

    agent: str

    action: str

    junction: str

    benefit: float = 0.0

    predicted_risk: float = 0.0

    confidence: float = 0.0

    network_score: float = 0.0


# ============================================================
# REALITY CHECK
# ============================================================

class RealityMetric(BaseModel):

    predicted: float

    actual: float

    error: float

    accuracy: float


class RealityVerification(BaseModel):

    metrics: Dict[str, RealityMetric]

    overall_accuracy: float

    verified: bool
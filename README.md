# NEXUS-T

## Network-wide Explainable Autonomous Traffic Safety Orchestration

### SH-SVA-01 — Autonomous Traffic Flow Optimization & Road-Safety Response Agents (V2X + Multi-Modal Signals)

NEXUS-T is a software prototype for autonomous traffic-flow optimization and road-safety response using multi-modal traffic observations, multi-agent decision making, counterfactual evaluation, safety verification and post-action validation.

---

## 1. Problem Statement

SH-SVA-01 requires autonomous systems capable of:

1. Optimizing traffic flow across a traffic network.
2. Responding to road-safety incidents using V2X and multi-modal signals.

NEXUS-T addresses both requirements through a unified decision pipeline.

---

## 2. Solution

NEXUS-T combines:

- CCTV / computer vision
- V2X observations
- IoT observations
- GPS information
- Dynamic source trust
- Traffic belief-state modeling
- Causal event graphs
- Multi-agent decision making
- Counterfactual evaluation
- Safety and evidence gating
- Autonomous intervention
- Post-action verification

### Core Principle

> Detection should not directly trigger autonomous intervention. The available evidence and predicted consequences should first be evaluated for safety.

---

## 3. Core Architecture

```text
CCTV / Vision + V2X + IoT + GPS
              |
              v
       Perception Layer
              |
              v
       Belief + Trust Engine
              |
              v
          Event Graph
              |
              v
        Multi-Agent Layer
              |
              v
     Counterfactual Evaluation
              |
              v
          Safety Gate
              |
              v
        Autonomous Action
              |
              v
      Post-Action Verification
              |
              v
          Trust Update
4. Traffic Flow Optimization

For autonomous traffic-flow optimization:

Traffic Observations
        |
        v
Traffic State
        |
        v
Agent Proposals
        |
        v
Candidate Actions
        |
        v
Counterfactual Evaluation
        |
        v
Network Impact + Risk
        |
        v
Safety Gate
        |
        v
Best Safe Action

The system evaluates competing traffic-control interventions before executing an action.

5. Road-Safety Response

For road-safety response:

Incident Detection
        |
        v
CCTV + V2X + IoT + GPS Evidence
        |
        v
Trust-Weighted Belief State
        |
        v
Event Graph
        |
        v
Road-Safety / Emergency Agents
        |
        v
Candidate Response
        |
        v
Counterfactual Evaluation
        |
        v
Safety / Evidence Gate
        |
        v
Autonomous Response
Example Event Relationship
Accident
   |
   v
Lane Blockage
   |
   v
Queue Formation
   |
   v
Emergency Requirement
   |
   v
Network Risk
6. Multi-Modal Inputs

NEXUS-T is designed to combine multiple traffic information sources.

CCTV / Computer Vision

Provides vehicle detections, classes, positions and traffic-state observations.

V2X

Provides connected-vehicle information such as emergency-vehicle or traffic-state observations.

IoT

Provides roadside sensor observations.

GPS

Provides mobility and position-related observations.

The current prototype represents V2X, IoT and GPS inputs through software interfaces/simulation.

7. Dynamic Source Trust

NEXUS-T does not assume that all information sources have equal reliability.

The Trust Engine maintains source-specific trust values and adjusts them according to contextual conditions.

Example
Rain
 |
 v
Reduced CCTV reliability
 |
 v
Lower CCTV contribution
 |
 v
Updated traffic belief

Similarly, V2X packet loss or IoT failure can reduce the corresponding source trust.

Post-action verification can also provide feedback for trust updating.

8. Belief State

The Belief State creates a unified representation of the traffic environment from available observations.

The traffic state can include:

Vehicle count
Queue length
Average speed
Congestion
Accident probability
Emergency probability
Pedestrian risk
Source confidence
Connected vehicle information
9. Multi-Agent Decision Layer

NEXUS-T uses specialized agents to generate intervention proposals.

The prototype includes agent modules for:

Traffic optimization
Emergency response
Safety response
Prediction

Each proposal can contain:

Proposed action
Target junction
Expected delay reduction
Emergency ETA reduction
Predicted risk
Confidence
Supporting evidence

The agents propose actions; the common evaluation and safety layers determine whether an action is suitable for execution.

10. Counterfactual Evaluation

Before executing a candidate intervention, NEXUS-T evaluates its predicted consequences.

Example

Current Situation:

Accident at J2 + lane blockage + approaching ambulance

Candidate A:

Extend green at J2

Candidate B:

Prioritize ambulance route and coordinate downstream signals

Candidate C:

Maintain current signal plan

                    Evaluate Each Candidate
                             |
          +------------------+------------------+
          |                  |                  |
          v                  v                  v
   Network Impact       Traffic Delay     Emergency Benefit
          |                  |                  |
          +------------------+------------------+
                             |
                    Predicted Risk
                             |
                       Confidence
                             |
                          Safety
                             |
                             v
                  Select Best Safe Candidate

This allows the system to evaluate possible consequences before committing to an intervention.

11. Safety / Evidence Gate

The safety gate prevents unsupported or unsafe autonomous intervention.

The proposed action is evaluated using factors including:

Evidence confidence
Source trust
Predicted risk
Safety score
Network impact
Decision confidence

If the required conditions are not satisfied:

Candidate Action
       |
       v
Safety / Evidence Gate
       |
      FAIL
       |
       v
Autonomous Execution Blocked
       |
       v
Restricted / Safer Decision Mode

The system is therefore designed to fail conservatively rather than force an uncertain autonomous action.

12. Post-Action Verification

After an intervention, NEXUS-T compares predicted and observed outcomes in the digital-twin environment.

Predicted Outcome
        |
        | compare
        v
Observed Digital-Twin Outcome
        |
        v
Verification
        |
        v
Source Trust Update

This creates a closed feedback loop rather than ending the system process immediately after execution.

13. AI / ML
Vehicle Detection

NEXUS-T uses a YOLO11-based vehicle detection model.

Vehicle Classes
Two-wheelers
Auto
Car
Vehicle Truck
Bus
Tractor
Bicycle
Tempo
Concrete Mixer
Truck Tanker
Accident Classification

An accident/normal classification model is used as an incident evidence source.

Classes
Accident
Normal
14. Dataset
Vehicle Detection Dataset

The vehicle dataset contains the following 10 categories:

Two-wheelers
Auto
Car
Vehicle Truck
Bus
Tractor
Bicycle
Tempo
Concrete Mixer
Truck Tanker
Accident Dataset

Used for accident-versus-normal classification.

Traffic Frames

Traffic frames are used for perception and traffic-state extraction.

15. Recorded Vehicle Detection Training

The recorded YOLO training configuration includes:

Parameter	Value
Model	YOLO11n
Training epochs	100
Batch size	8
Image size	640
Pretrained model	Yes
Training environment	CPU
Recorded Model Metrics
mAP@50: approximately 0.405
mAP@50–95: approximately 0.293

These are model-level training results and should not be interpreted as real-world traffic-system performance.

16. Technology Stack
Frontend
React
Vite
JavaScript
Lucide React
Backend
Python
FastAPI
Pydantic
AI / ML
YOLO11
Ultralytics
Computer Vision
Vehicle Detection
Vehicle Tracking
Accident Classification
Data / Processing
NumPy
Pandas
Graph Processing
NetworkX
Communication
MQTT
Hardware Interface
ESP32
Simulation
Network Digital Twin
Counterfactual Action Evaluation
17. Backend Architecture
backend/
│
├── agents/
│   ├── emergency_agent.py
│   ├── prediction_agent.py
│   ├── safety_agent.py
│   └── traffic_agent.py
│
├── counterfactual/
│   └── counterfactual_arena.py
│
├── event_graph/
│   └── event_graph.py
│
├── safety/
│   └── safety_gate.py
│
├── verification/
│   └── reality_check.py
│
├── world_model/
│   ├── belief_state.py
│   └── trust_engine.py
│
├── app.py
├── orchestrator.py
└── schemas.py
18. Implementation Responsibilities
Perception

Converts traffic frames into traffic observations.

World Model

Builds the traffic belief state and manages source trust.

Event Graph

Represents relationships between traffic incidents and their consequences.

Agents

Generate specialized intervention proposals.

Counterfactual

Evaluates candidate interventions before execution.

Safety

Verifies whether an intervention satisfies safety/evidence conditions.

Orchestrator

Coordinates the decision pipeline.

Verification

Compares predicted and observed digital-twin outcomes.

19. Prototype Scenarios

The prototype supports controlled scenarios including:

Normal Traffic

Baseline traffic-state processing.

Accident

Incident detection and road-safety response.

Ambulance

Emergency-vehicle information and priority response.

Heavy Rain

Context-dependent reduction in CCTV trust.

Low Confidence

Demonstrates conservative behavior when evidence is insufficient.

20. What the Team Developed

The project uses existing technologies and models as building blocks.

Existing Technologies Used
YOLO11 / Ultralytics
FastAPI
React / Vite
NetworkX
NumPy
Pandas
MQTT
ESP32
Team-Developed Components

The team designed and implemented the decision-orchestration layer including:

Dynamic source-trust logic
Trust-weighted belief-state construction
Causal event-graph workflow
Multi-agent proposal architecture
Counterfactual candidate evaluation workflow
Safety/evidence gating
Autonomous decision orchestration
Post-action verification
Trust-update mechanism
Integration of the complete perception-to-decision pipeline
21. Prototype Status

NEXUS-T is a working software prototype demonstrated through a digital-twin environment.

Implemented capabilities include:

Vehicle perception
Traffic-state construction
Dynamic source trust
Belief-state processing
Event-graph reasoning
Multi-agent proposals
Counterfactual evaluation
Safety/evidence gating
Autonomous decision orchestration
Post-action verification
22. Experimental Scenarios

The system has been tested using controlled software scenarios:

NORMAL
ACCIDENT
AMBULANCE
HEAVY RAIN
LOW CONFIDENCE

The scenarios test different parts of the decision architecture, including:

Traffic optimization
Incident response
Emergency priority
Sensor-confidence adaptation
Conservative autonomy
23. Real-World Deployment Considerations

The architecture is designed to interface with:

Connected Vehicles
        |
       V2X
        |
       RSU
        |
        v
     NEXUS-T
        |
        v
Traffic Controller
        |
        v
Traffic Signals

A production deployment would require:

Certified V2X OBUs and RSUs
Live roadside data
Production traffic-controller integration
Cybersecurity validation
Safety validation
Controlled field testing
Regulatory and infrastructure integration

The current prototype is a software and digital-twin validation and is not claimed as a live-city deployment.

24. Current Limitations
Physical V2X infrastructure is not deployed in the current prototype.
V2X, IoT and GPS inputs are represented through software interfaces/simulation.
The traffic controller interface is a prototype interface rather than a certified production controller.
Digital-twin observations are not equivalent to real-world field ground truth.
The vehicle dataset is relatively small.
Formal real-world traffic-delay improvement has not been measured.
Formal real-world emergency-response improvement has not been measured.
Production-scale multi-junction field validation remains future work.
25. Future Development
Integrate certified V2X OBU/RSU infrastructure.
Connect live CCTV and IoT streams.
Integrate production-grade traffic controllers.
Deploy latency-sensitive components at the edge.
Expand the digital twin to larger traffic networks.
Perform controlled real-world intersection pilots.
Use verified field outcomes for continuous system improvement.
26. Team
Charan Thej

Department: CSE-AIML

Contribution: Idea, system architecture and backend

Ankitha

Department: CSE-AIML

Contribution: Dashboard and frontend

Sreeleka

Department: CSE-AIML

Contribution: Research and evaluation

A. Vennela

Department: ECE

Contribution: Prototype development

S. V. Sai Jaswanth

Department: ECE

Contribution: Hardware implementation

Faculty Mentor

Priyanka Jaroli

27. Core Technical Contribution

The central design principle of NEXUS-T is:

MULTI-MODAL EVIDENCE
        ↓
DYNAMIC TRUST
        ↓
BELIEF STATE
        ↓
MULTI-AGENT PROPOSALS
        ↓
COUNTERFACTUAL EVALUATION
        ↓
SAFETY / EVIDENCE GATE
        ↓
AUTONOMOUS INTERVENTION
        ↓
POST-ACTION VERIFICATION

NEXUS-T therefore focuses on evidence-gated autonomous intervention rather than direct detection-to-action control.

28. Disclaimer

NEXUS-T is a hackathon research and engineering prototype.

The current demonstration validates the software decision architecture using controlled scenarios and digital-twin simulation.

It does not claim live-city deployment, production C-V2X operation, certified traffic-controller integration, or real-world traffic performance improvements.

Project Status

NEXUS-T — Network-wide Explainable Autonomous Traffic Safety Orchestration

The implementation is intended for demonstration, experimentation, and further research and development.
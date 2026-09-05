import { useEffect, useState } from "react";

import {
  Activity,
  AlertTriangle,
  Brain,
  Car,
  CheckCircle2,
  ChevronRight,
  CloudRain,
  Gauge,
  GitBranch,
  Network,
  Radio,
  ShieldCheck,
  Siren,
  Target,
  TrendingUp,
  Wifi,
  XCircle,
} from "lucide-react";

import "./App.css";

const API_BASE = "http://127.0.0.1:8000/api";

const SCENARIOS = [
  { id: "normal", label: "NORMAL", icon: Activity },
  { id: "accident", label: "ACCIDENT", icon: AlertTriangle },
  { id: "ambulance", label: "AMBULANCE", icon: Siren },
  { id: "rain", label: "HEAVY RAIN", icon: CloudRain },
  { id: "low_confidence", label: "LOW CONFIDENCE", icon: ShieldCheck },
];

const ACTION_LABELS = {
  CREATE_EMERGENCY_CORRIDOR: "CREATE EMERGENCY CORRIDOR",
  EXTEND_GREEN: "EXTEND GREEN",
  BALANCE_UPSTREAM_FLOW: "BALANCE UPSTREAM FLOW",
  OPTIMIZE_SIGNAL: "OPTIMIZE SIGNAL",
  NO_CHANGE: "NO CHANGE",
};

function App() {
  const [data, setData] = useState(null);
  const [liveData, setLiveData] = useState(null);
  const [networkData, setNetworkData] = useState(null);
  const [networkCompare, setNetworkCompare] = useState(null);
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedScenario, setSelectedScenario] = useState("accident");
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchScenario = async (scenario) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        `${API_BASE}/scenario/${scenario}`
      );

      if (!response.ok) {
        throw new Error(
          `Backend returned ${response.status}`
        );
      }

      const result = await response.json();

      setData(result);
      setLastUpdated(new Date());
    } catch (err) {
      console.error(err);
      setError(
        "Unable to connect to NEXUS-T backend."
      );
    } finally {
      setLoading(false);
    }
  };

  const refreshWorld = async () => {
    try {
      const [
        liveResponse,
        networkResponse,
        compareResponse,
        healthResponse,
      ] = await Promise.all([
        fetch(
          `${API_BASE}/live?scenario=${selectedScenario}`
        ),
        fetch(`${API_BASE}/network`),
        fetch(`${API_BASE}/network/compare`),
        fetch(`${API_BASE}/health`),
      ]);

      if (
        !liveResponse.ok ||
        !networkResponse.ok ||
        !compareResponse.ok ||
        !healthResponse.ok
      ) {
        throw new Error(
          "Live system unavailable"
        );
      }

      const [
        live,
        network,
        compare,
        health,
      ] = await Promise.all([
        liveResponse.json(),
        networkResponse.json(),
        compareResponse.json(),
        healthResponse.json(),
      ]);

      setLiveData(live);
      setNetworkData(network);
      setNetworkCompare(compare);
      setHealthData(health);
    } catch (err) {
      console.error(err);

      setError(
        "Decision engine is online; live telemetry is temporarily unavailable."
      );
    }
  };

  useEffect(() => {
    fetchScenario(selectedScenario);
  }, [selectedScenario]);

  useEffect(() => {
    let mounted = true;

    const run = async () => {
      if (!mounted) {
        return;
      }

      await refreshWorld();
    };

    run();

    const interval = setInterval(
      run,
      3000
    );

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [selectedScenario]);

  /*
   * IMPORTANT:
   * All hooks are above this point.
   *
   * Do NOT add hooks below either conditional return.
   * This prevents React's:
   * "Rendered more hooks than during the previous render"
   * error.
   */

  if (loading && !data) {
    return (
      <div className="loading-screen">
        <Brain size={48} />

        <h1>NEXUS-T</h1>

        <p>
          Initializing autonomous traffic
          intelligence...
        </p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="loading-screen">
        <AlertTriangle size={48} />

        <h1>Backend Offline</h1>

        <p>
          Start the NEXUS-T FastAPI server
          on port 8000.
        </p>

        <button
          onClick={() =>
            fetchScenario(
              selectedScenario
            )
          }
        >
          Retry Connection
        </button>
      </div>
    );
  }

  const state = data.state || {};

  const action =
    data.selected_action;

  const verification =
    data.verification || {
      metrics: {},
      overall_accuracy: 0,
    };

  const trust =
    data.trust?.after_learning ||
    data.trust?.before_learning ||
    {};

  const candidates =
    data.counterfactual_results ||
    [];

  const decisions =
    data.decisions || [];

  const isBlocked =
    data.autonomy_mode ===
    "RECOMMENDATION_ONLY";

  const topDecision =
    decisions.length
      ? decisions[0]
      : null;

  const evidenceScore =
    action?.evidence_score ??
    topDecision?.evidence_score ??
    0;

  const healthReady =
    healthData?.status ===
    "HEALTHY";

  const liveTraffic =
    liveData?.traffic || {};

  const liveSources =
    liveData?.sources || {};

  const liveTrust =
    liveData?.trust || {};

  const liveWorld =
    liveData?.world_model || {};

  const network =
    networkData?.network || {};

  const networkJunctions =
    networkData?.junctions || {};

  /*
   * FIX:
   *
   * Previously this was a useMemo() placed after
   * conditional returns. That caused React Hook order
   * violations.
   *
   * It is now a normal calculation.
   */
  const selectedImpact =
    action &&
    networkCompare?.candidates
      ? networkCompare.candidates.find(
          (item) =>
            item.action ===
            action.action
        ) || null
      : null;

  const bestNetworkAction =
    networkCompare?.best_action ||
    null;

  const liveConfidence =
    liveData?.fused_confidence ??
    0;

  return (
    <div className="app">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <header className="header">

        <div className="brand">

          <div className="brand-icon">
            <Brain size={27} />
          </div>

          <div>
            <h1>NEXUS-T</h1>

            <span>
              Explainable Autonomous
              Traffic Safety
            </span>
          </div>

        </div>

        <div className="header-right">

          <div className="live-status">

            <span className="pulse"></span>

            {healthReady
              ? "SYSTEM HEALTHY"
              : "SYSTEM ONLINE"}

          </div>

          <div className="junction">

            <Target size={17} />

            JUNCTION{" "}
            {state.junction_id ||
              "J2"}

          </div>

        </div>

      </header>


      <main className="main">

        {/* =====================================================
            SCENARIO CONTROL
        ===================================================== */}

        <section className="scenario-panel">

          <div className="scenario-heading">

            <div>

              <div className="eyebrow">

                <Activity size={15} />

                LIVE SCENARIO CONTROL

              </div>

              <h3>
                Test NEXUS-T
                decision intelligence
              </h3>

              <p>
                Change the world state and
                watch evidence, agents,
                safety and autonomy respond.
              </p>

            </div>

            <div className="scenario-current">

              <span>
                ACTIVE SCENARIO
              </span>

              <strong>
                {data.scenario_name}
              </strong>

            </div>

          </div>


          <div className="scenario-buttons">

            {SCENARIOS.map(
              (scenario) => {

                const Icon =
                  scenario.icon;

                return (
                  <button
                    key={
                      scenario.id
                    }
                    className={`scenario-button ${
                      selectedScenario ===
                      scenario.id
                        ? "active"
                        : ""
                    }`}
                    onClick={() =>
                      setSelectedScenario(
                        scenario.id
                      )
                    }
                  >

                    <Icon size={17} />

                    {
                      scenario.label
                    }

                  </button>
                );
              }
            )}

          </div>


          {error && (
            <div className="error-banner">

              <AlertTriangle
                size={16}
              />

              {error}

            </div>
          )}

        </section>


        {/* =====================================================
            HERO
        ===================================================== */}

        <section className="hero">

          <div>

            <div className="eyebrow">

              <ShieldCheck
                size={15}
              />

              EVIDENCE-GATED AUTONOMY

            </div>

            <h2>
              Traffic decisions that{" "}
              <span>
                prove they are safe.
              </span>
            </h2>

            <p>
              NEXUS-T fuses CCTV, V2X and
              IoT evidence, evaluates
              competing interventions,
              and executes only actions
              that pass the safety gate.
            </p>

            <div className="scenario-description">

              <strong>
                {data.scenario_name}
              </strong>

              <span>
                {
                  data.scenario_description
                }
              </span>

            </div>

          </div>


          <div className="hero-action">

            <div className="action-label">

              {isBlocked
                ? "AUTONOMY BLOCKED"
                : "AUTONOMOUS ACTION"}

            </div>

            <div
              className={`action-title ${
                isBlocked
                  ? "blocked-action"
                  : ""
              }`}
            >

              {isBlocked ? (
                <ShieldCheck
                  size={25}
                />
              ) : (
                <Siren size={25} />
              )}

              {action
                ? ACTION_LABELS[
                    action.action
                  ] ||
                  action.action.replaceAll(
                    "_",
                    " "
                  )
                : "NO AUTONOMOUS ACTION"}

            </div>

            <div className="action-meta">

              <span>

                {isBlocked ? (
                  <XCircle
                    size={15}
                  />
                ) : (
                  <CheckCircle2
                    size={15}
                  />
                )}

                {data.autonomy_mode}

              </span>

              <span>
                {Math.round(
                  (
                    action?.confidence ||
                    topDecision?.confidence ||
                    0
                  ) * 100
                )}
                % confidence
              </span>

            </div>

          </div>

        </section>


        {/* =====================================================
            LIVE MULTIMODAL WORLD
        ===================================================== */}

        <section
          className="panel"
          style={{
            marginTop: 18,
          }}
        >

          <PanelTitle
            icon={<Radio />}
            title="Live Multimodal World"
            subtitle="CCTV + V2X + IoT + GPS fused into one scenario-aligned world state"
          />


          <div className="live-grid">

            <LiveStat
              label="TOTAL VEHICLES"
              value={
                liveTraffic.vehicle_count ??
                "—"
              }
              detail="Live perception"
              icon={<Car size={18} />}
            />

            <LiveStat
              label="CONNECTED V2X"
              value={
                liveTraffic.connected_vehicles ??
                "—"
              }
              detail={`${Math.round(
                (
                  liveTraffic.connected_ratio ||
                  0
                ) * 100
              )}% coverage`}
              icon={<Wifi size={18} />}
            />

            <LiveStat
              label="NON-CONNECTED"
              value={
                liveTraffic.non_connected_vehicles ??
                "—"
              }
              detail="Inferred / visual"
              icon={<Car size={18} />}
            />

            <LiveStat
              label="FUSED CONFIDENCE"
              value={`${Math.round(
                liveConfidence * 100
              )}%`}
              detail={`${Math.round(
                (1 - liveConfidence) *
                  100
              )}% uncertainty`}
              icon={
                <ShieldCheck
                  size={18}
                />
              }
            />

          </div>


          <div className="live-lower-grid">

            <div className="live-metric-grid">

              <LiveMetric
                label="QUEUE"
                value={`${Number(
                  liveTraffic.queue_length ||
                    0
                ).toFixed(1)} m`}
              />

              <LiveMetric
                label="AVG SPEED"
                value={`${Number(
                  liveTraffic.average_speed ||
                    0
                ).toFixed(1)} km/h`}
              />

              <LiveMetric
                label="ACCIDENT RISK"
                value={`${Math.round(
                  (
                    liveTraffic.accident_probability ||
                    0
                  ) * 100
                )}%`}
              />

              <LiveMetric
                label="EMERGENCY"
                value={`${Math.round(
                  (
                    liveTraffic.emergency_probability ||
                    0
                  ) * 100
                )}%`}
              />

              <LiveMetric
                label="PEDESTRIAN RISK"
                value={`${Math.round(
                  (
                    liveTraffic.pedestrian_risk ||
                    0
                  ) * 100
                )}%`}
              />

              <LiveMetric
                label="V2X COVERAGE"
                value={`${Math.round(
                  (
                    liveWorld.v2x_coverage ||
                    0
                  ) * 100
                )}%`}
              />

            </div>


            <div className="source-trust-card">

              <div className="trust-card-heading">

                <strong>
                  SOURCE TRUST
                </strong>

                <span>
                  {liveWorld.state ||
                    "LIVE"}
                </span>

              </div>

              {Object.keys({
                CCTV: 1,
                V2X: 1,
                IoT: 1,
                GPS: 1,
              }).map(
                (source) => (
                  <SourceTrust
                    key={source}
                    name={source}
                    value={
                      liveTrust[
                        source
                      ] ??
                      liveSources[
                        source
                      ]?.confidence ??
                      0
                    }
                  />
                )
              )}

            </div>

          </div>


          <div className="live-footer-row">

            <div className="context-badge">

              <Activity
                size={15}
              />

              WORLD STATE:{" "}
              {liveWorld.state ||
                "INITIALIZING"}

            </div>

            <span>
              FRAME #
              {liveData?.frame_id ??
                "—"}{" "}
              ·{" "}
              {liveData?.scenario?.toUpperCase() ||
                selectedScenario.toUpperCase()}{" "}
              · J2
            </span>

          </div>

        </section>


        {/* =====================================================
            NETWORK DIGITAL TWIN
        ===================================================== */}

        <section className="panel">

          <PanelTitle
            icon={<Network />}
            title="Network Digital Twin"
            subtitle="Predict network-level consequences before execution"
          />


          <div className="live-grid three">

            <LiveStat
              label="NETWORK VEHICLES"
              value={
                network.total_vehicles ??
                "—"
              }
              detail="J1 → J4"
              icon={<Car size={18} />}
            />

            <LiveStat
              label="NETWORK QUEUE"
              value={
                network.total_queue !=
                null
                  ? `${Number(
                      network.total_queue
                    ).toFixed(1)} m`
                  : "—"
              }
              detail="Aggregated"
              icon={
                <Gauge size={18} />
              }
            />

            <LiveStat
              label="NETWORK SPEED"
              value={
                network.average_speed !=
                null
                  ? `${Number(
                      network.average_speed
                    ).toFixed(1)} km/h`
                  : "—"
              }
              detail={`Digital twin tick ${
                networkData?.tick ??
                "—"
              }`}
              icon={
                <TrendingUp
                  size={18}
                />
              }
            />

          </div>


          <div className="junction-grid">

            {Object.entries(
              networkJunctions
            ).map(
              ([junction, item]) => (
                <div
                  className="junction-card"
                  key={junction}
                >

                  <div className="junction-card-top">

                    <strong>
                      {junction}
                    </strong>

                    <span>
                      {item.signal ||
                        "NORMAL"}
                    </span>

                  </div>

                  <div>
                    {item.vehicles ??
                      "—"}{" "}
                    vehicles
                  </div>

                  <div>
                    {item.queue !=
                    null
                      ? Number(
                          item.queue
                        ).toFixed(1)
                      : "—"}{" "}
                    m queue
                  </div>

                  <div>
                    {item.speed !=
                    null
                      ? Number(
                          item.speed
                        ).toFixed(1)
                      : "—"}{" "}
                    km/h
                  </div>

                </div>
              )
            )}

          </div>

        </section>


        {/* =====================================================
            PREDICTED NETWORK IMPACT
        ===================================================== */}

        <section className="panel impact-panel">

          <PanelTitle
            icon={
              <TrendingUp />
            }
            title="Predicted Network Impact"
            subtitle="Counterfactual result for the selected intervention — not a real-world deployment measurement"
          />


          {selectedImpact ? (

            <div className="impact-grid">

              <ImpactCard
                label="QUEUE"
                value={
                  selectedImpact
                    .impact?.queue ||
                  "—"
                }
                detail={`${(
                  selectedImpact.queue_reduction_percent *
                  100
                ).toFixed(1)}% predicted reduction`}
              />

              <ImpactCard
                label="AVG SPEED"
                value={
                  selectedImpact
                    .impact?.speed ||
                  "—"
                }
                detail={
                  selectedImpact
                    .impact?.speed_gain ||
                  "No gain"
                }
              />

              <ImpactCard
                label="EMERGENCY ETA"
                value={
                  selectedImpact
                    .impact
                    ?.emergency_eta ||
                  "0%"
                }
                detail="Predicted response improvement"
              />

              <ImpactCard
                label="NETWORK BENEFIT"
                value={
                  selectedImpact.network_benefit !=
                  null
                    ? selectedImpact.network_benefit.toFixed(
                        3
                      )
                    : "0.000"
                }
                detail="Digital-twin score"
              />

            </div>

          ) : (

            <div className="blocked-note">

              No autonomous intervention
              selected. Network impact
              remains advisory.

            </div>

          )}


          <div className="impact-verdict">

            <div>

              <small>
                SELECTED ACTION
              </small>

              <strong>
                {action
                  ? ACTION_LABELS[
                      action.action
                    ] ||
                    action.action
                  : "NONE"}
              </strong>

            </div>


            <div>

              <small>
                BEST NETWORK ACTION
              </small>

              <strong>
                {bestNetworkAction
                  ? ACTION_LABELS[
                      bestNetworkAction
                    ] ||
                    bestNetworkAction
                  : "—"}
              </strong>

            </div>


            <div>

              <small>
                SIMULATION STATUS
              </small>

              <strong>
                {bestNetworkAction ===
                action?.action
                  ? "BEST MATCH"
                  : "SAFETY-GATED"}
              </strong>

            </div>

          </div>

        </section>


        {/* =====================================================
            METRICS
        ===================================================== */}

        <section className="metrics-grid">

          <MetricCard
            icon={<Car />}
            label="Vehicles"
            value={
              state.vehicle_count ??
              "—"
            }
            detail="Decision-world traffic"
          />

          <MetricCard
            icon={<Gauge />}
            label="Congestion"
            value={`${Math.round(
              (state.congestion ||
                0) * 100
            )}%`}
            detail={`${state.queue_length ??
              0}m queue`}
          />

          <MetricCard
            icon={
              <AlertTriangle />
            }
            label="Accident Risk"
            value={`${Math.round(
              (
                state.accident_probability ||
                0
              ) * 100
            )}%`}
            detail="Incident probability"
            danger
          />

          <MetricCard
            icon={<Siren />}
            label="Emergency"
            value={`${Math.round(
              (
                state.emergency_probability ||
                0
              ) * 100
            )}%`}
            detail="Response priority"
          />

          <MetricCard
            icon={
              <ShieldCheck />
            }
            label="Safety Score"
            value={
              action
                ? `${Math.round(
                    action.safety_score *
                      100
                  )}%`
                : "BLOCKED"
            }
            detail="Evidence gate"
          />

        </section>


        {/* =====================================================
            EVENT GRAPH + TRUST
        ===================================================== */}

        <section className="content-grid">

          <div className="panel">

            <PanelTitle
              icon={<GitBranch />}
              title="Causal Event Graph"
              subtitle="Why the system intervened"
            />


            <div className="event-chain">

              <EventNode
                icon={
                  <AlertTriangle />
                }
                title="ACCIDENT"
                detail={`${Math.round(
                  (
                    state.accident_probability ||
                    0
                  ) * 100
                )}% probability`}
              />

              <ChevronRight
                className="arrow"
              />

              <EventNode
                icon={<Activity />}
                title="LANE BLOCKAGE"
                detail={
                  (
                    state.accident_probability ||
                    0
                  ) >= 0.6
                    ? "High severity"
                    : "Medium severity"
                }
              />

              <ChevronRight
                className="arrow"
              />

              <EventNode
                icon={<Car />}
                title="QUEUE BUILDUP"
                detail={`${state.vehicle_count ??
                  0} vehicles`}
              />

              <ChevronRight
                className="arrow"
              />

              <EventNode
                icon={<Siren />}
                title="EMERGENCY"
                detail={`${Math.round(
                  (
                    state.emergency_probability ||
                    0
                  ) * 100
                )}% priority`}
              />

            </div>

          </div>


          <div className="panel">

            <PanelTitle
              icon={<Wifi />}
              title="Dynamic Source Trust"
              subtitle="Context-aware evidence reliability"
            />


            <div className="trust-list">

              {Object.entries(
                trust
              ).map(
                ([source, value]) => (
                  <SourceTrust
                    key={source}
                    name={source}
                    value={value}
                  />
                )
              )}

            </div>


            {data.trust?.context
              ?.rain && (
              <div className="context-badge">

                <CloudRain
                  size={15}
                />

                Rain detected —
                CCTV confidence
                reduced

              </div>
            )}


            {data.trust?.context
              ?.fog && (
              <div className="context-badge">

                <AlertTriangle
                  size={15}
                />

                Fog detected —
                visual evidence
                degraded

              </div>
            )}


            {data.trust?.context
              ?.v2x_packet_loss && (
              <div className="context-badge">

                <Wifi size={15} />

                V2X packet loss
                detected

              </div>
            )}

          </div>

        </section>


        {/* =====================================================
            COUNTERFACTUAL ARENA
        ===================================================== */}

        <section className="panel">

          <PanelTitle
            icon={<Brain />}
            title="Counterfactual Arena"
            subtitle="Competing interventions evaluated before execution"
          />


          <div className="proposal-list">

            {candidates.map(
              (candidate, index) => {

                const decision =
                  decisions[index];

                const approved =
                  decision?.approved;

                return (
                  <div
                    className={`proposal ${
                      index === 0
                        ? "winner"
                        : ""
                    }`}
                    key={`${candidate.agent}-${candidate.action}`}
                  >

                    <div className="proposal-rank">
                      {index + 1}
                    </div>


                    <div className="proposal-agent">

                      <strong>
                        {
                          candidate.agent
                        }
                      </strong>

                      <span>
                        {
                          ACTION_LABELS[
                            candidate.action
                          ] ||
                          candidate.action.replaceAll(
                            "_",
                            " "
                          )
                        }
                      </span>

                    </div>


                    <div className="proposal-stat">

                      <small>
                        NETWORK SCORE
                      </small>

                      <strong>
                        {Number(
                          candidate.network_score ||
                            0
                        ).toFixed(3)}
                      </strong>

                    </div>


                    <div className="proposal-stat">

                      <small>
                        RISK
                      </small>

                      <strong>
                        {Math.round(
                          (
                            candidate.predicted_risk ||
                            0
                          ) * 100
                        )}
                        %
                      </strong>

                    </div>


                    <div className="proposal-stat">

                      <small>
                        CONFIDENCE
                      </small>

                      <strong>
                        {Math.round(
                          (
                            candidate.confidence ||
                            0
                          ) * 100
                        )}
                        %
                      </strong>

                    </div>


                    <div className="proposal-status">

                      {approved &&
                      !isBlocked ? (
                        <CheckCircle2
                          size={20}
                        />
                      ) : (
                        <XCircle
                          size={20}
                        />
                      )}

                    </div>

                  </div>
                );
              }
            )}

          </div>

        </section>


        {/* =====================================================
            EVIDENCE GATE + REALITY CHECK
        ===================================================== */}

        <section className="content-grid">

          <div className="panel safety-panel">

            <PanelTitle
              icon={
                <ShieldCheck />
              }
              title="Evidence Gate"
              subtitle="Final authorization layer"
            />


            <div
              className={`gate-status ${
                isBlocked
                  ? "gate-blocked"
                  : ""
              }`}
            >

              <div className="gate-icon">

                {isBlocked ? (
                  <XCircle
                    size={34}
                  />
                ) : (
                  <CheckCircle2
                    size={34}
                  />
                )}

              </div>


              <div>

                <strong>
                  {isBlocked
                    ? "AUTONOMOUS ACTION BLOCKED"
                    : "ACTION APPROVED"}
                </strong>

                <span>
                  {isBlocked
                    ? "Insufficient evidence for autonomous execution"
                    : "All hard safety constraints passed"}
                </span>

              </div>

            </div>


            <div className="gate-metrics">

              <div>

                <small>
                  CONFIDENCE
                </small>

                <strong>
                  {Math.round(
                    (
                      action?.confidence ||
                      topDecision?.confidence ||
                      0
                    ) * 100
                  )}
                  %
                </strong>

              </div>


              <div>

                <small>
                  SAFETY
                </small>

                <strong>
                  {action
                    ? `${Math.round(
                        action.safety_score *
                          100
                      )}%`
                    : "BLOCKED"}
                </strong>

              </div>


              <div>

                <small>
                  EVIDENCE
                </small>

                <strong
                  className={
                    evidenceScore >=
                    0.70
                      ? "evidence-pass"
                      : "evidence-fail"
                  }
                >
                  {Math.round(
                    evidenceScore *
                      100
                  )}
                  %
                </strong>

              </div>


              <div>

                <small>
                  AUTONOMY
                </small>

                <strong>
                  {data.autonomy_mode}
                </strong>

              </div>

            </div>


            <div className="evidence-explanation">

              <div className="evidence-explanation-top">

                <ShieldCheck
                  size={17}
                />

                <strong>
                  Evidence Sufficiency
                </strong>

                <span>
                  {Math.round(
                    evidenceScore *
                      100
                  )}
                  %
                </span>

              </div>


              <div className="evidence-bar">

                <div
                  className="evidence-bar-fill"
                  style={{
                    width: `${Math.max(
                      0,
                      Math.min(
                        100,
                        evidenceScore *
                          100
                      )
                    )}%`,
                  }}
                />

              </div>


              <p>
                {isBlocked
                  ? "Evidence did not reach the autonomous threshold. NEXUS-T safely withholds control."
                  : "Evidence combines confidence, predicted safety and expected network benefit before autonomous execution."}
              </p>

            </div>

          </div>


          <div className="panel">

            <PanelTitle
              icon={
                <TrendingUp />
              }
              title="Post-Action Reality Check"
              subtitle="Prediction versus observed outcome"
            />


            <div className="reality-grid">

              <RealityMetric
                label="Queue"
                predicted={
                  verification.metrics
                    ?.queue
                    ?.predicted ??
                  "—"
                }
                observed={
                  verification.metrics
                    ?.queue
                    ?.observed ??
                  verification.metrics
                    ?.queue
                    ?.actual ??
                  "—"
                }
                accuracy={
                  verification.metrics
                    ?.queue
                    ?.accuracy ??
                  0
                }
              />


              <RealityMetric
                label="Speed"
                predicted={
                  verification.metrics
                    ?.speed
                    ?.predicted ??
                  "—"
                }
                observed={
                  verification.metrics
                    ?.speed
                    ?.observed ??
                  verification.metrics
                    ?.speed
                    ?.actual ??
                  "—"
                }
                accuracy={
                  verification.metrics
                    ?.speed
                    ?.accuracy ??
                  0
                }
              />

            </div>


            <div className="verification-result">

              <CheckCircle2
                size={19}
              />

              <span>
                {verification.verified
                  ? "Prediction verified"
                  : "Verification below threshold"}
              </span>

              <strong>
                {Math.round(
                  (
                    verification.overall_accuracy ||
                    0
                  ) * 100
                )}
                %
              </strong>

            </div>

          </div>

        </section>


        {/* =====================================================
            EXECUTION TRACE
        ===================================================== */}

        <section className="panel execution-panel">

          <PanelTitle
            icon={<Activity />}
            title="Autonomous Execution Trace"
            subtitle="Evidence → verification → authorization → action → learning"
          />


          <div className="execution-flow">

            <ExecutionStep
              number="01"
              title="SENSE"
              detail="CCTV + V2X + IoT + GPS"
              status="COMPLETE"
            />

            <ChevronRight
              className="execution-arrow"
            />

            <ExecutionStep
              number="02"
              title="FUSE"
              detail="Belief + source trust"
              status="COMPLETE"
            />

            <ChevronRight
              className="execution-arrow"
            />

            <ExecutionStep
              number="03"
              title="PROPOSE"
              detail={`${candidates.length} competing proposals`}
              status="COMPLETE"
            />

            <ChevronRight
              className="execution-arrow"
            />

            <ExecutionStep
              number="04"
              title="VERIFY"
              detail="Counterfactual + safety gate"
              status={
                isBlocked
                  ? "BLOCKED"
                  : "PASSED"
              }
            />

            <ChevronRight
              className="execution-arrow"
            />

            <ExecutionStep
              number="05"
              title="ACT"
              detail={
                action
                  ? ACTION_LABELS[
                      action.action
                    ] ||
                    action.action
                  : "No action"
              }
              status={
                isBlocked
                  ? "HELD"
                  : "EXECUTED"
              }
            />

            <ChevronRight
              className="execution-arrow"
            />

            <ExecutionStep
              number="06"
              title="LEARN"
              detail="Reality → trust update"
              status="COMPLETE"
            />

          </div>

        </section>


        {/* =====================================================
            EXPLANATION
        ===================================================== */}

        <section className="panel explanation-panel">

          <PanelTitle
            icon={<Brain />}
            title="Why NEXUS-T Acted"
            subtitle="Machine-readable decision explanation"
          />


          <div className="decision-explanation">

            <div className="explanation-main">

              <div className="explanation-status">

                {isBlocked ? (
                  <XCircle
                    size={25}
                  />
                ) : (
                  <CheckCircle2
                    size={25}
                  />
                )}

                <strong>
                  {action
                    ? ACTION_LABELS[
                        action.action
                      ] ||
                      action.action
                    : "NO AUTONOMOUS ACTION"}
                </strong>

              </div>


              <p>
                {
                  data.decision_summary
                }
              </p>

            </div>


            <div className="explanation-reasons">

              <div>

                <small>
                  TRAFFIC STATE
                </small>

                <strong>
                  {state.vehicle_count ??
                    0}{" "}
                  vehicles ·{" "}
                  {Math.round(
                    (
                      state.congestion ||
                      0
                    ) * 100
                  )}
                  % congestion
                </strong>

              </div>


              <div>

                <small>
                  LIVE WORLD CONFIDENCE
                </small>

                <strong>
                  {Math.round(
                    liveConfidence *
                      100
                  )}
                  % ·{" "}
                  {liveWorld.evidence_quality ||
                    "—"}
                </strong>

              </div>


              <div>

                <small>
                  NETWORK IMPACT
                </small>

                <strong>
                  {selectedImpact
                    ? `${selectedImpact.queue_reduction}m queue reduction`
                    : "No action"}
                </strong>

              </div>


              <div>

                <small>
                  SAFETY DECISION
                </small>

                <strong>
                  {isBlocked
                    ? "AUTONOMY BLOCKED"
                    : "SAFETY CONSTRAINTS PASSED"}
                </strong>

              </div>

            </div>

          </div>

        </section>


        {/* =====================================================
            FOOTER
        ===================================================== */}

        <footer>

          <div>

            <span className="footer-dot"></span>

            NEXUS-T AUTONOMOUS
            TRAFFIC SAFETY

          </div>

          <div>
            Evidence → Counterfactuals
            → Safety → Action → Reality
            → Learning
          </div>

          <div>
            {lastUpdated
              ? `Updated ${lastUpdated.toLocaleTimeString()}`
              : ""}
          </div>

        </footer>

      </main>

    </div>
  );
}


/* =============================================================
   PANEL TITLE
============================================================= */

function PanelTitle({
  icon,
  title,
  subtitle,
}) {
  return (
    <div className="panel-title">

      <div className="panel-title-icon">
        {icon}
      </div>

      <div>

        <h3>{title}</h3>

        <p>{subtitle}</p>

      </div>

    </div>
  );
}


/* =============================================================
   METRIC CARD
============================================================= */

function MetricCard({
  icon,
  label,
  value,
  detail,
  danger = false,
}) {
  return (
    <div
      className={`metric-card ${
        danger ? "danger" : ""
      }`}
    >

      <div className="metric-icon">
        {icon}
      </div>

      <div className="metric-label">
        {label}
      </div>

      <div className="metric-value">
        {value}
      </div>

      <div className="metric-detail">
        {detail}
      </div>

    </div>
  );
}


/* =============================================================
   LIVE STAT
============================================================= */

function LiveStat({
  label,
  value,
  detail,
  icon,
}) {
  return (
    <div className="live-stat">

      <div className="live-stat-label">

        {icon}

        {label}

      </div>

      <strong>
        {value}
      </strong>

      <span>
        {detail}
      </span>

    </div>
  );
}


/* =============================================================
   LIVE METRIC
============================================================= */

function LiveMetric({
  label,
  value,
}) {
  return (
    <div className="live-metric">

      <small>
        {label}
      </small>

      <strong>
        {value}
      </strong>

    </div>
  );
}


/* =============================================================
   SOURCE TRUST
============================================================= */

function SourceTrust({
  name,
  value,
}) {
  const percent = Math.round(
    Math.max(
      0,
      Math.min(
        1,
        Number(value) || 0
      )
    ) * 100
  );

  return (
    <div className="source-trust-row">

      <span>
        {name}
      </span>

      <div className="source-trust-bar">

        <div
          style={{
            width: `${percent}%`,
          }}
        />

      </div>

      <strong>
        {percent}%
      </strong>

    </div>
  );
}


/* =============================================================
   IMPACT CARD
============================================================= */

function ImpactCard({
  label,
  value,
  detail,
}) {
  return (
    <div className="impact-card">

      <small>
        {label}
      </small>

      <strong>
        {value}
      </strong>

      <span>
        {detail}
      </span>

    </div>
  );
}


/* =============================================================
   EVENT NODE
============================================================= */

function EventNode({
  icon,
  title,
  detail,
}) {
  return (
    <div className="event-node">

      <div className="event-icon">
        {icon}
      </div>

      <strong>
        {title}
      </strong>

      <span>
        {detail}
      </span>

    </div>
  );
}


/* =============================================================
   EXECUTION STEP
============================================================= */

function ExecutionStep({
  number,
  title,
  detail,
  status,
}) {
  const blocked =
    status === "BLOCKED" ||
    status === "HELD";

  return (
    <div
      className={`execution-step ${
        blocked
          ? "blocked-step"
          : ""
      }`}
    >

      <div className="execution-number">
        {number}
      </div>

      <strong>
        {title}
      </strong>

      <span>
        {detail}
      </span>

      <small>
        {status}
      </small>

    </div>
  );
}


/* =============================================================
   REALITY METRIC
============================================================= */

function RealityMetric({
  label,
  predicted,
  observed,
  accuracy,
}) {
  return (
    <div className="reality-card">

      <div className="reality-label">
        {label}
      </div>


      <div className="reality-values">

        <div>

          <small>
            PREDICTED
          </small>

          <strong>
            {predicted}
          </strong>

        </div>


        <ChevronRight
          size={18}
        />


        <div>

          <small>
            OBSERVED SIMULATION
          </small>

          <strong>
            {observed}
          </strong>

        </div>

      </div>


      <div className="accuracy">

        <CheckCircle2
          size={14}
        />

        {Math.round(
          accuracy * 100
        )}
        % match

      </div>

    </div>
  );
}


export default App;
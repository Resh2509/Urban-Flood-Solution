import { useEffect, useMemo, useRef, useState } from "react";
import * as maplibregl from "maplibre-gl";
import Papa from "papaparse";
import "maplibre-gl/dist/maplibre-gl.css";
import "./App.css";

const DATA = {
  nodes: "/data/01_velachery_nodes.csv",
  network: "/data/03_drainage_network.csv",
  drainage: "/data/member3_drainage_visualization.csv",
  predictions: "/data/member3_flood_predictions_new.csv",
  roads: "/data/roads.geojson",
  studyArea: "/data/study_area.geojson",
};

const TIME_OPTIONS = [
  { key: "current", label: "NOW", csv: "current_depth" },
  { key: "1h", label: "+1 HOUR", csv: "depth_t_plus_1h" },
  { key: "2h", label: "+2 HOURS", csv: "depth_t_plus_2h" },
  { key: "3h", label: "+3 HOURS", csv: "depth_t_plus_3h" },
];

const riskColor = (severity) => {
  const value = String(severity || "Low").toLowerCase().trim();
  if (value.includes("critical") || value.includes("severe")) return "#ef4444";
  if (value.includes("high")) return "#f97316";
  if (value.includes("medium") || value.includes("warning")) return "#f59e0b";
  return "#22c55e";
};

const riskLabel = (severity) => {
  const value = String(severity || "Low").toLowerCase();
  if (value.includes("critical") || value.includes("severe")) return "CRITICAL";
  if (value.includes("high")) return "HIGH RISK";
  if (value.includes("medium") || value.includes("warning")) return "WARNING";
  return "SAFE";
};

const num = (value) => {
  const n = Number.parseFloat(value);
  return Number.isFinite(n) ? n : null;
};

const getDepth = (prediction, time) => {
  if (!prediction) return null;
  return num(prediction[TIME_OPTIONS.find((x) => x.key === time)?.csv || "current_depth"]);
};

const parseCsv = async (url) => {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Cannot load ${url}`);
  const text = await response.text();
  return Papa.parse(text, {
    header: true,
    skipEmptyLines: true,
    transformHeader: (header) =>
      String(header).trim().replace(/^\uFEFF/, "").replace(/\s+/g, "_"),
  }).data;
};

function App() {
  const mapContainer = useRef(null);
  const mapRef = useRef(null);
  const nodeMarkersRef = useRef([]);
  const flowMarkersRef = useRef([]);

  const [selectedTime, setSelectedTime] = useState("current");
  const [status, setStatus] = useState("Loading digital twin…");
  const [predictions, setPredictions] = useState({});
  const [nodes, setNodes] = useState([]);
  const [drainage, setDrainage] = useState([]);
  const [rainfall] = useState(null);
  const [rainfallTime] = useState("");
  const [selectedNode, setSelectedNode] = useState(null);

  const predictionList = useMemo(() => Object.values(predictions), [predictions]);

  const kpis = useMemo(() => {
    const critical = predictionList.filter((p) =>
      /critical|severe/i.test(p.severity || "")
    ).length;
    const high = predictionList.filter((p) => /high/i.test(p.severity || "")).length;
    const blockages = predictionList.filter((p) =>
      /severe/i.test(p.blockage_status || "")
    ).length;
    const backflow = predictionList.filter(
      (p) => String(p.backflow_risk).toLowerCase() === "true"
    ).length;
    const maxDepth = predictionList.reduce((max, p) => {
      const d = getDepth(p, selectedTime);
      return d !== null && d > max ? d : max;
    }, 0);

    return {
      nodes: nodes.length,
      pipes: drainage.length,
      critical,
      high,
      blockages,
      backflow,
      maxDepth,
    };
  }, [predictionList, nodes.length, drainage.length, selectedTime]);

  const priorityLocations = useMemo(() => {
    return [...predictionList]
      .sort((a, b) => {
        const score = (p) =>
          (/critical/i.test(p.severity) ? 4 : /high/i.test(p.severity) ? 3 : /medium/i.test(p.severity) ? 2 : 1) +
          (String(p.backflow_risk).toLowerCase() === "true" ? 1 : 0) +
          (String(p.blockage_status).toLowerCase().includes("severe") ? 1 : 0);
        return score(b) - score(a);
      })
      .slice(0, 5)
      .map((p) => {
        const node = nodes.find((n) => String(n.node_id).trim() === String(p.node_id).trim());
        return { ...p, location_name: node?.location_name || "Mapped node" };
      });
  }, [predictionList, nodes]);

  const popupHtml = (node, prediction, time) => {
    const depth = getDepth(prediction, time);
    const label = TIME_OPTIONS.find((x) => x.key === time)?.label || "NOW";
    const severity = prediction?.severity || "Low";
    return `
      <div class="popup-card">
        <div class="popup-title">${node.location_name || "Flood location"}</div>
        <div class="popup-subtitle">${node.node_id}</div>
        <div class="popup-section">
          <div><span>Selected forecast</span><strong>${label}</strong></div>
          <div><span>Water depth</span><strong>${depth !== null ? depth.toFixed(3) : "N/A"} m</strong></div>
          <div><span>Risk</span><strong style="color:${riskColor(severity)}">${riskLabel(severity)}</strong></div>
        </div>
        <div class="popup-section">
          <div><span>NOW</span><strong>${getDepth(prediction, "current")?.toFixed(3) ?? "N/A"} m</strong></div>
          <div><span>+1 hour</span><strong>${getDepth(prediction, "1h")?.toFixed(3) ?? "N/A"} m</strong></div>
          <div><span>+2 hours</span><strong>${getDepth(prediction, "2h")?.toFixed(3) ?? "N/A"} m</strong></div>
          <div><span>+3 hours</span><strong>${getDepth(prediction, "3h")?.toFixed(3) ?? "N/A"} m</strong></div>
        </div>
        <div class="popup-section">
          <div><span>Blockage</span><strong>${prediction?.blockage_status || "N/A"}</strong></div>
          <div><span>Surcharge</span><strong>${prediction?.surcharge_status || "N/A"}</strong></div>
          <div><span>Backflow</span><strong>${prediction?.backflow_risk ?? "N/A"}</strong></div>
          <div><span>Integrated risk</span><strong>${prediction?.integrated_risk || "N/A"}</strong></div>
        </div>
      </div>
    `;
  };

  useEffect(() => {
    if (mapRef.current) return;

    const map = new maplibregl.Map({
      container: mapContainer.current,
      style: "https://demotiles.maplibre.org/style.json",
      center: [80.2216, 12.9784],
      zoom: 13.7,
      attributionControl: true,
    });

    mapRef.current = map;
    map.addControl(new maplibregl.NavigationControl({ showCompass: true }), "top-right");

    map.on("load", async () => {
      try {
        const [studyArea, roads, nodeRows, networkRows, drainageRows, predictionRows] =
          await Promise.all([
            fetch(DATA.studyArea).then((r) => r.json()),
            fetch(DATA.roads).then((r) => r.json()),
            parseCsv(DATA.nodes),
            parseCsv(DATA.network),
            parseCsv(DATA.drainage),
            parseCsv(DATA.predictions),
          ]);

        const predictionMap = {};
        predictionRows.forEach((row) => {
          const id = String(row.node_id || "").trim();
          if (id) predictionMap[id] = row;
        });

        setPredictions(predictionMap);
        setNodes(nodeRows);
        setDrainage(drainageRows);

        const coords = {};
        nodeRows.forEach((node) => {
          const lat = num(node.latitude);
          const lng = num(node.longitude);
          const id = String(node.node_id || "").trim();
          if (id && lat !== null && lng !== null) coords[id] = [lng, lat];
        });

        // Study area
        map.addSource("study-area", { type: "geojson", data: studyArea });
        map.addLayer({
          id: "study-area-fill",
          type: "fill",
          source: "study-area",
          paint: { "fill-color": "#38bdf8", "fill-opacity": 0.08 },
        });
        map.addLayer({
          id: "study-area-outline",
          type: "line",
          source: "study-area",
          paint: { "line-color": "#0f172a", "line-width": 2, "line-opacity": 0.75 },
        });

        // Roads
        map.addSource("roads", { type: "geojson", data: roads });
        map.addLayer({
          id: "roads-layer",
          type: "line",
          source: "roads",
          paint: { "line-color": "#64748b", "line-width": 2.2, "line-opacity": 0.55 },
        });

        // Drainage network + Member 3 drainage visualization
        const visualByPipe = {};
        drainageRows.forEach((row) => {
          const id = String(row.drainage_id || row.pipe_id || "").trim();
          if (id) visualByPipe[id] = row;
        });

        const features = [];
        networkRows.forEach((pipe) => {
          const pipeId = String(pipe.pipe_id || pipe.drainage_id || "").trim();
          const source = String(pipe.source_node || pipe.from_node || "").trim();
          const target = String(pipe.target_node || pipe.to_node || "").trim();
          if (!pipeId || !coords[source] || !coords[target]) return;

          const visual = visualByPipe[pipeId] || {};
          const blockageStatus = visual.blockage_status || pipe.blockage_status || "Normal";
          const severe = /severe/i.test(blockageStatus);

          features.push({
            type: "Feature",
            properties: {
              pipe_id: pipeId,
              source_node: source,
              target_node: target,
              severe,
              flow_rate: visual.flow_rate_lps ?? "N/A",
              capacity: visual.capacity_lps ?? pipe.pipe_capacity_lps ?? "N/A",
              water_level: visual.water_level_cm ?? "N/A",
              blockage_probability: visual.blockage_probability ?? "N/A",
              blockage_status: blockageStatus,
              overflow_risk: visual.overflow_risk ?? "N/A",
              backflow_risk: visual.backflow_risk ?? "N/A",
            },
            geometry: { type: "LineString", coordinates: [coords[source], coords[target]] },
          });
        });

        map.addSource("drainage-network", {
          type: "geojson",
          data: { type: "FeatureCollection", features },
        });

        map.addLayer({
          id: "normal-drainage-pipes",
          type: "line",
          source: "drainage-network",
          filter: ["==", ["get", "severe"], false],
          paint: {
            "line-color": "#16a34a",
            "line-width": 4,
            "line-opacity": 0.82,
          },
        });

        map.addLayer({
          id: "severe-drainage-pipes",
          type: "line",
          source: "drainage-network",
          filter: ["==", ["get", "severe"], true],
          paint: {
            "line-color": "#ef4444",
            "line-width": 6,
            "line-opacity": 0.95,
          },
        });

        // One clear arrow at the centre of every pipe: source -> target.
        features.forEach((feature) => {
          const [source, target] = feature.geometry.coordinates;
          const mid = [(source[0] + target[0]) / 2, (source[1] + target[1]) / 2];

          const dx = target[0] - source[0];
          const dy = target[1] - source[1];
          const angle = Math.atan2(dy, dx) * 180 / Math.PI;

          const arrow = document.createElement("div");
          arrow.className = "flow-arrow";
          arrow.style.transform = `rotate(${angle}deg)`;
          arrow.innerHTML = `
            <span class="flow-line"></span>
            <span class="flow-head"></span>
          `;

          const marker = new maplibregl.Marker({ element: arrow, anchor: "center" })
            .setLngLat(mid)
            .addTo(map);
          flowMarkersRef.current.push(marker);
        });

        const showPipePopup = (e) => {
          const pipe = e.features?.[0];
          if (!pipe) return;
          new maplibregl.Popup({ closeButton: true, maxWidth: "320px" })
            .setLngLat(e.lngLat)
            .setHTML(`
              <div class="popup-card">
                <div class="popup-title">Drainage Pipe ${pipe.properties.pipe_id}</div>
                <div class="popup-subtitle">${pipe.properties.source_node} → ${pipe.properties.target_node}</div>
                <div class="popup-section">
                  <div><span>Flow rate</span><strong>${pipe.properties.flow_rate} LPS</strong></div>
                  <div><span>Capacity</span><strong>${pipe.properties.capacity} LPS</strong></div>
                  <div><span>Water level</span><strong>${pipe.properties.water_level}${pipe.properties.water_level !== "N/A" ? " cm" : ""}</strong></div>
                  <div><span>Blockage</span><strong>${pipe.properties.blockage_status}</strong></div>
                  <div><span>Overflow risk</span><strong>${pipe.properties.overflow_risk}</strong></div>
                  <div><span>Backflow risk</span><strong>${pipe.properties.backflow_risk}</strong></div>
                </div>
              </div>
            `)
            .addTo(map);
        };

        map.on("click", "normal-drainage-pipes", showPipePopup);
        map.on("click", "severe-drainage-pipes", showPipePopup);
        map.on("mouseenter", "normal-drainage-pipes", () => (map.getCanvas().style.cursor = "pointer"));
        map.on("mouseenter", "severe-drainage-pipes", () => (map.getCanvas().style.cursor = "pointer"));
        map.on("mouseleave", "normal-drainage-pipes", () => (map.getCanvas().style.cursor = ""));
        map.on("mouseleave", "severe-drainage-pipes", () => (map.getCanvas().style.cursor = ""));

        // Node markers
        nodeRows.forEach((node) => {
          const id = String(node.node_id || "").trim();
          if (!coords[id]) return;
          const prediction = predictionMap[id] || {};
          const markerElement = document.createElement("div");
          markerElement.className = "node-marker";
          markerElement.style.background = riskColor(prediction.severity);

          const popup = new maplibregl.Popup({ offset: 18, maxWidth: "340px" })
            .setHTML(popupHtml(node, prediction, "current"));

          const marker = new maplibregl.Marker({ element: markerElement })
            .setLngLat(coords[id])
            .setPopup(popup)
            .addTo(map);

          markerElement.addEventListener("click", () => {
            setSelectedNode({ node, prediction });
          });

          nodeMarkersRef.current.push({
            marker,
            markerElement,
            popup,
            node,
            nodeId: id,
            prediction,
          });
        });

        setStatus(
          `LIVE DATASET • ${nodeRows.length} nodes • ${features.length} pipes • ${predictionRows.length} forecasts`
        );
      } catch (error) {
        console.error(error);
        setStatus(`ERROR: ${error.message}`);
      }
    });

    return () => {
      nodeMarkersRef.current.forEach(({ marker }) => marker.remove());
      flowMarkersRef.current.forEach((marker) => marker.remove());
      nodeMarkersRef.current = [];
      flowMarkersRef.current = [];
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    nodeMarkersRef.current.forEach(({ markerElement, popup, node, prediction }) => {
      markerElement.style.background = riskColor(prediction?.severity);
      popup.setHTML(popupHtml(node, prediction, selectedTime));
      const depth = getDepth(prediction, selectedTime);
      markerElement.title = `${node.node_id} • ${TIME_OPTIONS.find((x) => x.key === selectedTime)?.label} • ${depth ?? "N/A"} m`;
    });
  }, [selectedTime]);

  const selectedLabel = TIME_OPTIONS.find((x) => x.key === selectedTime)?.label || "NOW";

  return (
    <div className="dashboard-shell">
      <div ref={mapContainer} className="map-canvas" />

      <header className="topbar">
        <div>
          <div className="brand-row">
            <span className="brand-mark">🌊</span>
            <div>
              <h1>HydroGraph-Twin</h1>
              <p>Velachery Flood Monitoring • GIS Digital Twin</p>
            </div>
          </div>
        </div>
        <div className="live-badge"><span /> LIVE MAP</div>
      </header>

      <aside className="left-panel">
        <section className="glass-card hero-card">
          <div className="eyebrow">FLOOD & DRAINAGE INTELLIGENCE</div>
          <h2>See the risk before it reaches the street.</h2>
          <p className="muted">
            AI flood predictions are joined to mapped nodes and the drainage network using <b>node_id</b>.
          </p>
          <div className="data-status">{status}</div>
        </section>

        <section className="kpi-grid">
          <div className="kpi-card"><span>Mapped Nodes</span><strong>{kpis.nodes}</strong><small>GIS locations</small></div>
          <div className="kpi-card"><span>Drainage Pipes</span><strong>{kpis.pipes}</strong><small>network links</small></div>
          <div className="kpi-card danger"><span>Critical Nodes</span><strong>{kpis.critical}</strong><small>current risk class</small></div>
          <div className="kpi-card warning"><span>High Risk</span><strong>{kpis.high}</strong><small>priority monitoring</small></div>
          <div className="kpi-card danger"><span>Blockages</span><strong>{kpis.blockages}</strong><small>severe status</small></div>
          <div className="kpi-card"><span>Backflow Risk</span><strong>{kpis.backflow}</strong><small>true in dataset</small></div>
        </section>

        <section className="glass-card forecast-card">
          <div className="section-heading">
            <div>
              <div className="eyebrow">TIME MACHINE</div>
              <h3>Flood Forecast</h3>
            </div>
            <span className="selected-pill">{selectedLabel}</span>
          </div>

          <div className="timeline">
            {TIME_OPTIONS.map((option, index) => (
              <div className="timeline-item" key={option.key}>
                <button
                  className={selectedTime === option.key ? "time-button active" : "time-button"}
                  onClick={() => setSelectedTime(option.key)}
                >
                  {option.label}
                </button>
                {index < TIME_OPTIONS.length - 1 && <span className="timeline-line" />}
              </div>
            ))}
          </div>

          <p className="muted small">
            Select a time to update node popups and see the predicted water depth for that horizon.
          </p>
        </section>

        <section className="glass-card rainfall-card">
          <div className="section-heading">
            <div><div className="eyebrow">INPUT</div><h3>🌧️ Rainfall</h3></div>
            <span className="source-tag">MEMBER 1</span>
          </div>
          {rainfall !== null ? (
            <>
              <div className="rain-value">{rainfall} <span>mm</span></div>
              <div className="muted small">{rainfallTime || "Latest available reading"}</div>
            </>
          ) : (
            <div className="unavailable">
              <strong>Rainfall input not connected</strong>
              <span>No rainfall CSV was supplied for this dashboard.</span>
            </div>
          )}
        </section>

        <section className="glass-card priority-card">
          <div className="section-heading">
            <div><div className="eyebrow">ACTION LIST</div><h3>🚨 Priority Locations</h3></div>
            <span className="count-pill">{priorityLocations.length}</span>
          </div>
          <div className="priority-list">
            {priorityLocations.map((p) => (
              <button
                className="priority-row"
                key={p.node_id}
                onClick={() => {
                  const item = nodeMarkersRef.current.find((x) => x.nodeId === p.node_id);
                  if (item) {
                    item.marker.togglePopup();
                    mapRef.current?.flyTo({ center: item.marker.getLngLat(), zoom: 15.2, duration: 700 });
                  }
                }}
              >
                <span className="priority-dot" style={{ background: riskColor(p.severity) }} />
                <span className="priority-main">
                  <b>{p.node_id}</b>
                  <small>{p.location_name}</small>
                </span>
                <span className="priority-risk">{riskLabel(p.severity)}</span>
              </button>
            ))}
          </div>
        </section>

        <section className="glass-card response-card">
          <div className="eyebrow">OPERATIONS</div>
          <h3>Response Readiness</h3>
          <div className="readiness-row"><span>👷 Worker assignment</span><b className="not-connected">Pending input</b></div>
          <div className="readiness-row"><span>🛣️ Safe route</span><b className="not-connected">Road data only</b></div>
          <p className="muted small">These two modules require worker and road-level flood/routing outputs that are not present in the supplied CSVs.</p>
        </section>
      </aside>

      <div className="right-legend glass-card">
        <div className="eyebrow">MAP LEGEND</div>
        <div className="legend-row"><i style={{ background: "#22c55e" }} /> Safe / Low</div>
        <div className="legend-row"><i style={{ background: "#f59e0b" }} /> Warning / Medium</div>
        <div className="legend-row"><i style={{ background: "#f97316" }} /> High Risk</div>
        <div className="legend-row"><i style={{ background: "#ef4444" }} /> Critical</div>
        <div className="legend-divider" />
        <div className="legend-row"><span className="line-sample" /> Normal pipe</div>
        <div className="legend-row"><span className="line-sample severe" /> Severe blockage</div>
        <div className="legend-row"><span className="arrow-sample">➜</span> Flow direction</div>
      </div>

      <div className="map-hint">
        <span>📍</span>
        <div><b>Click a node</b><small>View flood + drainage risk</small></div>
      </div>

      <div className="bottom-bar">
        <div><b>MAX DEPTH</b><span>{kpis.maxDepth.toFixed(3)} m</span></div>
        <div><b>SELECTED</b><span>{selectedLabel}</span></div>
        <div><b>MODEL INPUT</b><span>Member 1 hourly forecast</span></div>
        <div><b>NETWORK</b><span>Member 2 drainage data</span></div>
      </div>

      {selectedNode && (
        <div className="selected-node-toast">
          <span className="toast-dot" style={{ background: riskColor(selectedNode.prediction?.severity) }} />
          <div><b>{selectedNode.node.node_id}</b><small>{selectedNode.node.location_name}</small></div>
          <button onClick={() => setSelectedNode(null)}>×</button>
        </div>
      )}
    </div>
  );
}

export default App;

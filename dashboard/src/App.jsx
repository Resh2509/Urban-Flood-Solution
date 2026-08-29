import { useEffect, useRef, useState } from "react";
import * as maplibregl from "maplibre-gl";
import Papa from "papaparse";
import "maplibre-gl/dist/maplibre-gl.css";

function App() {
  const mapContainer = useRef(null);

  // Store map and markers
  const mapRef = useRef(null);
  const nodeMarkersRef = useRef([]);

  const [message, setMessage] = useState("Loading map...");
  const [selectedTime, setSelectedTime] = useState("current");

  // =========================================================
  // DAY 4: GET THE CORRECT MEMBER 1 DEPTH FOR SELECTED TIME
  // =========================================================
  const getSelectedDepth = (prediction, time) => {
    if (time === "current") {
      return prediction.current_depth || "N/A";
    }

    if (time === "15") {
      return prediction.depth_15min || "N/A";
    }

    if (time === "30") {
      return prediction.depth_30min || "N/A";
    }

    if (time === "45") {
      return prediction.depth_45min || "N/A";
    }

    return "N/A";
  };

  const getSelectedTimeLabel = (time) => {
    if (time === "current") return "Current Time";
    if (time === "15") return "+15 Minutes";
    if (time === "30") return "+30 Minutes";
    if (time === "45") return "+45 Minutes";
    return "Unknown";
  };

  // =========================================================
  // MEMBER 1 SEVERITY COLOUR
  // =========================================================
  const getSeverityColor = (severity) => {
    const value = String(severity || "low").toLowerCase().trim();

    if (value === "medium") return "#FFC107";
    if (value === "high") return "#FF9800";
    if (value === "severe") return "#F44336";

    return "#4CAF50";
  };

  // =========================================================
  // CREATE NODE POPUP
  // =========================================================
  const createNodePopupHtml = (node, nodeId, prediction, time) => {
    const selectedDepth = getSelectedDepth(prediction, time);
    const selectedTimeLabel = getSelectedTimeLabel(time);
    const severity = String(
      prediction.severity || "Low"
    ).trim();

    return `
      <div style="min-width: 230px;">
        <h3 style="margin-bottom: 8px;">
          ${node.location_name || "Flood Monitoring Node"}
        </h3>

        <p><b>Node ID:</b> ${nodeId}</p>

        <p><b>Selected Prediction Time:</b>
        ${selectedTimeLabel}</p>

        <p style="font-size: 16px;">
          <b>Selected Water Depth:</b>
          ${selectedDepth} m
        </p>

        <hr />

        <h4>Member 1 Flood Prediction</h4>

        <p><b>Current Depth:</b>
        ${prediction.current_depth || "N/A"} m</p>

        <p><b>+15 min Depth:</b>
        ${prediction.depth_15min || "N/A"} m</p>

        <p><b>+30 min Depth:</b>
        ${prediction.depth_30min || "N/A"} m</p>

        <p><b>+45 min Depth:</b>
        ${prediction.depth_45min || "N/A"} m</p>

        <hr />

        <p><b>Severity:</b> ${severity}</p>
      </div>
    `;
  };

  // =========================================================
  // LOAD MAP ONLY ONCE
  // =========================================================
  useEffect(() => {
    if (mapRef.current) return;

    const map = new maplibregl.Map({
      container: mapContainer.current,
      style: "https://demotiles.maplibre.org/style.json",
      center: [80.22, 12.978],
      zoom: 13,
    });

    mapRef.current = map;

    map.on("load", async () => {
      try {
        // =====================================================
        // 1. LOAD STUDY AREA
        // =====================================================
        const studyResponse = await fetch(
          "/data/study_area.geojson"
        );

        if (!studyResponse.ok) {
          throw new Error("Cannot load study_area.geojson");
        }

        const studyArea = await studyResponse.json();

        map.addSource("study-area", {
          type: "geojson",
          data: studyArea,
        });

        map.addLayer({
          id: "study-area-fill",
          type: "fill",
          source: "study-area",
          paint: {
            "fill-opacity": 0.1,
          },
        });

        map.addLayer({
          id: "study-area-outline",
          type: "line",
          source: "study-area",
          paint: {
            "line-width": 2,
          },
        });

        // =====================================================
        // 2. LOAD ROADS
        // =====================================================
        const roadsResponse = await fetch(
          "/data/roads.geojson"
        );

        if (!roadsResponse.ok) {
          throw new Error("Cannot load roads.geojson");
        }

        const roads = await roadsResponse.json();

        map.addSource("roads", {
          type: "geojson",
          data: roads,
        });

        map.addLayer({
          id: "roads-layer",
          type: "line",
          source: "roads",
          paint: {
            "line-width": 2,
          },
        });

        // =====================================================
        // 3. LOAD MEMBER 1 FLOOD PREDICTION DATA
        // =====================================================
        const predictionResponse = await fetch(
          "/data/member1_flood_predictions.csv"
        );

        if (!predictionResponse.ok) {
          throw new Error(
            "Cannot load member1_flood_predictions.csv"
          );
        }

        const predictionCsvText =
          await predictionResponse.text();

        const predictionResult = Papa.parse(
          predictionCsvText,
          {
            header: true,
            skipEmptyLines: true,
            delimiter: ",",
            transformHeader: (header) =>
              header.trim().replace(/^\uFEFF/, ""),
          }
        );

        // Store Member 1 data using node_id
        const predictionData = {};

        predictionResult.data.forEach((row) => {
          const nodeId = String(
            row.node_id || ""
          ).trim();

          if (nodeId) {
            predictionData[nodeId] = row;
          }
        });

        // =====================================================
        // 4. LOAD NODES
        // =====================================================
        const nodesResponse = await fetch(
          "/data/01_velachery_nodes.csv"
        );

        if (!nodesResponse.ok) {
          throw new Error(
            "Cannot load 01_velachery_nodes.csv"
          );
        }

        const nodesCsvText =
          await nodesResponse.text();

        const nodesResult = Papa.parse(
          nodesCsvText,
          {
            header: true,
            skipEmptyLines: true,
            delimiter: ",",
            transformHeader: (header) =>
              header.trim().replace(/^\uFEFF/, ""),
          }
        );

        const nodeCoordinates = {};
        let nodeCount = 0;

        nodesResult.data.forEach((node) => {
          const nodeId = String(
            node.node_id || ""
          ).trim();

          const latitude = parseFloat(
            String(node.latitude || "").trim()
          );

          const longitude = parseFloat(
            String(node.longitude || "").trim()
          );

          if (
            nodeId &&
            !isNaN(latitude) &&
            !isNaN(longitude)
          ) {
            // Store coordinates for drainage pipes
            nodeCoordinates[nodeId] = [
              longitude,
              latitude,
            ];

            const prediction =
              predictionData[nodeId] || {};

            const severity = String(
              prediction.severity || "Low"
            ).trim();

            const nodeColor =
              getSeverityColor(severity);

            // Create marker
            const markerElement =
              document.createElement("div");

            markerElement.style.width = "24px";
            markerElement.style.height = "24px";
            markerElement.style.borderRadius = "50%";
            markerElement.style.backgroundColor =
              nodeColor;
            markerElement.style.border =
              "3px solid white";
            markerElement.style.boxShadow =
              "0 2px 6px rgba(0,0,0,0.4)";
            markerElement.style.cursor =
              "pointer";

            const popup =
              new maplibregl.Popup({
                offset: 25,
              }).setHTML(
                createNodePopupHtml(
                  node,
                  nodeId,
                  prediction,
                  "current"
                )
              );

            const marker =
              new maplibregl.Marker({
                element: markerElement,
              })
                .setLngLat([
                  longitude,
                  latitude,
                ])
                .setPopup(popup)
                .addTo(map);

            // Store marker for Day 4 updates
            nodeMarkersRef.current.push({
              marker,
              markerElement,
              popup,
              node,
              nodeId,
              prediction,
            });

            nodeCount++;
          }
        });

        // =====================================================
        // 5. LOAD MEMBER 2 DRAINAGE DATA
        // =====================================================
        const drainageResponse = await fetch(
          "/data/03_drainage_network.csv"
        );

        if (!drainageResponse.ok) {
          throw new Error(
            "Cannot load 03_drainage_network.csv"
          );
        }

        const drainageCsvText =
          await drainageResponse.text();

        const drainageResult = Papa.parse(
          drainageCsvText,
          {
            header: true,
            skipEmptyLines: true,
            delimiter: ",",
            transformHeader: (header) =>
              header.trim().replace(/^\uFEFF/, ""),
          }
        );

        const drainageFeatures = [];
        let pipeCount = 0;
        let severeBlockageCount = 0;

        drainageResult.data.forEach((pipe) => {
          const pipeId = String(
            pipe.drainage_id ||
              pipe.pipe_id ||
              ""
          ).trim();

          const sourceNode = String(
            pipe.from_node ||
              pipe.source_node ||
              ""
          ).trim();

          const targetNode = String(
            pipe.to_node ||
              pipe.target_node ||
              ""
          ).trim();

          if (
            pipeId &&
            nodeCoordinates[sourceNode] &&
            nodeCoordinates[targetNode]
          ) {
            const blockageStatus = String(
              pipe.blockage_status ||
                pipe.blockage_st ||
                "Normal"
            ).trim();

            const isSevere =
              blockageStatus
                .toLowerCase()
                .includes("severe");

            if (isSevere) {
              severeBlockageCount++;
            }

            drainageFeatures.push({
              type: "Feature",

              properties: {
                pipe_id: pipeId,
                source_node: sourceNode,
                target_node: targetNode,
                flow_rate:
                  pipe.flow_rate || "N/A",
                capacity:
                  pipe.capacity ||
                  pipe.pipe_capacity ||
                  "N/A",
                water_level:
                  pipe.water_level || "N/A",
                blockage_probability:
                  pipe.blockage_probability ||
                  pipe.blockage_p ||
                  "N/A",
                blockage_status:
                  blockageStatus,
                overflow_risk:
                  pipe.overflow_risk ||
                  "N/A",
                backflow_risk:
                  pipe.backflow_risk ||
                  "N/A",
                severe: isSevere,
              },

              geometry: {
                type: "LineString",
                coordinates: [
                  nodeCoordinates[sourceNode],
                  nodeCoordinates[targetNode],
                ],
              },
            });

            pipeCount++;
          }
        });

        // =====================================================
        // 6. ADD DRAINAGE NETWORK
        // =====================================================
        map.addSource("drainage-network", {
          type: "geojson",

          data: {
            type: "FeatureCollection",
            features: drainageFeatures,
          },
        });

        // Normal pipes
        map.addLayer({
          id: "normal-drainage-pipes",
          type: "line",
          source: "drainage-network",

          filter: [
            "!=",
            ["get", "severe"],
            true,
          ],

          paint: {
            "line-color": "#138A36",
            "line-width": 4,
            "line-opacity": 0.8,
          },
        });

        // Severe blockage pipes
        map.addLayer({
          id: "severe-drainage-pipes",
          type: "line",
          source: "drainage-network",

          filter: [
            "==",
            ["get", "severe"],
            true,
          ],

          paint: {
            "line-color": "#FF0000",
            "line-width": 6,
            "line-opacity": 0.9,
          },
        });

        // =====================================================
        // 7. PIPE POPUP
        // =====================================================
        const showPipePopup = (e) => {
          if (!e.features || !e.features.length) {
            return;
          }

          const pipe = e.features[0];

          new maplibregl.Popup()
            .setLngLat(e.lngLat)
            .setHTML(`
              <h3>Drainage Pipe</h3>

              <p><b>Pipe ID:</b>
              ${pipe.properties.pipe_id}</p>

              <p><b>From:</b>
              ${pipe.properties.source_node}</p>

              <p><b>To:</b>
              ${pipe.properties.target_node}</p>

              <p><b>Flow Rate:</b>
              ${pipe.properties.flow_rate} LPS</p>

              <p><b>Capacity:</b>
              ${pipe.properties.capacity} LPS</p>

              <p><b>Water Level:</b>
              ${pipe.properties.water_level}</p>

              <p><b>Blockage Probability:</b>
              ${pipe.properties.blockage_probability}</p>

              <p><b>Blockage Status:</b>
              ${pipe.properties.blockage_status}</p>

              <p><b>Overflow Risk:</b>
              ${pipe.properties.overflow_risk}</p>

              <p><b>Backflow Risk:</b>
              ${pipe.properties.backflow_risk}</p>
            `)
            .addTo(map);
        };

        map.on(
          "click",
          "normal-drainage-pipes",
          showPipePopup
        );

        map.on(
          "click",
          "severe-drainage-pipes",
          showPipePopup
        );

        // =====================================================
        // 8. SUCCESS MESSAGE
        // =====================================================
        setMessage(
          `SUCCESS: ${nodeCount} nodes | ${pipeCount} drainage pipes | ${severeBlockageCount} severe blockage pipes`
        );
      } catch (error) {
        console.error(error);

        setMessage(
          `ERROR: ${error.message}`
        );
      }
    });

    return () => {
      nodeMarkersRef.current = [];

      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  // =========================================================
  // DAY 4: UPDATE NODE POPUPS WHEN TIME BUTTON CHANGES
  // =========================================================
  useEffect(() => {
    nodeMarkersRef.current.forEach(
      ({
        markerElement,
        popup,
        node,
        nodeId,
        prediction,
      }) => {
        const selectedDepth =
          getSelectedDepth(
            prediction,
            selectedTime
          );

        // Update popup with selected prediction time
        popup.setHTML(
          createNodePopupHtml(
            node,
            nodeId,
            prediction,
            selectedTime
          )
        );

        // Show selected prediction as tooltip
        markerElement.title =
          `${nodeId} | ${getSelectedTimeLabel(
            selectedTime
          )} | Depth: ${selectedDepth} m`;
      }
    );
  }, [selectedTime]);

  // =========================================================
  // BUTTON STYLE
  // =========================================================
  const getButtonStyle = (time) => ({
    padding: "8px 10px",
    margin: "3px",
    borderRadius: "5px",
    border: "1px solid #555",
    cursor: "pointer",
    fontWeight: "bold",
    background:
      selectedTime === time
        ? "#1976D2"
        : "#F1F1F1",
    color:
      selectedTime === time
        ? "white"
        : "black",
  });

  return (
    <div>
      {/* =====================================================
          INFORMATION PANEL
      ===================================================== */}
      <div
        style={{
          position: "absolute",
          top: "20px",
          left: "20px",
          zIndex: 2,
          background: "white",
          padding: "15px",
          borderRadius: "8px",
          fontWeight: "bold",
          minWidth: "330px",
        }}
      >
        <div
          style={{
            textAlign: "center",
            fontSize: "20px",
          }}
        >
          HydroGraph-Twin
        </div>

        <div
          style={{
            textAlign: "center",
            marginTop: "5px",
          }}
        >
          Velachery Flood Monitoring
        </div>

        <br />

        <div>{message}</div>

        <br />

        <div>🟢 Low Flood Severity</div>
        <div>🟡 Medium Flood Severity</div>
        <div>🟠 High Flood Severity</div>
        <div>🔴 Severe Flood</div>

        <br />

        <div>🟢 Normal Pipe</div>
        <div>🔴 Severe Blockage</div>
      </div>

      {/* =====================================================
          DAY 4 PREDICTION TIME CONTROL
      ===================================================== */}
      <div
        style={{
          position: "absolute",
          top: "400px",
          left: "20px",
          zIndex: 2,
          background: "white",
          padding: "15px",
          borderRadius: "8px",
          minWidth: "330px",
        }}
      >
        <div
          style={{
            fontWeight: "bold",
            marginBottom: "10px",
          }}
        >
          Day 4: Flood Prediction Time
        </div>

        <button
          style={getButtonStyle("current")}
          onClick={() =>
            setSelectedTime("current")
          }
        >
          Current
        </button>

        <button
          style={getButtonStyle("15")}
          onClick={() =>
            setSelectedTime("15")
          }
        >
          +15 min
        </button>

        <button
          style={getButtonStyle("30")}
          onClick={() =>
            setSelectedTime("30")
          }
        >
          +30 min
        </button>

        <button
          style={getButtonStyle("45")}
          onClick={() =>
            setSelectedTime("45")
          }
        >
          +45 min
        </button>

        <div
          style={{
            marginTop: "10px",
            fontWeight: "bold",
          }}
        >
          Selected:{" "}
          {getSelectedTimeLabel(
            selectedTime
          )}
        </div>

        <div
          style={{
            marginTop: "5px",
            fontSize: "13px",
          }}
        >
          Click any node to view the selected
          prediction depth.
        </div>
      </div>

      {/* =====================================================
          MAP
      ===================================================== */}
      <div
        ref={mapContainer}
        style={{
          width: "100vw",
          height: "100vh",
        }}
      />
    </div>
  );
}

export default App;
import { useEffect, useRef, useState } from "react";
import * as maplibregl from "maplibre-gl";
import Papa from "papaparse";
import "maplibre-gl/dist/maplibre-gl.css";

function App() {
  const mapContainer = useRef(null);
  const [message, setMessage] = useState("Loading map...");

  useEffect(() => {
    const map = new maplibregl.Map({
      container: mapContainer.current,
      style: "https://demotiles.maplibre.org/style.json",
      center: [80.22, 12.978],
      zoom: 13,
    });

    map.on("load", async () => {
      try {
        // =========================
        // 1. LOAD STUDY AREA
        // =========================
        const studyResponse = await fetch(
          "/data/study_area.geojson"
        );

        if (!studyResponse.ok) {
          throw new Error(
            "Cannot load study_area.geojson"
          );
        }

        const studyArea =
          await studyResponse.json();

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

        // =========================
        // 2. LOAD ROADS
        // =========================
        const roadsResponse = await fetch(
          "/data/roads.geojson"
        );

        if (!roadsResponse.ok) {
          throw new Error(
            "Cannot load roads.geojson"
          );
        }

        const roads =
          await roadsResponse.json();

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

        // =========================
        // 3. LOAD NODES
        // =========================
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
            // Store coordinates
            nodeCoordinates[nodeId] = [
              longitude,
              latitude,
            ];

            // Add node marker
            new maplibregl.Marker()
              .setLngLat([
                longitude,
                latitude,
              ])
              .setPopup(
                new maplibregl.Popup().setHTML(`
                  <h3>
                    ${
                      node.location_name ||
                      "Unknown Location"
                    }
                  </h3>
                  <p>
                    <b>Node ID:</b> ${nodeId}
                  </p>
                  <p>
                    <b>Type:</b>
                    ${node.node_type || "N/A"}
                  </p>
                  <p>
                    <b>Latitude:</b>
                    ${latitude}
                  </p>
                  <p>
                    <b>Longitude:</b>
                    ${longitude}
                  </p>
                `)
              )
              .addTo(map);

            nodeCount++;
          }
        });

        // =========================
        // 4. LOAD MEMBER 2 DATA
        // =========================
        const visualizationResponse =
          await fetch(
            "/data/member3_drainage_visualization.csv"
          );

        if (!visualizationResponse.ok) {
          throw new Error(
            "Cannot load member3_drainage_visualization.csv"
          );
        }

        const visualizationCsvText =
          await visualizationResponse.text();

        const visualizationResult =
          Papa.parse(
            visualizationCsvText,
            {
              header: true,
              skipEmptyLines: true,
              delimiter: ",",
              transformHeader: (header) =>
                header
                  .trim()
                  .replace(/^\uFEFF/, ""),
            }
          );

        // Store Member 2 data using drainage_id
        const visualizationData = {};

        visualizationResult.data.forEach(
          (item) => {
            const drainageId = String(
              item.drainage_id || ""
            ).trim();

            // Convert Severe_Blockage
            // to Severe Blockage
            const rawStatus = String(
              item.blockage_status || "Normal"
            )
              .trim()
              .replace(/_/g, " ");

            const normalizedStatus =
              rawStatus.toLowerCase() ===
              "severe blockage"
                ? "Severe Blockage"
                : "Normal";

            if (drainageId) {
              visualizationData[drainageId] = {
                flow_rate_lps:
                  item.flow_rate_lps || "N/A",

                capacity_lps:
                  item.capacity_lps || "N/A",

                water_level_cm:
                  item.water_level_cm || "N/A",

                blockage_probability:
                  item.blockage_probability || "0",

                blockage_status:
                  normalizedStatus,

                overflow_risk:
                  item.overflow_risk || "Low",

                backflow_risk:
                  item.backflow_risk || "False",
              };
            }
          }
        );

        // =========================
        // 5. LOAD ORIGINAL
        // DRAINAGE NETWORK
        // =========================
        const drainageResponse =
          await fetch(
            "/data/03_drainage_network.csv"
          );

        if (!drainageResponse.ok) {
          throw new Error(
            "Cannot load 03_drainage_network.csv"
          );
        }

        const drainageCsvText =
          await drainageResponse.text();

        const drainageResult =
          Papa.parse(
            drainageCsvText,
            {
              header: true,
              skipEmptyLines: true,
              delimiter: ",",
              transformHeader: (header) =>
                header
                  .trim()
                  .replace(/^\uFEFF/, ""),
            }
          );

        const drainageFeatures = [];
        let pipeCount = 0;
        let severeCount = 0;

        drainageResult.data.forEach(
          (pipe) => {
            const pipeId = String(
              pipe.pipe_id || ""
            ).trim();

            const sourceNode = String(
              pipe.source_node || ""
            ).trim();

            const targetNode = String(
              pipe.target_node || ""
            ).trim();

            // Match Member 2 data
            const visualData =
              visualizationData[pipeId] || {};

            if (
              pipeId &&
              nodeCoordinates[sourceNode] &&
              nodeCoordinates[targetNode]
            ) {
              const blockageStatus =
                visualData.blockage_status ||
                "Normal";

              if (
                blockageStatus ===
                "Severe Blockage"
              ) {
                severeCount++;
              }

              drainageFeatures.push({
                type: "Feature",

                properties: {
                  pipe_id: pipeId,
                  source_node: sourceNode,
                  target_node: targetNode,

                  flow_rate_lps:
                    visualData.flow_rate_lps ||
                    "N/A",

                  capacity_lps:
                    visualData.capacity_lps ||
                    "N/A",

                  water_level_cm:
                    visualData.water_level_cm ||
                    "N/A",

                  blockage_probability:
                    visualData.blockage_probability ||
                    "0",

                  blockage_status:
                    blockageStatus,

                  overflow_risk:
                    visualData.overflow_risk ||
                    "Low",

                  backflow_risk:
                    visualData.backflow_risk ||
                    "False",
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
          }
        );

        // =========================
        // 6. ADD DRAINAGE SOURCE
        // =========================
        map.addSource("drainage-network", {
          type: "geojson",
          data: {
            type: "FeatureCollection",
            features: drainageFeatures,
          },
        });

        // =========================
        // 7. ADD COLORED PIPES
        // =========================
        map.addLayer({
          id: "drainage-pipes",
          type: "line",
          source: "drainage-network",

          paint: {
            "line-width": [
              "match",
              ["get", "blockage_status"],
              "Severe Blockage",
              7,
              4,
            ],

            "line-opacity": 0.9,

            "line-color": [
              "match",
              ["get", "blockage_status"],
              "Severe Blockage",
              "#ff0000",
              "#008000",
            ],
          },
        });

        // =========================
        // 8. CLICK PIPE
        // SHOW MEMBER 2 DETAILS
        // =========================
        map.on(
          "click",
          "drainage-pipes",
          (event) => {
            const feature =
              event.features?.[0];

            if (!feature) return;

            const properties =
              feature.properties;

            new maplibregl.Popup()
              .setLngLat(event.lngLat)
              .setHTML(`
                <h3>
                  Drainage Pipe:
                  ${properties.pipe_id}
                </h3>

                <p>
                  <b>From:</b>
                  ${properties.source_node}
                </p>

                <p>
                  <b>To:</b>
                  ${properties.target_node}
                </p>

                <p>
                  <b>Flow Rate:</b>
                  ${properties.flow_rate_lps} LPS
                </p>

                <p>
                  <b>Capacity:</b>
                  ${properties.capacity_lps} LPS
                </p>

                <p>
                  <b>Water Level:</b>
                  ${properties.water_level_cm} cm
                </p>

                <p>
                  <b>Blockage Probability:</b>
                  ${properties.blockage_probability}
                </p>

                <p>
                  <b>Blockage Status:</b>
                  ${properties.blockage_status}
                </p>

                <p>
                  <b>Overflow Risk:</b>
                  ${properties.overflow_risk}
                </p>

                <p>
                  <b>Backflow Risk:</b>
                  ${properties.backflow_risk}
                </p>
              `)
              .addTo(map);
          }
        );

        // =========================
        // 9. CHANGE CURSOR
        // =========================
        map.on(
          "mouseenter",
          "drainage-pipes",
          () => {
            map.getCanvas().style.cursor =
              "pointer";
          }
        );

        map.on(
          "mouseleave",
          "drainage-pipes",
          () => {
            map.getCanvas().style.cursor =
              "";
          }
        );

        // =========================
        // 10. SUCCESS MESSAGE
        // =========================
        setMessage(
          `SUCCESS: ${nodeCount} nodes | ${pipeCount} drainage pipes | ${severeCount} severe blockage pipes`
        );
      } catch (error) {
        console.error(error);
        setMessage(
          `ERROR: ${error.message}`
        );
      }
    });

    return () => map.remove();
  }, []);

  return (
    <div>
      {/* INFORMATION PANEL */}
      <div
        style={{
          position: "absolute",
          top: "20px",
          left: "20px",
          zIndex: 1,
          background: "white",
          padding: "15px",
          borderRadius: "8px",
          fontWeight: "bold",
        }}
      >
        <div>HydroGraph-Twin</div>

        <div>
          Velachery Flood Monitoring
        </div>

        <br />

        <div>{message}</div>

        <br />

        <div>🟢 Normal Pipe</div>
        <div>🔴 Severe Blockage</div>
      </div>

      {/* MAP */}
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
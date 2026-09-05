const pool =
    require("../db/database");

const {
    runRouting
} =
    require("./routingService");


// ============================================================
// GENERATE FLOOD-AWARE ROUTE
// ============================================================

const generateRoute =
    async (req, res) => {

        try {

            const {
                assignment_id
            } = req.params;


            // ------------------------------------------------
            // Get worker + task from PostgreSQL
            // ------------------------------------------------

            const result =
                await pool.query(

                    `SELECT

                        a.assignment_id,

                        w.worker_id,
                        w.worker_name,
                        w.latitude AS worker_latitude,
                        w.longitude AS worker_longitude,

                        t.task_id,
                        t.node_id,
                        t.latitude AS task_latitude,
                        t.longitude AS task_longitude,
                        t.severity,
                        t.priority_score

                    FROM assignments a

                    JOIN workers w
                    ON a.worker_id =
                       w.worker_id

                    JOIN tasks t
                    ON a.task_id =
                       t.task_id

                    WHERE
                        a.assignment_id = $1`,

                    [
                        assignment_id
                    ]

                );


            // ------------------------------------------------
            // Assignment not found
            // ------------------------------------------------

            if (
                result.rows.length === 0
            ) {

                return res
                    .status(404)
                    .json({

                        success: false,

                        error:
                            "Assignment not found"

                    });

            }


            const row =
                result.rows[0];


            // ------------------------------------------------
            // Worker
            // ------------------------------------------------

            const worker = {

                worker_id:
                    row.worker_id,

                worker_name:
                    row.worker_name,

                latitude:
                    Number(
                        row.worker_latitude
                    ),

                longitude:
                    Number(
                        row.worker_longitude
                    )

            };


            // ------------------------------------------------
            // Destination
            // ------------------------------------------------

            const task = {

                task_id:
                    row.task_id,

                node_id:
                    row.node_id,

                latitude:
                    Number(
                        row.task_latitude
                    ),

                longitude:
                    Number(
                        row.task_longitude
                    ),

                severity:
                    row.severity,

                priority_score:
                    row.priority_score

            };


            // ------------------------------------------------
            // Flooded road segments
            //
            // These are prototype/test values.
            //
            // Later your flood prediction member
            // can send these automatically.
            // ------------------------------------------------

            const floodedEdges =
                req.body?.flooded_edges || [];


            // ------------------------------------------------
            // Run Python A*
            // ------------------------------------------------

            const routingResult =
                await runRouting(

                    worker,

                    task,

                    floodedEdges

                );


            // ------------------------------------------------
            // Check routing result
            // ------------------------------------------------

            if (
                !routingResult.success
            ) {

                return res
                    .status(500)
                    .json({

                        success: false,

                        error:
                            routingResult.error

                    });

            }


            // ------------------------------------------------
            // Convert route to text
            // ------------------------------------------------

            const routeText =
                routingResult.route
                    .join(" -> ");


            // ------------------------------------------------
            // Save route in PostgreSQL
            // ------------------------------------------------

            await pool.query(

                `UPDATE assignments

                 SET route = $1

                 WHERE assignment_id = $2`,

                [

                    routeText,

                    assignment_id

                ]

            );


            // ------------------------------------------------
            // Send response to frontend
            // ------------------------------------------------

            res.json({

                success: true,

                assignment_id:
                    assignment_id,

                worker: {

                    worker_id:
                        worker.worker_id,

                    worker_name:
                        worker.worker_name,

                    latitude:
                        worker.latitude,

                    longitude:
                        worker.longitude

                },

                destination: {

                    task_id:
                        task.task_id,

                    node_id:
                        task.node_id,

                    latitude:
                        task.latitude,

                    longitude:
                        task.longitude,

                    severity:
                        task.severity,

                    priority_score:
                        task.priority_score

                },

                route:
                    routingResult.route,

                route_text:
                    routeText,

                route_coordinates:
                    routingResult.route_coordinates,

                flooded_segments:
                    routingResult.flooded_segments

            });

        }

        catch (error) {

            console.error(
                "Routing error:",
                error
            );


            res.status(500).json({

                success: false,

                error:
                    error.message

            });

        }

    };


module.exports = {
    generateRoute
};
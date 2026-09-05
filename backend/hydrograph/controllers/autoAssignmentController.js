const pool = require("../db/database");

const {
    runOptimizer
} = require("./assignmentService");


const autoAssign = async (req, res) => {

    try {

        // 1. Get available and idle workers
        const workersResult = await pool.query(
            `SELECT
                worker_id,
                latitude,
                longitude
             FROM workers
             WHERE availability = 'Available'
             AND status = 'Idle'
             AND latitude IS NOT NULL
             AND longitude IS NOT NULL`
        );


        // 2. Get pending and unassigned tasks
        const tasksResult = await pool.query(
            `SELECT
                task_id,
                node_id,
                latitude,
                longitude,
                priority_score,
                severity,
                deadline_minutes
             FROM tasks
             WHERE status = 'Pending'
             AND assigned_worker_id IS NULL
             AND latitude IS NOT NULL
             AND longitude IS NOT NULL
             ORDER BY priority_score DESC`
        );


        const workers = workersResult.rows;
        const tasks = tasksResult.rows;


        // 3. Check workers
        if (workers.length === 0) {

            return res.status(400).json({
                error: "No available workers found."
            });

        }


        // 4. Check tasks
        if (tasks.length === 0) {

            return res.status(400).json({
                error: "No pending tasks found."
            });

        }


        // 5. Send workers and tasks to Python OR-Tools optimizer
        const optimizerResult =
            await runOptimizer(
                workers,
                tasks
            );


        // 6. Check optimizer result
        if (!optimizerResult.success) {

            return res.status(500).json({
                error: optimizerResult.error
            });

        }


        const assignments =
            optimizerResult.assignments;


        // 7. Connect to PostgreSQL
        const client =
            await pool.connect();


        try {

            // Start database transaction
            await client.query("BEGIN");


            const savedAssignments = [];


            // 8. Save every assignment
            for (const item of assignments) {

                const workerId =
                    item.worker_id;

                const taskId =
                    item.task_id;


                // Create unique assignment ID
                const assignmentId =
                    "A" +
                    Date.now().toString().slice(-6) +
                    Math.floor(Math.random() * 1000);


                // Create assignment record
                const assignmentResult =
                    await client.query(
                        `INSERT INTO assignments
                        (
                            assignment_id,
                            worker_id,
                            task_id,
                            assigned_at,
                            route,
                            status
                        )
                        VALUES
                        ($1, $2, $3, NOW(), NULL, 'Active')
                        RETURNING *`,

                        [
                            assignmentId,
                            workerId,
                            taskId
                        ]
                    );


                // Update task
                await client.query(
                    `UPDATE tasks
                     SET
                        assigned_worker_id = $1,
                        status = 'Assigned'
                     WHERE task_id = $2`,

                    [
                        workerId,
                        taskId
                    ]
                );


                // Update worker
                await client.query(
                    `UPDATE workers
                     SET
                        current_task_id = $1,
                        status = 'On Route'
                     WHERE worker_id = $2`,

                    [
                        taskId,
                        workerId
                    ]
                );


                savedAssignments.push(
                    assignmentResult.rows[0]
                );

            }


            // Save all database changes
            await client.query("COMMIT");


            return res.json({

                success: true,

                message:
                    "Workers assigned successfully",

                assignments:
                    savedAssignments

            });


        } catch (error) {

            // Undo changes if an error happens
            await client.query("ROLLBACK");

            throw error;

        } finally {

            // Release PostgreSQL connection
            client.release();

        }


    } catch (error) {

        console.error(
            "Automatic assignment error:",
            error
        );


        return res.status(500).json({

            success: false,

            error: error.message

        });

    }

};


module.exports = {
    autoAssign
};
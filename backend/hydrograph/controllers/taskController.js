const pool = require("../db/database");


// GET ALL TASKS
const getTasks = async (req, res) => {

    try {

        const result = await pool.query(
            "SELECT * FROM tasks ORDER BY priority_score DESC"
        );

        res.json(result.rows);

    } catch (error) {

        console.error(error);

        res.status(500).json({
            error: error.message
        });

    }
};


// CREATE TASK
const createTask = async (req, res) => {

    try {

        const {
            task_id,
            node_id,
            latitude,
            longitude,
            priority_score,
            severity,
            deadline_minutes
        } = req.body;

        if (!task_id || !node_id) {

            return res.status(400).json({
                error: "task_id and node_id are required"
            });

        }

        const result = await pool.query(
            `INSERT INTO tasks
            (
                task_id,
                node_id,
                latitude,
                longitude,
                priority_score,
                severity,
                deadline_minutes,
                status
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
            RETURNING *`,

            [
                task_id,
                node_id,
                latitude ?? null,
                longitude ?? null,
                priority_score ?? null,
                severity ?? null,
                deadline_minutes ?? null,
                "pending"
            ]
        );

        res.status(201).json(result.rows[0]);

    } catch (error) {

        console.error(error);

        res.status(500).json({
            error: error.message
        });

    }
};


module.exports = {
    getTasks,
    createTask
};
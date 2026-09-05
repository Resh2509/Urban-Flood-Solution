const pool = require("../db/database");


// GET ALL ASSIGNMENTS
const getAssignments = async (req, res) => {

    try {

        const result = await pool.query(
            `SELECT *
             FROM assignments
             ORDER BY assigned_at DESC`
        );

        res.json(result.rows);

    } catch (error) {

        console.error("Error fetching assignments:", error);

        res.status(500).json({
            error: error.message
        });

    }
};


// CREATE ASSIGNMENT
const createAssignment = async (req, res) => {

    try {

        const {
            worker_id,
            task_id,
            route,
            status
        } = req.body;


        if (!worker_id || !task_id) {

            return res.status(400).json({
                error: "worker_id and task_id are required"
            });

        }


        const result = await pool.query(
            `INSERT INTO assignments
            (
                worker_id,
                task_id,
                route,
                status
            )
            VALUES ($1, $2, $3, $4)
            RETURNING *`,

            [
                worker_id,
                task_id,
                route ?? null,
                status ?? "Active"
            ]
        );


        res.status(201).json(result.rows[0]);

    } catch (error) {

        console.error("Error creating assignment:", error);

        res.status(500).json({
            error: error.message
        });

    }
};


module.exports = {
    getAssignments,
    createAssignment
};
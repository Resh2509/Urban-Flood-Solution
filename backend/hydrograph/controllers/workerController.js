const pool = require("../db/database");


// GET ALL WORKERS
const getWorkers = async (req, res) => {

    try {

        const result = await pool.query(
            "SELECT * FROM workers ORDER BY worker_id"
        );

        res.json(result.rows);

    } catch (error) {

        console.error("Error fetching workers:", error);

        res.status(500).json({
            error: error.message
        });

    }
};


// GET ONE WORKER
const getWorker = async (req, res) => {

    try {

        const result = await pool.query(
            "SELECT * FROM workers WHERE worker_id = $1",
            [req.params.worker_id]
        );

        if (result.rows.length === 0) {

            return res.status(404).json({
                error: "Worker not found"
            });

        }

        res.json(result.rows[0]);

    } catch (error) {

        console.error("Error fetching worker:", error);

        res.status(500).json({
            error: error.message
        });

    }
};


// CREATE WORKER
const createWorker = async (req, res) => {

    try {

        const {
            worker_id,
            worker_name,
            phone_number,
            latitude,
            longitude,
            availability,
            status,
            current_task_id
        } = req.body;


        if (!worker_id) {

            return res.status(400).json({
                error: "worker_id is required"
            });

        }


        const result = await pool.query(
            `INSERT INTO workers
            (
                worker_id,
                worker_name,
                phone_number,
                latitude,
                longitude,
                availability,
                status,
                current_task_id
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
            RETURNING *`,

            [
                worker_id,
                worker_name ?? null,
                phone_number ?? null,
                latitude ?? null,
                longitude ?? null,
                availability ?? true,
                status ?? "available",
                current_task_id ?? null
            ]
        );


        res.status(201).json(result.rows[0]);

    } catch (error) {

        console.error("Error creating worker:", error);

        res.status(500).json({
            error: error.message
        });

    }
};


// UPDATE WORKER
const updateWorker = async (req, res) => {

    try {

        const {
            worker_name,
            phone_number,
            latitude,
            longitude,
            availability,
            status,
            current_task_id
        } = req.body;


        const result = await pool.query(
            `UPDATE workers
             SET
                worker_name = COALESCE($1, worker_name),
                phone_number = COALESCE($2, phone_number),
                latitude = COALESCE($3, latitude),
                longitude = COALESCE($4, longitude),
                availability = COALESCE($5, availability),
                status = COALESCE($6, status),
                current_task_id = $7

             WHERE worker_id = $8

             RETURNING *`,

            [
                worker_name,
                phone_number,
                latitude,
                longitude,
                availability,
                status,
                current_task_id,
                req.params.worker_id
            ]
        );


        if (result.rows.length === 0) {

            return res.status(404).json({
                error: "Worker not found"
            });

        }


        res.json(result.rows[0]);

    } catch (error) {

        console.error("Error updating worker:", error);

        res.status(500).json({
            error: error.message
        });

    }
};


// DELETE WORKER
const deleteWorker = async (req, res) => {

    try {

        const result = await pool.query(
            "DELETE FROM workers WHERE worker_id = $1 RETURNING *",
            [req.params.worker_id]
        );


        if (result.rows.length === 0) {

            return res.status(404).json({
                error: "Worker not found"
            });

        }


        res.json({
            message: "Worker deleted successfully"
        });

    } catch (error) {

        console.error("Error deleting worker:", error);

        res.status(500).json({
            error: error.message
        });

    }
};


module.exports = {
    getWorkers,
    getWorker,
    createWorker,
    updateWorker,
    deleteWorker
};
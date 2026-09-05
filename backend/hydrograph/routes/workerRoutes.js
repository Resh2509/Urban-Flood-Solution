const express = require("express");

const {
    getWorkers,
    getWorker,
    createWorker,
    updateWorker,
    deleteWorker
} = require("../controllers/workerController");

const router = express.Router();


// GET ALL WORKERS
router.get("/", getWorkers);


// GET ONE WORKER
router.get("/:worker_id", getWorker);


// CREATE WORKER
router.post("/", createWorker);


// UPDATE WORKER
router.patch("/:worker_id", updateWorker);


// DELETE WORKER
router.delete("/:worker_id", deleteWorker);


module.exports = router;
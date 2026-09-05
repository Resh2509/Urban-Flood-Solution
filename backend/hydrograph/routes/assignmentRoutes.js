const express = require("express");

const {
    getAssignments,
    createAssignment
} = require("../controllers/assignmentController");

const router = express.Router();


// GET ALL ASSIGNMENTS
router.get("/", getAssignments);


// CREATE ASSIGNMENT
router.post("/", createAssignment);


module.exports = router;
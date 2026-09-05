const express = require("express");

const {
    autoAssign
} = require("../controllers/autoAssignmentController");


const router = express.Router();


router.post(
    "/",
    autoAssign
);


module.exports = router;
const express = require("express");

const router = express.Router();

const {
    createNotification
} = require("../controllers/notificationController");


// Create notification + send SMS
router.post(
    "/send",
    createNotification
);


module.exports = router;
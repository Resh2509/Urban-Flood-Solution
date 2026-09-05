require("dotenv").config();

const express = require("express");
const cors = require("cors");

const taskRoutes = require("./routes/taskRoutes");
const workerRoutes = require("./routes/workerRoutes");
const assignmentRoutes = require("./routes/assignmentRoutes");
const autoAssignmentRoutes = require("./routes/autoAssignmentRoutes");
const routingRoutes =require("./routes/routingRoutes");
const app = express();
const notificationRoutes = require("./routes/notificationRoutes");

app.use(express.static("public"));

// Middleware
app.use(cors());
app.use(express.json());

// Home
app.get("/", (req, res) => {
    res.json({
        message: "HydroGraph-Twin HydroGraph API"
    });
});


// APIs
app.use("/api/tasks", taskRoutes);

app.use("/api/workers", workerRoutes);

app.use("/api/assignments", assignmentRoutes);

app.use("/api/auto-assign",autoAssignmentRoutes);

app.use("/api/routes",routingRoutes);

app.use("/api/notifications", notificationRoutes);

// Start server
const PORT = 3000;

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
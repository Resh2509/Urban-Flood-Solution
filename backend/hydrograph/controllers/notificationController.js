const pool = require("../db/database");
const { sendSMS } = require("../services/smsService");

const createNotification = async (req, res) => {
    try {

        const {
            worker_id,
            task_id,
            message
        } = req.body;

        // Get worker phone number
        const workerResult = await pool.query(
            `SELECT worker_name, phone_number
             FROM workers
             WHERE worker_id = $1`,
            [worker_id]
        );

        if (workerResult.rows.length === 0) {
            return res.status(404).json({
                error: "Worker not found"
            });
        }

        const worker = workerResult.rows[0];

        // Send SMS
        let smsStatus = "Failed";
        let smsSid = null;

        try {

            const sms = await sendSMS(
                worker.phone_number,
                message
            );

            smsStatus = "Sent";
            smsSid = sms.sid;

        } catch (smsError) {

            console.error(
                "SMS failed:",
                smsError.message
            );

        }

        res.status(201).json({
            success: true,
            worker_id,
            worker_name: worker.worker_name,
            phone_number: worker.phone_number,
            message,
            sms_status: smsStatus,
            sms_sid: smsSid
        });

    } catch (error) {

        console.error(error);

        res.status(500).json({
            error: "Notification failed",
            details: error.message
        });
    }
};

module.exports = {
    createNotification
};
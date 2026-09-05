require("dotenv").config();

const { sendSMS } = require("./hydrograph/services/smsService");

async function testSMS() {
    try {
        const result = await sendSMS(
            "+919840660555",
            "HYDROGRAPH TEST ALERT: SMS is working!"
        );

        console.log("SMS SENT SUCCESSFULLY!");
        console.log("SID:", result.sid);

    } catch (error) {
        console.error("SMS FAILED!");
        console.error(error.message);
    }
}

testSMS();
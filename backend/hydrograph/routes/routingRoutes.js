const express =
    require("express");


const {
    generateRoute
} =
    require(
        "../controllers/routingController"
    );


const router =
    express.Router();


router.post(
    "/:assignment_id",
    generateRoute
);


module.exports =
    router;
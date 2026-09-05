const { spawn } = require("child_process");
const path = require("path");


function runOptimizer(workers, tasks) {

    return new Promise((resolve, reject) => {

        const scriptPath = path.join(
            __dirname,
            "..",
            "optimizer",
            "assignment_optimizer.py"
        );


        const python = spawn(
            "python",
            [scriptPath]
        );


        let output = "";
        let errorOutput = "";


        python.stdout.on("data", (data) => {

            output += data.toString();

        });


        python.stderr.on("data", (data) => {

            errorOutput += data.toString();

        });


        python.on("close", (code) => {

            if (code !== 0) {

                return reject(
                    new Error(
                        errorOutput ||
                        "Optimizer failed"
                    )
                );

            }


            try {

                const result = JSON.parse(output);

                resolve(result);

            } catch (error) {

                reject(
                    new Error(
                        "Invalid optimizer response: " +
                        output
                    )
                );

            }

        });


        python.stdin.write(
            JSON.stringify({
                workers: workers,
                tasks: tasks
            })
        );


        python.stdin.end();

    });

}


module.exports = {
    runOptimizer
};
const { spawn } = require("child_process");
const path = require("path");


function runRouting(
    worker,
    task,
    floodedEdges
) {

    return new Promise(
        (resolve, reject) => {

            const scriptPath =
                path.join(
                    __dirname,
                    "..",
                    "optimizer",
                    "routing_service.py"
                );


            const python =
                spawn(
                    "python",
                    [scriptPath]
                );


            let output = "";

            let errorOutput = "";


            // Python stdout

            python.stdout.on(
                "data",
                (data) => {

                    output +=
                        data.toString();

                }
            );


            // Python stderr

            python.stderr.on(
                "data",
                (data) => {

                    errorOutput +=
                        data.toString();

                }
            );


            // Python finished

            python.on(
                "close",
                (code) => {

                    if (code !== 0) {

                        return reject(
                            new Error(
                                errorOutput ||
                                "Python routing failed"
                            )
                        );

                    }


                    try {

                        const result =
                            JSON.parse(
                                output.trim()
                            );


                        resolve(result);

                    }

                    catch (error) {

                        reject(
                            new Error(
                                "Invalid Python response: "
                                +
                                output
                            )
                        );

                    }

                }
            );


            // Send data to Python

            python.stdin.write(

                JSON.stringify({

                    worker: worker,

                    task: task,

                    flooded_edges:
                        floodedEdges

                })

            );


            python.stdin.end();

        }
    );
}


module.exports = {
    runRouting
};
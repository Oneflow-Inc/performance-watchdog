// https://docs.aws.amazon.com/sdk-for-javascript/v3/developer-guide/cloudwatch-examples-getting-metrics.html
// Import required AWS SDK clients and commands for Node.js
const {
    CloudWatchClient,
    PutMetricDataCommand,
} = require("@aws-sdk/client-cloudwatch");

// Set the AWS Region
const REGION = "cn-northwest-1"; //e.g. "us-east-1"

// Set the parameters
const params = {
    MetricData: [
        {
            MetricName: "Throughput",
            Dimensions: [
                {
                    Name: "Model",
                    Value: "ResNet50",
                },
            ],
            Unit: "None",
            Value: 100.0,
        },
    ],
    Namespace: "OneFlow/Performance",
};

// Create CloudWatch service object
const cw = new CloudWatchClient({ region: REGION });

const run = async () => {
    try {
        const data = await cw.send(new PutMetricDataCommand(params));
        console.log("Success", data.$metadata.requestId);
    } catch (err) {
        console.log("Error", err);
    }
};
run();

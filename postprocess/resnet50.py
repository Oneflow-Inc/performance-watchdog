import sys
import re
import argparse
import subprocess
import statistics

parser = argparse.ArgumentParser()
parser.add_argument("--stdin", default=False, action="store_true", required=False)
parser.add_argument("--test", default=False, action="store_true", required=False)
parser.add_argument("--upload_cw", default=False, action="store_true", required=False)
parser.add_argument("--model", type=str, required=True)
parser.add_argument("--branch", type=str, required=True)
parser.add_argument("--gpu_num_per_node", type=int, required=True)
args = parser.parse_args()


def get_gpu_name():
    return (
        subprocess.check_output(
            "nvidia-smi --query-gpu=name --id=0 --format=csv,noheader", shell=True
        )
        .decode()
        .strip()
    )


def process_one_line(line: str):
    print("[log]", line.strip())
    if "train" in line:
        throughput = re.search("samples/s: (.+?)\s", line.strip())
        if throughput is not None:
            throughput = float(throughput.group(1))
            print("[throughput]", throughput)
            return {"throughput": throughput}


def test():
    example = "train: epoch 0, iter 16, loss: 7.191658, top_1: 0.000000, top_k: 0.013889, samples/s: 147.423 1617360674.1762571"
    process_one_line(example)


if args.stdin:
    throughputs = []
    for line in sys.stdin:
        processed = process_one_line(line)
        if processed is not None:
            throughputs.append(processed["throughput"])
    if args.upload_cw:
        import boto3
        from botocore.config import Config

        my_config = Config(
            region_name="cn-northwest-1",
            signature_version="v4",
            retries={"max_attempts": 10, "mode": "standard"},
        )
        # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html
        client = boto3.client("cloudwatch", config=my_config)
        response = client.put_metric_data(
            Namespace="OneFlow/Performance",
            MetricData=[
                {
                    "MetricName": "Throughput",
                    "Dimensions": [
                        {"Name": "Model", "Value": args.model,},
                        {"Name": "Branch", "Value": args.branch,},
                        {"Name": "GPU", "Value": get_gpu_name(),},
                        {
                            "Name": "GPU Number per Node",
                            "Value": str(args.gpu_num_per_node),
                        },
                    ],
                    "Unit": "None",
                    "Value": statistics.median(throughputs),
                },
            ],
        )
        print(response)

if args.test:
    test()

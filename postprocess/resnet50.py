import sys
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--stdin", default=False, action="store_true", required=False)
parser.add_argument("--test", default=False, action="store_true", required=False)
args = parser.parse_args()


def process_one_line(line: str):
    if "train" in line:
        print("[process]", line.strip())
        throughput = re.search("samples/s: (.+?)\s", line.strip())
        if throughput is not None:
            throughput = float(throughput.group(1))
            print("[throughput]", throughput)
    else:
        print("[ignore]", line.strip())


def test():
    example = "train: epoch 0, iter 16, loss: 7.191658, top_1: 0.000000, top_k: 0.013889, samples/s: 147.423 1617360674.1762571"
    process_one_line(example)


if args.stdin:
    for line in sys.stdin:
        process_one_line(line)
if args.test:
    test()

import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(usage='python3 dirscan.py --target [source urls file] --path [dict file]')
    parser.add_argument("--target", type=str, help="target urls file.")
    parser.add_argument("--path", type=str, help="path file.")
    # parser.add_argument("--coros", "-c", default=COROS_NUM, type=int, help="coros num")
    if len(sys.argv) == 1:
        sys.argv.append("-h")
    args = parser.parse_args()
    return args

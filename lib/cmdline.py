import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(usage='python3 dirscan.py --target [source urls file] --path [dict file]')
    parser.add_argument("--target", type=str, help="target urls file.")
    parser.add_argument("--dirs", type=str, help="dir dict path.")
    parser.add_argument("--filenames", type=str, help="filename dict path")
    if len(sys.argv) == 1:
        sys.argv.append("-h")
    args = parser.parse_args()
    return args

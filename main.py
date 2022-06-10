import os
import argparse
from art import *
from updater import Updater


if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--directory", default=os.getcwd(),
                    help="Cesta k PP2 projektu  (defaultne aktualni slozka)")
    args = ap.parse_args()

    Updater(pp2_line_dir=args.directory)

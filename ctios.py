#!/usr/bin/env python3

import argparse

from ctios import CtiOs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='...')
    parser.add_argument('--user', help="Username", required=True)

    args = parser.parse_args()

    co = CtiOs(args.user)

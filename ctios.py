#!/usr/bin/env python3

import argparse
import getpass
import sys

from ctios import CtiOs
from ctios.exceptions import CtiOsError


def main():
    parser = argparse.ArgumentParser(description='...')

    parser.add_argument(
        '--user',
        help="Username",
        required=True)
    parser.add_argument(
        '--password',
        help="Password",
        required=False)
    parser.add_argument(
        '--posidents',
        help="Limit posidents (if not specified than all posidents from db are processed)",
        required=False)
    parser.add_argument(
        '--logdir',
        help="Log directory",
        required=False)
    parser.add_argument(
        '--db',
        help="Database produced by GDAL from input VFK file",
        required=True)

    args = parser.parse_args()

    if not args.password:
      args.password = getpass.getpass(prompt='Password? ')

    # Set up CtiOs reader
    try:
        co = CtiOs(args.user, args.password)
    except CtiOsError as e:
        sys.exit(e)

    # Set db
    try:
        co.set_db(args.db)
    except CtiOsError as e:
        sys.exit(e)

    # Set log directory (logs are not generated when no logdir specified)
    if args.logdir:
        co.set_log_file(args.logdir)

    # Set input posidents from file or db
    try:
        if args.posidents:
            co.set_posidents_from_file(args.posidents)
        else:
            co.set_posidents_from_db()
    except CtiOsError as e:
        sys.exit(e)

    # Send query
    try:
        co.query_requests()
    except CtiOsError as e:
        sys.exit(e)

    return 0

if __name__ == "__main__":
    sys.exit(main())


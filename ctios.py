#!/usr/bin/env python3

import argparse
import getpass
import sys

from ctios import CtiOs
from ctios.exceptions import CtiOsError

def main():
    parser = argparse.ArgumentParser(description='...')

    parser.add_argument('--user', help="Username", required=True)
    parser.add_argument('--password', help="Password", required=False)
    parser.add_argument('--limit', help="Limit", required=False)
    parser.add_argument('--logfile', help="Log File", required=False)
    parser.add_argument('--db', help="Database", required=True)

    args = parser.parse_args()

    if not args.password:
        # TODO: ask for password
        args.password = getpass.getpass(prompt='Password? ')

    # Constructor
    co = CtiOs(args.user, args.password)

    # Set log file
    co.set_log_file(args.logfile)

    # Set input
    if args.limit:
        try:
            co.set_ids(args.limit)
        except CtiOsError as e:
            sys.exit(e)

    # Set output
    co.set_db(args.db)

    # Send query
    co.query_service()

if __name__ == "__main__":
    sys.exit(main())

# ctios.py --user WSTEST --password WSHESLO --limit D:\Projekty\projekty2019\CTI_OS\posidents_1-4.txt --logfile D:\Projekty\projekty2019\CTI_OS --db D:\Projekty\projekty2019\CTI_OS\Export_1-4.db



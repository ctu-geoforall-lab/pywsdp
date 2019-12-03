#!/usr/bin/env python3

import argparse
import getpass
import sys

from ctios import CtiOs
from ctios.exceptions import CtiOsError


def main():
    parser = argparse.ArgumentParser(description='Knihovna pyctios umožňuje k předdefinované množině oprávněných subjektů získat osobní údaje. Využívá k tomu službu ČTIOS, která byla vytvořena na základě nařízení Evropské unie o zpracovávání osobních údajů. Upozornění: Získávání osobních údajů skrze službu ČTIOS je ze strany ČÚZK logováno.')

    parser.add_argument(
       '--user',
       help="Username",
       required=True)
    parser.add_argument(
       '--password',
       help="Password",
       required=False)
    parser.add_argument(
       '--sql',
       help="Limit posidents by sql query (if not specified than all posidents from db are processed)",
       required=False)
    parser.add_argument(
       '--logdir',
       help="Log directory",
       required=False)
    parser.add_argument(
       '--db',
       help="Database produced by GDAL from input VFK file",
       required=True)
    parser.add_argument(
        '--config',
        help="Config file for service and path configuration",
        required=False)

    args = parser.parse_args()

    if not args.password:
        args.password = getpass.getpass(prompt='Password? ')

    # Set up CtiOs reader
    try:
        co = CtiOs(args.user, args.password, args.config)
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
        co.set_posidents_from_db(args.sql)
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



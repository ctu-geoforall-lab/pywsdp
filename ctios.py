#!/usr/bin/env python3

import argparse
import getpass
import sys

from ctios import CtiOs
from ctios.exceptions import CtiOsError
from ctios.logger import Logger


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
       help="Limit posidents by sql query (if not specified than all ids from db are processed)",
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
        co = CtiOs(args.user, args.password, args.config, args.logdir)
    except CtiOsError as e:
        return 1

    # Set db
    try:
        db_path = co.set_db(args.db)
    except CtiOsError as e:
        return 1

    # Set input ids from file or db
    try:
        ids = co.set_ids_from_db(db_path, args.sql)
    except (CtiOsError, CtiOsDbError)  as e:
        return 1

    # Send query
    try:
        co.query_requests(ids, db_path)
    except CtiOsError as e:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())



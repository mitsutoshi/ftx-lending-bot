import os
import argparse
from datetime import datetime
import logging.config
from logging import getLogger, StreamHandler, Formatter, INFO

from ftx import Ftx

from influxdb import InfluxDBClient


logging.config.fileConfig("logging.conf")
logger = getLogger(__name__)


def conv(t, coin, size):
    logger.info(f"point: coin={coin}, size={size}")
    return {'measurement': 'borrow_summary',
            'time': t,
            'tags': {'coin': coin},
            'fields': {'size': size}}


def main():

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--coin', type=str, required=True,
            dest='coin', nargs='*',  help='Coin name such as USD, BTC, etc.')
    args = parser.parse_args()

    # get borrow_summary
    logger.info(f"Start getting the borrow summary. {args.coin}")
    result = Ftx().spot_margin_borrow_summary()

    # write data
    now = datetime.utcnow()
    points = [conv(now, r['coin'], r['size']) for r in result if r['coin'] in args.coin]
    idb = InfluxDBClient(os.environ['DB_HOST'], os.environ['DB_PORT'],
            os.getenv('DB_USER'), os.getenv('DB_PASS'), os.environ['DB_NAME'])
    idb.write_points(points)
    logger.info(f"IDB client have written {len(points)} records.")
    logger.info("End.")


if __name__ == '__main__':
    main()

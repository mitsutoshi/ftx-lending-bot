import os
from datetime import datetime
from logging import getLogger, StreamHandler, Formatter, INFO

from ftx import Ftx
from influxdb import InfluxDBClient


coins = ['USD', 'USDT']

logger = getLogger(__name__)
logger.setLevel(INFO)
logger.propagate = False
h = StreamHandler()
h.setLevel(INFO)
h.setFormatter(Formatter('%(levelname)s %(asctime)s %(filename)s %(message)s'))
logger.addHandler(h)


def conv(t, coin, size):
    return {'measurement': 'borrow_summary',
            'time': t,
            'tags': {'coin': coin},
            'fields': {'size': size}}


def main():
    logger.info("Start getting the borrow summary.")
    result = Ftx().spot_margin_borrow_summary()
    now = datetime.utcnow()
    points = [conv(now, r['coin'], r['size']) for r in result if r['coin'] in coins]
    idb = InfluxDBClient(os.environ['DB_HOST'], os.environ['DB_PORT'],
            os.getenv('DB_USER'), os.getenv('DB_PASS'), os.environ['DB_NAME'])
    #idb.write_points(points)
    logger.info(f"IDB client have written {len(points)} records.")
    logger.info("End.")


if __name__ == '__main__':
    main()

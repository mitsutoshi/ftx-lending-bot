import os
from datetime import datetime

from influxdb import InfluxDBClient

from ftx import Ftx


def main():

    ftx = Ftx()
    result = ftx.spot_margin_borrow_summary()
    now = datetime.utcnow()
    points = []
    for r in result:
        if r['coin'] == 'USD':
            p = {
                'measurement': 'borrow_summary',
                'time': now,
                'tags': {
                    'coin': r['coin']
                },
                'fields': {
                    'size': r['size']
                }
            }
            points.append(p)
            print(p)

    idb = InfluxDBClient(host=os.environ['DB_HOST'],
                         port=os.environ['DB_PORT'],
                         username=os.getenv('DB_USER', ''),
                         password=os.getenv('DB_PASS', ''),
                         database=os.environ['DB_NAME'])
    idb.write_points(points)

if __name__ == '__main__':
    main()

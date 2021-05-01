
import os

from influxdb import InfluxDBClient

from ftx import Ftx


def main():

    ftx = Ftx()
    history = ftx.spot_margin_lending_history()

    points = []
    for h in history:
        print(h)
        p = {
            'measurement': 'lending_history',
            'time': h['time'],
            'tags': {
                'coin': h['coin']
            },
            'fields': {
                'size': h['size'],
                'rate': h['rate'],
                'proceeds': h['proceeds']
            }
        }
        points.append(p)

    idb = InfluxDBClient(host=os.environ['DB_HOST'],
                         port=os.environ['DB_PORT'],
                         username=os.getenv('DB_USER', ''),
                         password=os.getenv('DB_PASS', ''),
                         database=os.environ['DB_NAME'])
    idb.write_points(points)

if __name__ == '__main__':
    main()

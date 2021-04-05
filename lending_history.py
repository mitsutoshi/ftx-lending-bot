
import os

from influxdb import InfluxDBClient

from ftx import Ftx


def main():

    # check env vars
    api_key = os.getenv('FTX_API_KEY')
    api_secret = os.getenv('FTX_API_SECRET')
    if not api_key or not api_secret:
        raise ValueError('Environment variables are reuqired. [FTX_API_KEY, FTX_API_SECRET]')

    ftx = Ftx(api_key, api_secret)
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

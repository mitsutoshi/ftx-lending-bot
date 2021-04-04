#! /usr/bin/env python

import os
import argparse
import json
import logging
import time
import hmac
from typing import Any

from requests import Request, Session, Response


logging.basicConfig(level=logging.INFO, format='%(levelname)s %(asctime)s %(message)s')
logger = logging.getLogger()


def private(func):
    def wrapper(self, *args, **kwargs):
        if not self.api_key or not self.api_secret:
            raise ValueError('api_key and api_secret are required.')
        return func(self, *args, **kwargs)
    return wrapper


class Ftx(object):

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = 'https://ftx.com'
        self.s = Session()

    @private
    def spot_margin_lending_rates(self) -> list[dict[str, Any]]:
        res = self.__call_with_auth('GET', '/api/spot_margin/lending_rates')
        return json.loads(res.text)['result']

    @private
    def spot_margin_borrow_summary(self) -> list[dict[str, Any]]:
        res = self.__call_with_auth('GET', '/api/spot_margin/borrow_summary')
        return json.loads(res.text)['result']

    @private
    def spot_margin_lending_info(self) -> list[dict[str, Any]]:
        res = self.__call_with_auth('GET', '/api/spot_margin/lending_info')
        return json.loads(res.text)['result']

    @private
    def account_leverage(self, leverage: int) -> bool:
        data= {'leverage': leverage}
        res = self.__call_with_auth('POST', '/api/account/leverage', data)

        result = json.loads(res.text)
        if res.status_code != 200 and 'error' in result:
            logger.error(result['error'])
            return False
        return 'success' in result and result['success']

    @private
    def spot_margin_offer(self, coin: str, size: float, rate: float) -> bool:
        data = {'coin': coin, 'size': size, 'rate': rate}
        res = self.__call_with_auth('POST', '/api/spot_margin/offers', data)
        result = json.loads(res.text)
        if res.status_code != 200 and 'error' in result:
            logger.error(result['error'])
            return False
        return 'success' in result and result['success']

    def __call_with_auth(self, method: str, path: str, data: dict = None) -> Response:
        req = Request(method, self.base_url + path, self.__auth_header(method, path, data))
        if data:
            req.json = data
        return self.s.send(req.prepare())

    def __auth_header(self, method: str, path: str, data: dict = None) -> dict[str, str]:
        ts = int(time.time() * 1000)
        payload = f'{ts}{method}{path}' + (json.dumps(data) if data else '')
        sign = hmac.new(self.api_secret.encode(), payload.encode(), 'sha256').hexdigest()
        return {
                'FTX-KEY': self.api_key,
                'FTX-SIGN': sign,
                'FTX-TS': str(ts)}


def main():

    # check env vars
    api_key = os.getenv('FTX_API_KEY')
    api_secret = os.getenv('FTX_API_SECRET')
    if not api_key or not api_secret:
        raise ValueError('Environment variables are reuqired. [FTX_API_KEY, FTX_API_SECRET]')

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--coin', type=str, required=True, dest='coin')
    args = parser.parse_args()

    ftx = Ftx(api_key, api_secret)

    # get current lending information
    lendings = ftx.spot_margin_lending_info()

    for lnd in lendings:

        # logging current lending
        if lnd['offered']:
            logger.info(f"Current lending: coin={lnd['coin']}, locked={lnd['locked']}, lendable={lnd['lendable']:.7f}, minRate: {lnd['minRate']:4f}, offered={lnd['offered']}")

        # offer if available
        if lnd['coin'] == args.coin and lnd['lendable'] > lnd['offered']:

            # Truncate below 6 digits after the decimal point to get offer price
            lendable_s = f"{lnd['lendable']}"
            idx = lendable_s.find('.') + 7
            offer = lendable_s[:idx]
            logger.info(f"Found lenderble: coin={lnd['coin']}, available={offer}")

            # send offer
            ftx.spot_margin_offer(args.coin, offer, lnd['minRate'])
            logger.info(f"{lnd['coin']} have been offered.")


if __name__ == '__main__':
    main()


import os
import json
import logging
import time
import hmac
from typing import Any

from requests import Request, Session, Response


logger = logging.getLogger()


def private(func):
    def wrapper(self, *args, **kwargs):
        if not self.api_key or not self.api_secret:
            raise ValueError('api_key and api_secret are required.')
        return func(self, *args, **kwargs)
    return wrapper


class Ftx(object):

    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key if api_key else os.getenv('FTX_API_KEY')
        self.api_secret = api_secret if api_secret else os.getenv('FTX_API_SECRET')
        self.base_url = 'https://ftx.com'
        self.s = Session()

    def spot_margin_borrow_summary(self) -> list[dict[str, Any]]:
        req = Request('GET', self.base_url + '/api/spot_margin/borrow_summary')
        res = self.s.send(req.prepare())
        return json.loads(res.text)['result']

    @private
    def spot_margin_lending_rates(self) -> list[dict[str, Any]]:
        res = self.__call_with_auth('GET', '/api/spot_margin/lending_rates')
        return json.loads(res.text)['result']

    @private
    def spot_margin_lending_info(self) -> list[dict[str, Any]]:
        res = self.__call_with_auth('GET', '/api/spot_margin/lending_info')
        return json.loads(res.text)['result']

    @private
    def spot_margin_lending_history(self) -> list[dict[str, Any]]:
        res = self.__call_with_auth('GET', '/api/spot_margin/lending_history')
        return json.loads(res.text)['result']

    @private
    def spot_margin_offer(self, coin: str, size: float, rate: float) -> bool:
        data = {'coin': coin, 'size': size, 'rate': rate}
        res = self.__call_with_auth('POST', '/api/spot_margin/offers', data)
        result = json.loads(res.text)
        if res.status_code != 200 and 'error' in result:
            logger.error(result['error'])
            return False
        return 'success' in result and result['success']

    @private
    def account_leverage(self, leverage: int) -> bool:
        data= {'leverage': leverage}
        res = self.__call_with_auth('POST', '/api/account/leverage', data)

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


#! /usr/bin/env python

import os
import argparse
import logging
from typing import Any

from ftx import Ftx

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(asctime)s %(message)s')
logger = logging.getLogger()


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
            #ftx.spot_margin_offer(args.coin, offer, lnd['minRate'])
            logger.info(f"{lnd['coin']} have been offered.")


if __name__ == '__main__':
    main()


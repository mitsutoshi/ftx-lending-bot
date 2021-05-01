#! /usr/bin/env python
import os
import argparse
import logging.config
from logging import getLogger
from typing import Any

from ftx import Ftx


logging.config.fileConfig("logging.conf")
logger = getLogger()


def main():

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--coin', type=str, required=True,
            dest='coin', nargs='*',  help='Coin name such as USD, BTC, etc.')
    args = parser.parse_args()

    # get lending info
    ftx = Ftx()
    lend_info = ftx.spot_margin_lending_info()

    for lnd in lend_info:

        # logging lending state
        if lnd['offered']:
            logger.info(f"Enable lending: coin={lnd['coin']}, locked={lnd['locked']}, lendable={lnd['lendable']:.7f}, minRate={lnd['minRate']:4f}, offered={lnd['offered']}")
        else:
            logger.info(f"Not lending: coin={lnd['coin']}, lendable={lnd['lendable']:.7f}")

        if lnd['coin'] in args.coin and lnd['lendable']:

            # truncate below 6 digits after the decimal point to get offer price
            s = f"{lnd['lendable']:.8f}"
            lendable = float(s[:s.find('.') + 7])

            # send offer
            if lendable > lnd['offered']:
                ftx.spot_margin_offer(args.coin, lendable, lnd['minRate'])
                logger.info(f"{lendable} {lnd['coin']} have been offered.")


if __name__ == '__main__':
    main()

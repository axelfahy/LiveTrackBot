# -*- coding: utf-8 -*-
"""Telegram bot for livetracking.

This module get the json data about the flight and send
messages for take-offs and landings.
"""
import json
import logging
import time
from typing import Dict, Optional

import requests
import telegram

from . import (CHANNEL_ID,
               TIMEOUT,
               TELEGRAM_KEY,
               SLEEP_TIME)

LOGGER = logging.getLogger(__name__)


def get_json(url: str) -> Optional[dict]:
    """
    Retrieve the JSON from the given url.


    Parameters
    ----------
    url
        URL containing the JSON.

    Returns
    -------
    dict
        The JSON retrieved.
    """
    try:
        r = requests.get(url, timeout=TIMEOUT)
        r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        LOGGER.error(f'Http error: {errh}')
    except requests.exceptions.ConnectionError as errc:
        LOGGER.error(f'Error connecting: {errc}')
    except requests.exceptions.Timeout as errt:
        LOGGER.error(f'Timeout error: {errt}')
    except requests.exceptions.RequestException as err:
        LOGGER.error(f'Something else happened: {err}')
    else:
        try:
            return r.json()
        except json.JSONDecodeError as e:
            LOGGER.error(f'Error decoding the json: {e}')
    return None


def run(url: str) -> None:
    """
    Get the JSON every 5 minutes and parse it.

    Parameters
    ----------
    url
        URL containing the JSON.

    Send to the Telegram channel any new take offs or landings.
    """
    pilots: Dict[str, Dict[str, Dict[str, str]]] = {}
    bot = telegram.Bot(token=TELEGRAM_KEY)
    newline = '\n'

    while True:
        data = get_json(url)

        if data is not None:
            for pilot, points in data.items():
                # If pilot is not in the dict, add it and
                # recover the first point of the pilot to get
                # the start time of the flight.
                if pilot not in pilots:
                    pilots[pilot] = {}
                    pilots[pilot]['start'] = points[str(points['Count'])]
                    LOGGER.info(f'{pilots[pilot]} took off.')
                    bot.sendMessage(chat_id=CHANNEL_ID,
                                    text=f'{pilot} took off at '
                                         f'{pilots[pilot]["start"]["DateTime"]}')
                else:
                    # Check the last point of the pilot.
                    # If this is an `OK`, send a message on the channel with flight information:
                    # Flight time, distance, distance to take off
                    # (to know if we need to go get him...)
                    # Send the link to the livetrack as well.
                    # For other messages (`HELP`, `NEW MOVEMENT`),
                    # send them with the link of the livetrack.
                    # TODO: can we miss a point, hence the OK? Need to test.
                    msg = points['0']['Msg']
                    if msg == 'OK':
                        pilots[pilot]['ok'] = points['0']
                        LOGGER.info(f'{pilots[pilot]} landed.')
                        bot.sendMessage(chat_id=CHANNEL_ID,
                                        text=f'{pilot} landed at '
                                             f'{pilots[pilot]["ok"]["DateTime"]}{newline}'
                                             f'Duration: '
                                             f'{pilots[pilot]["ok"]["flightTime"]}{newline}'
                                             f'Cumulative distance: '
                                             f'{pilots[pilot]["ok"]["cumDist"]}{newline}'
                                             f'Distance from take off: '
                                             f'{pilots[pilot]["ok"]["takeOffDist"]}{newline}'
                                             f'Tracking: {url}')
                    elif msg in ('HELP', 'NEW MOVEMENT'):
                        LOGGER.info(f'{pilots[pilot]} sent {msg}.')
                        bot.sendMessage(chat_id=CHANNEL_ID,
                                        text=f'{pilot} sent {msg}!!!{newline}'
                                             f'Tracking: {url}')
                    else:
                        # TODO: change, might not be new points.
                        LOGGER.debug(f'New points for {pilot}: {points["0"]}')

        time.sleep(SLEEP_TIME)

# -*- coding: utf-8 -*-
"""Telegram bot for livetracking.

This module get the json data about the flight and send
messages for take-offs and landings.
"""
from datetime import date, datetime
import json
import logging
import time
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import urlparse

import requests
import telegram

from . import (TIMEOUT,
               TELEGRAM_KEY,
               SLEEP_TIME)

LOGGER = logging.getLogger(__name__)


def delete_messages(bot: telegram.bot, messages: Sequence[telegram.Message]) -> None:
    """
    Delete all the messages sent.

    Parameters
    ----------
    bot: telegram.bot
        Bot used to remove the messages.
    messages : Sequence of messages
        List of messages to delete.
    """
    for msg in messages:
        bot.deleteMessage(chat_id=msg.chat.id, message_id=msg.message_id)


def get_display_url(url: str, pilot: str) -> str:
    """
    Get the url to send with a message to display the pilot's track.

    The parameters of the url need to be kept, and the `hLg=pilot`
    option is added to show only the pilot tracks and center it.

    Parameters
    ----------
    url : str
        URL containing the JSON.
    pilot : str
        Name of the pilot to display.

    Returns
    -------
    str
        URL to display the track of the pilot
    """
    s = urlparse(url)
    res = f'{s.scheme}://{s.netloc}?'

    if s.query != '':
        res += f'{s.query}&'
    return f'[Tracking]({res}hLg={pilot})'


def get_json(url: str, timeout: int = TIMEOUT) -> Optional[dict]:
    """
    Retrieve the JSON from the given url.


    Parameters
    ----------
    url : str
        URL containing the JSON.
    timeout : int, default `TIMEOUT`
        Timeout for the request.

    Returns
    -------
    dict
        The JSON retrieved.
    """
    try:
        r = requests.get(url, timeout=timeout)
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


def format_date(date_str: str) -> str:
    """
    Parse the date from a given format to another.

    Used to send a correct format of date in the message.

    Parameters
    ----------
    date_str : str
        Date from the JSON, format: '%Y-%m-%dT%H:%M:%S%z'

    Returns
    -------
    str
        Date formatted for the message, format: '%Y-%m-%d %H:%M:%S UTC'
    """
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d %H:%M:%S UTC')


def run(channel: str, url: str) -> None:
    """
    Get the JSON every 5 minutes and parse it.

    Parameters
    ----------
    channel : str
        Channel's ID to send the messages to.
    url : str
        URL containing the JSON.

    Send to the Telegram channel any new take offs or landings.
    """
    pilots: Dict[str, Dict[str, Any]] = {}
    messages: List[telegram.Message] = []
    bot = telegram.Bot(token=TELEGRAM_KEY)
    newline = '\n'
    last_update = date.min

    while True:
        # Each day, clear the pilots and remove the messages.
        if last_update < datetime.utcnow().date():
            pilots.clear()
            delete_messages(bot, messages)
            del messages[:]
            last_update = datetime.utcnow().date()

        data = get_json(url)

        if data:
            for pilot, points in data.items():
                # If pilot is not in the dict, add it and
                # recover the first point of the pilot to get
                # the start time of the flight.
                if pilot not in pilots:
                    pilots[pilot] = {}
                    pilots[pilot]['start'] = points[str(points['Count'])]
                    pilots[pilot]['lastTime'] = pilots[pilot]['start']['unixTime']
                    LOGGER.info(f'{pilot} took off: {pilots[pilot]}')
                    messages.append(bot.sendMessage(
                        chat_id=channel,
                        text=f'*{pilot}* started tracking at '
                             f'{format_date(pilots[pilot]["start"]["DateTime"])}',
                        parse_mode='Markdown'))
                else:
                    # Check the unseen points of the pilot.
                    # A point is unseen if the `unixTime` is higher than
                    # the pilot's `lastTime` value.
                    # If this is an `OK`, send a message on the channel with flight information:
                    # Flight time, distance, distance to take off
                    # (to know if we need to go get him...)
                    # Send the link to the livetrack as well.
                    # For other messages (`HELP`, `NEW MOVEMENT`),
                    # send them with the link of the livetrack.
                    point = 0
                    while point < points['Count']:
                        if points[str(point)]['unixTime'] > pilots[pilot]['lastTime']:
                            msg = points[str(point)]['Msg']
                            if msg == 'OK':
                                pilots[pilot]['ok'] = points[str(point)]
                                LOGGER.info(f'{pilot} landed: {pilots[pilot]}')
                                messages.append(bot.sendMessage(
                                    chat_id=channel,
                                    text=f'*{pilot}* sent OK at '
                                         f'{format_date(pilots[pilot]["ok"]["DateTime"])}{newline}'
                                         f'Duration: '
                                         f'{pilots[pilot]["ok"]["flightTime"]}{newline}'
                                         f'Distance ALL/TO: {pilots[pilot]["ok"]["cumDist"]}'
                                         f'/{pilots[pilot]["ok"]["takeOffDist"]} km{newline}'
                                         f'{get_display_url(url, pilot)}',
                                    parse_mode='Markdown'))
                            elif msg in ('HELP', 'MOVE', 'CUSTOM'):
                                LOGGER.info(f'{pilots[pilot]} sent {msg}.')
                                messages.append(bot.sendMessage(
                                    chat_id=channel,
                                    text=f'*{pilot}* sent {msg}!!!{newline}'
                                         f'{get_display_url(url, pilot)}',
                                    parse_mode='Markdown'))
                            else:
                                LOGGER.debug(f'New point for {pilot}: {points[str(point)]}')

                        else:
                            break
                        point += 1
                    pilots[pilot]['lastTime'] = points['0']['unixTime']

        time.sleep(SLEEP_TIME)

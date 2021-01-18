# -*- coding: utf-8 -*-
"""Telegram bot for livetracking.

This module get the json data about the flight and send
messages for take-offs and landings.
"""
from dataclasses import dataclass
from datetime import date, datetime
import json
import logging
import time
from typing import Dict, List, Optional, Sequence
from urllib.parse import urlparse

import requests
import telegram

from . import (TIMEOUT,
               TELEGRAM_KEY,
               SLEEP_TIME)

LOGGER = logging.getLogger(__name__)


@dataclass
class Point():
    """
    Class to store information about a point.

    The points can be loaded from json using `from_json`.
    """
    cum_dist: str
    take_off_dist: str
    flight_time: str
    avg_speed: str
    leg_speed: str
    leg_dist: str
    lat: float
    lng: float
    alt: int
    msg: str
    date_time: str
    unix_time: int
    spot_id: int

    def __init__(self, json_dict: dict):
        """
        Create a `Point` object from a dictionnary.

        Parameters
        ----------
        json: dict
            JSON with the data point, as a dictionary.

        Returns
        -------
        Point
            Point with the data from the JSON.
        """
        self.cum_dist = json_dict['cumDist']
        self.take_off_dist = json_dict['takeOffDist']
        self.flight_time = json_dict['flightTime']
        self.avg_speed = json_dict['AvgSpeed']
        self.leg_speed = json_dict['LegSpeed']
        self.leg_dist = json_dict['LegDist']
        self.lat = json_dict['Lat']
        self.lng = json_dict['Lng']
        self.alt = json_dict['Alt']
        self.msg = json_dict['Msg']
        self.date_time = json_dict['DateTime']
        self.unix_time = json_dict['unixTime']
        self.spot_id = json_dict['spotId']


@dataclass
class Pilot:
    """
    Class to store information about a pilot.

    Only the last point needs to be saved in order to know if the other points are new.
    """
    name: str
    last_point: Point


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
        try:
            bot.deleteMessage(chat_id=msg.chat.id, message_id=msg.message_id)
        except telegram.error.BadRequest as e:
            LOGGER.error(f'Error when deleting the message {msg.message_id}: {e}')
        except AttributeError as e:
            LOGGER.error(f'Error when deleting the message {msg}: {e}')


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
    res = f'{s.scheme}://{s.netloc}{s.path.replace("/json4Others.php", "")}?'

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
            LOGGER.error(f'Error decoding the json: {e} - {r.text}')
    return None


def format_date(date_str: str) -> str:
    """
    Parse the date from a given format to another.

    Use to send a correct format of date in the message.

    Parameters
    ----------
    date_str : str
        Date from the JSON, format: '%Y-%m-%dT%H:%M:%S%z'

    Returns
    -------
    str
        Date formatted for the message, format: '%Y-%m-%d %H:%M:%S UTC'
        If format is not correct, the original date is returned.
    """
    try:
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d %H:%M:%S UTC')
    except ValueError as e:
        LOGGER.error(f'Format for date {date_str} is not correct: {e}')
    # Try another format if it did not work.
    try:
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%').strftime('%Y-%m-%d %H:%M:%S UTC')
    except ValueError as e:
        LOGGER.error(f'Format for date {date_str} is not correct: {e}')
    return date_str


def run(channel: str, url: str) -> None:
    """
    Get the JSON every `SLEEP_TIME` and parse it.

    Send to the Telegram channel any new take offs or landings.

    Parameters
    ----------
    channel : str
        Channel's ID to send the messages to.
    url : str
        URL containing the JSON.
    """
    pilots: Dict[str, Pilot] = {}
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

        # Load the JSON and create the points for each pilots.
        data = get_json(url)
        if data:
            for pilot, points in data.items():
                # Check the pilot and set the last point with the first point.
                if pilot not in pilots:
                    pilots[pilot] = Pilot(name=pilot,
                                          last_point=Point(points[str(points['Count'])]))
                    LOGGER.info(f'{pilot} took off: {pilots[pilot]}')
                    messages.append(send_message(
                        bot,
                        channel,
                        (f'*{pilot}* started tracking at '
                         f'{format_date(pilots[pilot].last_point.date_time)}')))

                # Create a list with only the points to process, based on timestamp.
                unseen_points = sorted(
                    [Point(v) for k, v in points.items() if k != 'Count'
                     if v['unixTime'] > pilots[pilot].last_point.unix_time],
                    key=lambda x: x.unix_time)

                for point in unseen_points:
                    # If this is an `OK`, send a message on the channel with flight information
                    # For other messages (`HELP`, `NEW MOVEMENT`),
                    # send them with the link of the livetrack.
                    if point.msg == 'OK':
                        LOGGER.info(f'{pilot} landed: {point}')
                        messages.append(send_message(
                            bot,
                            channel,
                            (f'*{pilot}* sent OK at {format_date(point.date_time)}{newline}'
                             f'Duration: {point.flight_time}{newline}'
                             f'Distance ALL/TO: {point.cum_dist}'
                             f'/{point.take_off_dist} km{newline}'
                             f'{get_display_url(url, pilot)}')))
                    elif point.msg in ('HELP', 'MOVE', 'CUSTOM'):
                        LOGGER.info(f'{pilots[pilot]} sent message: {point}.')
                        messages.append(send_message(
                            bot,
                            channel,
                            (f'*{pilot}* sent {point.msg}!!!{newline}'
                             f'{get_display_url(url, pilot)}')))
                    elif point.msg == 'START':
                        # Pilot took off again, not on Spot for now.
                        LOGGER.info(f'{pilot} took off again: {point}')
                        messages.append(send_message(
                            bot,
                            channel,
                            (f'*{pilot}* started tracking again at '
                             f'{format_date(point.date_time)}')))
                    elif point.msg == 'OFF':
                        LOGGER.info(f'{pilot} turned the tracking off: {point}')
                        messages.append(send_message(
                            bot,
                            channel,
                            (f'*{pilot}* turned the tracking off at '
                             f'{format_date(point.date_time)}')))
                    else:
                        LOGGER.debug(f'New point for {pilot}: {point}')

                # Update the last point
                if unseen_points:
                    pilots[pilot].last_point = unseen_points[-1]

        time.sleep(SLEEP_TIME)


def send_message(bot: telegram.Bot, channel: str, text: str,
                 parse_mode: str = 'Markdown') -> Optional[telegram.Message]:
    """
    Send a message on the channel.

    Handles possible exception and return the send message.

    Parameters
    ----------
    bot : telegram.Bot
        Bot object containing the API key.
    channel : str
        Channel's ID to send the messages to.
    text : str
        Text to send.
    parse_mode : str, default `Markdown`
        Mode for the parsing.

    Returns
    -------
    telegram.Message
        The message object from the telegram api, containing the chat and message id.
    """
    msg = None
    try:
        msg = bot.sendMessage(
            chat_id=channel,
            text=text,
            parse_mode=parse_mode)
    except (telegram.vendor.ptb_urllib3.urllib3.exceptions.ReadTimeoutError,
            telegram.error.TimedOut) as e:
        LOGGER.error(f'Error when sending message {text} on channel {channel}: {e}')
    return msg

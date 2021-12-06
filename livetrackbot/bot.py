# -*- coding: utf-8 -*-
"""Telegram bot for livetracking.

This module get the json data about the flight and send
messages for take-offs and landings.
"""

from datetime import date, datetime
import json
import logging
import time
from typing import Dict, List, Optional, Sequence

from prometheus_client import start_http_server, Counter, Gauge
import requests
import telegram

from livetrackbot import METRICS_NAMESPACE, SLEEP_TIME, TELEGRAM_KEY, TIMEOUT
from livetrackbot.pilot import Pilot
from livetrackbot.point import Point

LOGGER = logging.getLogger(__name__)


class LivetrackBot:
    """
    LivetrackBot class

    This class handles the logic of the livetracking bot.
    """

    NEWLINE = "\n"

    def __init__(self, channel: str, url: str, port: int) -> None:
        """
        Initialization of LivetrackBot.

        Parameters
        ----------
        channel : str
            Channel's ID to send the messages to.
        url : str
            URL containing the JSON.
        port : int
            Port used for metrics.
        """
        self.channel = channel
        self.url = url

        self.bot = telegram.Bot(token=TELEGRAM_KEY)

        # Initialize Prometheus.
        start_http_server(port)
        self.metrics = {
            "errors_total": Counter(
                f"{METRICS_NAMESPACE}_errors_total",
                "Number of errors.",
            ),
            "messages_send_total": Counter(
                f"{METRICS_NAMESPACE}_messages_send_total",
                "Number of messages sent.",
            ),
            "pilots_flying": Gauge(
                f"{METRICS_NAMESPACE}_pilots_flying",
                "Number of pilots currently flying.",
            ),
            "requests_total": Counter(
                f"{METRICS_NAMESPACE}_requests_total",
                "Number of requests sent.",
            ),
        }

    def delete_messages(self, messages: Sequence[telegram.Message]) -> None:
        """
        Delete all the messages sent.

        Parameters
        ----------
        messages : Sequence of messages
            List of messages to delete.
        """
        for msg in messages:
            try:
                self.bot.deleteMessage(chat_id=msg.chat.id, message_id=msg.message_id)
            except telegram.error.BadRequest as e:
                LOGGER.error(f"Error when deleting the message {msg.message_id}: {e}")
            except AttributeError as e:
                LOGGER.error(f"Error when deleting the message {msg}: {e}")

    def get_json(self, timeout: int = TIMEOUT) -> Optional[dict]:
        """
        Retrieve the JSON from the given url.

        Parameters
        ----------
        timeout : int, default `TIMEOUT`
            Timeout for the request.

        Returns
        -------
        dict
            The JSON retrieved.
        """
        try:
            error = False
            r = requests.get(self.url, timeout=timeout)
            r.encoding = "utf-8-sig"
            r.raise_for_status()
            self.metrics["requests_total"].inc()
        except requests.exceptions.HTTPError as errh:
            error = True
            LOGGER.error(f"Http error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            error = True
            LOGGER.error(f"Error connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            error = True
            LOGGER.error(f"Timeout error: {errt}")
        except requests.exceptions.RequestException as err:
            error = True
            LOGGER.error(f"Something else happened: {err}")
        else:
            try:
                return r.json()
            except json.JSONDecodeError as e:
                error = True
                LOGGER.error(f"Error decoding the json: {e} - {r.text}")
        if error:
            self.metrics["errors_total"].inc()
        return None

    def send_message(
        self, text: str, parse_mode: str = "Markdown"
    ) -> Optional[telegram.Message]:
        """
        Send a message on the channel.

        Handles possible exception and return the send message.

        Parameters
        ----------
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
            msg = self.bot.sendMessage(
                chat_id=self.channel, text=text, parse_mode=parse_mode
            )
            self.metrics["messages_send_total"].inc()
        except (
            telegram.vendor.ptb_urllib3.urllib3.exceptions.ReadTimeoutError,
            telegram.error.TimedOut,
        ) as e:
            self.metrics["errors_total"].inc()
            LOGGER.error(
                f"Error when sending message {text} on channel {self.channel}: {e}"
            )
        return msg

    def run(self) -> None:
        """
        Get the JSON every `SLEEP_TIME` and parse it.

        Send to the Telegram channel any new take offs or landings.
        """
        LOGGER.info("Starting bot...")
        LOGGER.info(f"Channel: {self.channel}")
        LOGGER.info(f"Url:     {self.url}")

        pilots: Dict[str, Pilot] = {}
        messages: List[telegram.Message] = []
        last_update = date.min

        while True:
            # Each day, clear the pilots and remove the messages.
            if last_update < datetime.utcnow().date():
                pilots.clear()
                self.delete_messages(messages)
                del messages[:]
                last_update = datetime.utcnow().date()

            # Load the JSON and create the points for each pilots.
            data = self.get_json()
            if data:
                for pilot, points in data.items():
                    # Check the pilot and set the last point with the first point.
                    if pilot not in pilots:
                        pilots[pilot] = Pilot(
                            name=pilot, last_point=Point(points[str(points["Count"])])
                        )
                        LOGGER.info(f"{pilot} took off: {pilots[pilot]}")
                        messages.append(
                            self.send_message(
                                (
                                    f"*{pilot}* started tracking at "
                                    f"{pilots[pilot].last_point.format_date()}"
                                )
                            )
                        )
                        self.metrics["pilots_flying"].inc()

                    # Create a list with only the points to process, based on timestamp.
                    unseen_points = sorted(
                        [
                            Point(v)
                            for k, v in points.items()
                            if k != "Count"
                            if v["unixTime"] > pilots[pilot].last_point.unix_time
                        ],
                        key=lambda x: x.unix_time,
                    )

                    for point in unseen_points:
                        # If this is an `OK`, send a message on the channel with flight information
                        # For other messages (`HELP`, `NEW MOVEMENT`),
                        # send them with the link of the livetrack.
                        if point.msg == "OK":
                            LOGGER.info(f"{pilot} landed: {point}")
                            messages.append(
                                self.send_message(
                                    (
                                        f"*{pilot}* sent OK at {point.format_date()}{self.NEWLINE}"
                                        f"Duration: {point.flight_time}{self.NEWLINE}"
                                        f"Distance ALL/TO: {point.cum_dist}"
                                        f"/{point.take_off_dist} km{self.NEWLINE}"
                                        f"{pilots[pilot].get_display_url(self.url)}{self.NEWLINE}"
                                        f"{point.get_itinerary_url()}"
                                    )
                                )
                            )
                            self.metrics["pilots_flying"].dec()
                        elif point.msg in ("HELP", "MOVE", "CUSTOM"):
                            LOGGER.info(f"{pilots[pilot]} sent message: {point}.")
                            messages.append(
                                self.send_message(
                                    (
                                        f"*{pilot}* sent {point.msg}!!!{self.NEWLINE}"
                                        f"{pilots[pilot].get_display_url(self.url)}"
                                    )
                                )
                            )
                        elif point.msg == "START":
                            # Pilot took off again, not on Spot for now.
                            LOGGER.info(f"{pilot} took off again: {point}")
                            messages.append(
                                self.send_message(
                                    (
                                        f"*{pilot}* started tracking again at "
                                        f"{point.format_date()}"
                                    )
                                )
                            )
                            self.metrics["pilots_flying"].inc()
                        elif point.msg == "OFF":
                            LOGGER.info(f"{pilot} turned the tracking off: {point}")
                            messages.append(
                                self.send_message(
                                    (
                                        f"*{pilot}* turned the tracking off at "
                                        f"{point.format_date()}"
                                    )
                                )
                            )
                            self.metrics["pilots_flying"].dec()
                        else:
                            LOGGER.debug(f"New point for {pilot}: {point}")

                    # Update the last point
                    if unseen_points:
                        pilots[pilot].last_point = unseen_points[-1]

            time.sleep(SLEEP_TIME)

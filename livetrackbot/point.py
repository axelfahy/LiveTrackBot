# -*- coding: utf-8 -*-
"""Class to represent a point from the livetrack."""

from dataclasses import dataclass
from datetime import datetime
import logging

LOGGER = logging.getLogger(__name__)


@dataclass
class Point:
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
        Create a `Point` object from a dictionary.

        Parameters
        ----------
        json : dict
            JSON with the data point, as a dictionary.

        Returns
        -------
        Point
            Point with the data from the JSON.
        """
        self.cum_dist = json_dict["cumDist"]
        self.take_off_dist = json_dict["takeOffDist"]
        self.flight_time = json_dict["flightTime"]
        self.avg_speed = json_dict["AvgSpeed"]
        self.leg_speed = json_dict["LegSpeed"]
        self.leg_dist = json_dict["LegDist"]
        self.lat = json_dict["Lat"]
        self.lng = json_dict["Lng"]
        self.alt = json_dict["Alt"]
        self.msg = json_dict["Msg"]
        self.date_time = json_dict["DateTime"]
        self.unix_time = json_dict["unixTime"]
        self.spot_id = json_dict["spotId"]

    def get_itinerary_url(self) -> str:
        """
        Get the url with the map itinerary to retrieve the pilot.

        Need the latitude and longitude of the pilot.

        Returns
        -------
        str
            URL with the map itinerary.
        """
        base_url = "https://www.google.com/maps/dir/?api=1&destination="
        link_name = "[Pick Me]"
        return f"{link_name}({base_url}{self.lat},{self.lng}&travelmode=driving)"

    def format_date(self) -> str:
        """
        Parse the date from a given format to another.

        Use to send a correct format of date in the message.

        Returns
        -------
        str
            Date formatted for the message, format: '%Y-%m-%d %H:%M:%S UTC'
            If format is not correct, the original date is returned.
        """
        try:
            return datetime.strptime(self.date_time, "%Y-%m-%dT%H:%M:%S%z").strftime(
                "%Y-%m-%d %H:%M:%S UTC"
            )
        except ValueError as e:
            LOGGER.error(f"Format for date {self.date_time} is not correct: {e}")
        # Try another format if it did not work.
        try:
            return datetime.strptime(self.date_time, "%Y-%m-%dT%H:%M:%S%").strftime(
                "%Y-%m-%d %H:%M:%S UTC"
            )
        except ValueError as e:
            LOGGER.error(f"Format for date {self.date_time} is not correct: {e}")
        return self.date_time

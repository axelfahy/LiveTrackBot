# -*- coding: utf-8 -*-
"""Class to represent a pilot."""

from dataclasses import dataclass
import logging
from urllib.parse import urlparse

import requests

from livetrackbot import API_SEARCH
from livetrackbot.point import Point

LOGGER = logging.getLogger(__name__)


@dataclass
class Pilot:
    """
    Class to store information about a pilot.

    Only the last point needs to be saved in order to know if the other points are new.
    The `home` of the pilot is stored in order to set the destination of the SBB itinerary.
    """

    name: str
    last_point: "Point"
    home: str

    def get_display_url(self, url: str) -> str:
        """
        Get the url to send with a message to display the pilot's track.

        The parameters of the url need to be kept, and the `hLg=pilot`
        option is added to show only the pilot tracks and center it.

        Parameters
        ----------
        url : str
            URL containing the JSON.

        Returns
        -------
        str
            URL to display the track of the pilot.
        """
        s = urlparse(url)
        res = f'{s.scheme}://{s.netloc}{s.path.replace("/json4Others.php", "")}?'

        if s.query != "":
            res += f"{s.query}&"
        return f"[Tracking]({res}hLg={self.name})"

    def get_sbb_itinerary(self) -> str:
        """
        Get the sbb itinerary on using search.ch api.

        The starting point is the last point of the pilot,
        which at the time of sending the message is the OK message.

        Returns
        -------
        str
            URL of the sbb itinerary.
        """
        payload = {
            "from": f"{self.last_point.lat},{self.last_point.lng}",
            "to": self.home,
        }
        result = requests.get(API_SEARCH, params=payload).json()
        url = result["url"]
        LOGGER.debug(f"URL for SBB itinerary: {url}")
        link_name = "[Back with SBB]"
        return f"{link_name}({url})"

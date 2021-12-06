# -*- coding: utf-8 -*-
"""Class to represent a pilot."""

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class Pilot:
    """
    Class to store information about a pilot.

    Only the last point needs to be saved in order to know if the other points are new.
    """

    name: str
    last_point: "Point"

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

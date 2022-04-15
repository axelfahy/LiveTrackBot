# -*- coding: utf-8 -*-
"""Test of the livetrackbot module.

This module tests the parsing and the order of the events.
"""

import json
from pathlib import Path
import unittest
import sys

from livetrackbot.pilot import Pilot
from livetrackbot.point import Point


class TestLivetrackbot(unittest.TestCase):
    """
    Unittest of livetrackbot module.
    """

    # Load the JSON file.
    with open(
        Path(__file__).parent.joinpath("resources", "json4Others_0.json"),
        encoding="utf-8-sig",
    ) as f:
        data = json.load(f)

    fakePoint = Point(
        {
            "cumDist": "1.36",
            "takeOffDist": "0.95",
            "flightTime": "0h17",
            "AvgSpeed": "4.78",
            "LegSpeed": "6.31",
            "LegDist": "0.95",
            "Lat": 46.04947,
            "Lng": 6.68662,
            "Alt": 1721,
            "Msg": "UNLIMITED-TRACK",
            "DateTime": "2022-04-15T11:52:48+0000",
            "unixTime": 1650023568,
            "spotId": 1752754773,
        }
    )

    def test_format_date(self):
        """
        Test of the `format_date` function.
        """
        # Check both possible formats.
        self.assertEqual(self.fakePoint.format_date(), "2022-04-15 11:52:48 UTC")

    def test_get_display_url(self):
        """
        Test of the `get_display_url` function.
        """
        pilot = Pilot("C-3PO", self.fakePoint, "Geneva")
        url = "https://livetrack.gartemann.tech/json4Others.php"

        self.assertEqual(
            pilot.get_display_url(url),
            "[Tracking](https://livetrack.gartemann.tech?hLg=C-3PO)",
        )
        self.assertEqual(
            pilot.get_display_url(f"{url}?jD=2"),
            "[Tracking](https://livetrack.gartemann.tech?jD=2&hLg=C-3PO)",
        )

    def test_get_sbb_itinerary(self):
        """
        Test of the `get_sbb_itinerary` function.
        """
        pilot = Pilot("C-3PO", self.fakePoint, "Geneva")

        self.assertEqual(
            pilot.get_sbb_itinerary(),
            "[Back with SBB](https://fahrplan.search.ch/Samo%C3%ABns,Plateau-des-Saix@541791,100051..Gen%C3%A8ve)",
        )


if __name__ == "__main__":
    from pkg_resources import load_entry_point

    sys.exit(load_entry_point("pytest", "console_scripts", "py.test")())  # type: ignore

# -*- coding: utf-8 -*-
"""Test of the livetrackbot module.

This module tests the parsing and the order of the events.
"""

import json
from pathlib import Path
import unittest
import sys

from livetrackbot.livetrackbot import (get_display_url,
                                       format_date)


class TestLivetrackbot(unittest.TestCase):
    """
    Unittest of livetrackbot module.
    """
    # Load the JSON file.
    with open(Path(__file__).parent.joinpath('resources', 'json4Others_0.json'),
              encoding='utf-8-sig') as f:
        data = json.load(f)

    def test_get_display_url(self):
        """
        Test of the `get_display_url` function.
        """
        url = 'https://livetrack.gartemann.tech/json4Others.php'

        self.assertEqual(get_display_url(url, 'C-3PO'),
                         '[Tracking](https://livetrack.gartemann.tech?hLg=C-3PO)')
        self.assertEqual(get_display_url(f'{url}?jD=2', 'Han_Solo'),
                         '[Tracking](https://livetrack.gartemann.tech?jD=2&hLg=Han_Solo)')

    def test_format_date(self):
        """
        Test of the `format_date` function.
        """
        # Check both possible format
        self.assertEqual(format_date(self.data['C-3PO']['0']['DateTime']),
                         '2020-07-13 19:39:16 UTC')
        self.assertEqual(format_date(self.data['Rey']['20']['DateTime']),
                         '2020-07-13 10:29:30 UTC')


if __name__ == '__main__':
    from pkg_resources import load_entry_point
    sys.exit(load_entry_point('pytest', 'console_scripts', 'py.test')())  # type: ignore

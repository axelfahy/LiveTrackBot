"""Livetracking module."""
import logging
import os
from dotenv import load_dotenv

from ._version import get_versions

# Load the .env file containing the keys.
load_dotenv()

# Logging configuration.
FORMAT = '%(asctime)s [%(levelname)-7s] %(name)s: %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

# For a test, you can add `?jD=X` to the URL,
# where `X` is the number of days in the past.
TRACKING_URL = 'https://livetrack.gartemann.tech/json4Others.php?jD=10'
TIMEOUT = 5
# Livetrack is refresh every 5 minutes.
SLEEP_TIME = 60 * 5

# Telegram information.
TELEGRAM_KEY = os.getenv('TELEGRAM_TOKEN')
CHANNEL_ID = '@FollowUsIfYouCan_channel'
# Not used for now, using the telegram api.
TELEGRAM_URL = f'https://api.telegram.org/bot{TELEGRAM_KEY}/sendMessage?chat_id={CHANNEL_ID}&text='

__version__ = get_versions()['version']
del get_versions

"""Livetracking module."""
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

from ._version import get_versions

# Load the .env file containing the keys.
load_dotenv()

# For a test, you can add `?jD=X` to the URL,
# where `X` is the number of days in the past.
TRACKING_URL = 'https://livetrack.gartemann.tech/json4Others.php'
TIMEOUT = 5
# Livetrack is refresh every minute.
SLEEP_TIME = 60

# Telegram information.
TELEGRAM_KEY = os.getenv('TELEGRAM_TOKEN')
assert TELEGRAM_KEY, 'Telegram key for the bot not found, `.env` file is probably missing.'
CHANNEL_ID = '@FollowUsIfYouCan_channel'
# Not used for now, using the telegram api.
TELEGRAM_URL = f'https://api.telegram.org/bot{TELEGRAM_KEY}/sendMessage?chat_id={CHANNEL_ID}&text='

# Logging configuration.
# Log the DEBUG inside a file and the INFO to stderr.
FORMATTER = logging.Formatter('%(asctime)s [%(levelname)-7s] %(name)s: %(message)s')

# File logger.
LOGFILE = Path('logs').joinpath(f'livetrackbot_{CHANNEL_ID}.log')
file_handler = logging.FileHandler(LOGFILE)  # pylint: disable=invalid-name
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(FORMATTER)

# Stream logger.
stream_handler = logging.StreamHandler(None)  # pylint: disable=invalid-name
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(FORMATTER)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)-7s] %(name)s: %(message)s',
    handlers=[file_handler, stream_handler]
)

__version__ = get_versions()['version']
del get_versions

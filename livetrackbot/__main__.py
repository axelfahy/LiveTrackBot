# -*- coding: utf-8 -*-
"""Entry point of the livetrack cli."""
import click

from livetrackbot import TRACKING_URL, CHANNEL_ID, METRICS_PORT
from livetrackbot.bot import LivetrackBot


@click.command()
@click.option(
    "--channel",
    "-c",
    default=CHANNEL_ID,
    show_default=False,
    help="Channel's ID (starts with `@`) on which the messages will be sent.",
)
@click.option(
    "--url",
    "-u",
    default=TRACKING_URL,
    show_default=False,
    help="URL to retrieve the JSON containing the points of the pilots.",
)
@click.option(
    "--port",
    "-p",
    default=METRICS_PORT,
    show_default=False,
    help="Port used for metrics (Prometheus).",
)
def main(channel: str, url: str, port: int):
    """CLI for livetracking.

    Parameters
    ----------
    channel : str
        ID of the channel to sent the messages to, starts with `@`.
    url : str
        URL to retrieve the JSON containing the points of the pilots.
        For a test, you can add `?jD=X` to the URL, where `X` is the number of days in the past.
    port: int
        Port used for metrics.

    Examples
    --------
    $ livetrack
    """
    bot = LivetrackBot(channel, url, port)
    bot.run()


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter

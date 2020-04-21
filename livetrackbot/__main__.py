# -*- coding: utf-8 -*-
"""Entry point of the livetrack cli."""
import click

from . import TRACKING_URL
from .livetrackbot import run


@click.command()
@click.option('--url', '-u',
              default=TRACKING_URL, show_default=False,
              help='URL to retrieve the JSON containing the points of the pilots.'
              )
def main(url: str):
    """CLI for livetracking.

    Parameters
    ----------
    url : str
        URL to retrieve the JSON containing the points of the pilots.
        For a test, you can add `?jD=X` to the URL, where `X` is the number of days in the past.

    Examples
    --------
    $ livetrack
    """
    run(url)


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter

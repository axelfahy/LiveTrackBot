# -*- coding: utf-8 -*-
"""
Configuration loader.
Tool to load the configuration from a configuration file (`config.json`).
"""
from collections.abc import Mapping
import logging
from pathlib import Path
import pprint
import json

LOGGER = logging.getLogger(__name__)


class Config(Mapping):
    """
    Class to load the configuration file.
    This class behaves like a dictionary that loads a
    configuration file in json format.

    Examples
    --------
    >>> config = Config()
    >>> print(config)
    {
      'yoda': 'dagobah',
      'Dark Vader': 'Mustafar'
    }
    """

    def __init__(
        self, path: Path = Path.home().joinpath(".config/livetrackbot/config.json")
    ):
        """
        Initialization of configuration.

        Parameters
        ----------
        path : Path, default '~/.config/livetrackbot/config.json'
            Path to the configuration file.
        """
        if path.exists():
            LOGGER.info(f"Loading configuration from {path}.")
            with path.open(mode="r", encoding="utf-8") as f:
                self._config = json.load(f)
                LOGGER.debug(f"Config:\n{self._config}")
        else:
            self._config = {}
            LOGGER.warning(f"Configuration path {path} does not exist.")

    def __getitem__(self, item):
        """Getter of the class."""
        try:
            return self._config[item]
        except KeyError as err:
            LOGGER.error(f"Configuration for {item} does not exist.")
            return err

    def __iter__(self):
        """Iterator of the class."""
        return iter(self._config)

    def __len__(self):
        """Lenght of the config."""
        return len(self._config)

    def __repr__(self):
        """Representation of the config."""
        return f"{super().__repr__}\n{str(self._config)}"

    def __str__(self):
        """
        __str__ method.
        Pretty representation of the config.
        """
        pretty = pprint.PrettyPrinter(indent=2)
        return pretty.pformat(self._config)

# -*- coding: utf-8 -*-
"""
Helpers for managing the ``.aiida-testing-config.yml`` configuration file.
"""

import os
import pathlib
import typing as ty
import collections
from voluptuous import Schema
from enum import Enum

import yaml

CONFIG_FILE_NAME = '.aiida-testing-config.yml'


class ConfigActions(Enum):
    """
    An enum containing the actions to perform on the config file.
    """
    READ = 'read'
    GENERATE = 'generate'
    REQUIRE = 'require'


class Config(collections.abc.MutableMapping):
    """Configuration of aiida-testing package."""

    schema = Schema({'mock_code': Schema({str: str})})

    def __init__(self, config=None):
        self._dict = config or {}
        self.validate()

    def validate(self):
        """Validate configuration dictionary."""
        return self.schema(self._dict)

    @classmethod
    def from_file(cls):
        """
        Parses the configuration file ``.aiida-testing-config.yml``.

        The file is searched in the current working directory and all its parent
        directories.
        """
        cwd = pathlib.Path(os.getcwd())
        config: ty.Dict[str, str]
        for dir_path in [cwd, *cwd.parents]:
            config_file_path = (dir_path / CONFIG_FILE_NAME)
            if config_file_path.exists():
                with open(config_file_path) as config_file:
                    config = yaml.load(config_file, Loader=yaml.SafeLoader)
                    break
        else:
            config = {}

        return cls(config)

    def to_file(self):
        """Write configuration to file in yaml format.

        Writes to current working directory.

        :param handle: File handle to write config file to.
        """
        cwd = pathlib.Path(os.getcwd())
        config_file_path = (cwd / CONFIG_FILE_NAME)

        with open(config_file_path, 'w') as handle:
            yaml.dump(self._dict, handle, Dumper=yaml.SafeDumper)

    def __getitem__(self, item):
        return self._dict.__getitem__(item)

    def __setitem__(self, key, value):
        return self._dict.__setitem__(key, value)

    def __delitem__(self, key):
        return self._dict.__delitem__(key)

    def __iter__(self):
        return self._dict.__iter__()

    def __len__(self):
        return self._dict.__len__()

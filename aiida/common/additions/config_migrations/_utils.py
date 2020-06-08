# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida_core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
"""Defines the migrations on the config.json file."""

from aiida.common.exceptions import ConfigurationVersionError
from ._migrations import (
    _MIGRATION_LOOKUP, CURRENT_CONFIG_VERSION, OLDEST_COMPATIBLE_CONFIG_VERSION
)

VERSION_KEY = 'CONFIG_VERSION'
CURRENT_KEY = 'CURRENT'
OLDEST_KEY = 'OLDEST_COMPATIBLE'

__all__ = ['check_and_migrate_config', 'add_config_version']

def add_config_version(
        config,
        current_version=CURRENT_CONFIG_VERSION,
        oldest_version=OLDEST_COMPATIBLE_CONFIG_VERSION
    ):
    """Injects the current and oldest compatible version numbers into the config."""
    config[VERSION_KEY] = {CURRENT_KEY: current_version, OLDEST_KEY: oldest_version}

def check_and_migrate_config(config, store=True):
    """
    Checks if the config needs to be migrated, and performs the migration if needed.
    """
    if config_needs_migrating(config):
        config = migrate_config(config)
        from aiida.common.setup import store_config
        if store:
            store_config(config)
    return config

def config_needs_migrating(config):
    """Checks if the config needs to be migrated."""
    current, oldest = _get_config_version(config)
    if oldest > CURRENT_CONFIG_VERSION:
        raise ConfigurationVersionError("The configuration in 'config.json' is generated by a newer version of AiiDA, and not compatible with the current version.")
    return CURRENT_CONFIG_VERSION > current

def _get_config_version(config):
    """Gets the current and oldest compatible versions from the config."""
    try:
        versions = config[VERSION_KEY]
        current = versions[CURRENT_KEY]
        oldest = versions[OLDEST_KEY]
    except KeyError:
        current = 0
        oldest = 0
    return current, oldest

def migrate_config(config):
    """Runs the migration functions to update the config to the current version."""
    current, _ = _get_config_version(config)
    while current < CURRENT_CONFIG_VERSION:
        config = _MIGRATION_LOOKUP[current].apply(config)
        current, _ = _get_config_version(config)
    return config
"""
Configuration Manager for API Load Pro
Handles loading and validation of configuration settings.
"""

import configparser
import os
from typing import Dict, Any

class ConfigManager:
    """ Manages configuration loading and validation """

    def __init__(self, config_path: str = "config.ini"):
        self.config_path = config_path
        self.config = None

    def load_config(self) -> Dict[str, Any]:
        """
        :rtype: Dict[str, Any]
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file '{self.config_path}' not found")

        config = configparser.ConfigParser()
        config.read(self.config_path)

        # Extract values
        api_config = {
            'base_url' : config.get('api', 'base_url'),
            'auth_url' : config.get('api', 'auth_url'),
            'client_id' : config.get('api', 'client_id'),
            'client_secret' : config.get('api', 'client_secret')
        }

        self.config = api_config
        return self.config

    def get_base_url(self) -> str:
        return self.config['api']['base_url']
    def get_auth_url(self) -> str:
        return self.config['api']['auth_url']
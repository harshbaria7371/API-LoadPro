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

        # Extract values with defaults
        require_auth = config.getboolean('api', 'require_auth', fallback=True)
        
        api_config = {
            'base_url' : config.get('api', 'base_url'),
            'require_auth' : require_auth
        }
        
        # Only load auth-related config if authentication is required
        if require_auth:
            api_config['auth_url'] = config.get('api', 'auth_url')
            api_config['client_id'] = config.get('api', 'client_id')
            api_config['client_secret'] = config.get('api', 'client_secret')
        else:
            # Set optional values even if not required
            api_config['auth_url'] = config.get('api', 'auth_url', fallback='')
            api_config['client_id'] = config.get('api', 'client_id', fallback='')
            api_config['client_secret'] = config.get('api', 'client_secret', fallback='')

        self.config = api_config
        return self.config

    def get_base_url(self) -> str:
        return self.config['base_url']
    
    def get_auth_url(self) -> str:
        return self.config['auth_url']
    
    def requires_auth(self) -> bool:
        """Check if authentication is required based on configuration"""
        return self.config.get('require_auth', True)
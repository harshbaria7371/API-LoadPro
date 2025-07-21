"""
Authenticator for API Load Pro
Handles API authentication and token management.
"""

import requests
import json
import os
import base64
import time
from typing import Optional, Dict, Any
from Libraries.config_manager import ConfigManager

class Authenticator:
    """ Handles API authentication and token management """

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.access_token = None
        self.token_file = "access_token.json"

    def authenticate(self) -> bool:
        """ Authenticate with the API and obtain access token """
        try:
            auth_url = self.config_manager.get_auth_url()
            client_id = self.config_manager.config['client_id']
            client_secret = self.config_manager.config['client_secret']

            print(f"Log: Authenticating with {auth_url}")

            auth_data = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret
            }

            response = requests.post(
                auth_url,
                data=auth_data)

            print(f"Log: Auth response status: {response.status_code}")

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')

                if self.access_token:
                    self._save_token(token_data)
                    print("Authentication successful")
                    return True
                else:
                    print("Authentication failed")
                    return False

            else:
                print(f"Authentication failed: {response.status_code}")

        except requests.exceptions.ConnectionError as e:
            print(f"Authentication Connection Error : {e}")
            return False

        except requests.RequestException as e:
            print(f"Authentication Request Error : {e}")
            return False

        except Exception as e:
            print(f"Authentication Exception : {e}")
            return False

    def get_access_token(self) -> Optional[str]:
        """
        Get the current access token, loading from file if needed.
        Checks for token expiration and refreshes if necessary.
        :return:
        """
        if self.access_token:
            if self.__is_token_expired(self.access_token):
                print("Log: current access token expired, refreshing token")
                if self.authenticate():
                    return self.access_token
                else:
                    return None
        return self.access_token


    def __is_token_expired(self, access_token):
        """
        Check if JWT token is expired by decoding the access token.
        :param access_token:
        :return:
           True if token is expired.
        """
        try:
            parts = access_token.split(".")
            if len(parts) != 3:
                print("Log: invalid JWT token format")
                return True

            payload = parts[1]

                # Add padding if required
                # Understand the method here
            payload += '=' * (-len(payload) % 4)

                # Decode base64
            decoded_payload = base64.b64decode(payload)
            payload_data = json.loads(decoded_payload.decode('utf-8'))

            if 'exp' in payload_data:
                exp_time = payload_data['exp']
                current_time = int(time.time())

                buffer_time = 300 # Added 5 minute buffer to refresh before actual expiration

                if current_time >= (exp_time - buffer_time):
                    print(f"Log: Token expires at {exp_time}, current time is {current_time}")
                    return True
                else:
                    print(f"Log: Token is valid till {exp_time}")
                    return False
            else:
                print(f"Log: No expiration time found")
                return False
        except Exception as e:
            print(f"Log: Error checking token expiration : {e}")
            return True

    def clear_token(self) -> None:
        self.access_token = None
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
        print("Log: Cleared stored token file")

    def refresh_token(self) -> bool:
        print("Log: Refreshing access token")
        self.access_token = None
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
        return self.authenticate()

    def _save_token(self, token_data: Dict[str, Any]) -> None:
        try:
            with open(self.token_file, 'w') as f:
                json.dump(token_data, f)
        except Exception as e:
            print(f"Warning: Error saving token : {e}")

import getpass

import keyring
import requests
import datetime

jamf_hostname = None
bearer_token = None


def get_uapi_token(host: str):
    global bearer_token
    global jamf_hostname
    jamf_hostname = host
    jamf_api_url = jamf_hostname + "/api/v1/auth/token"
    headers = {'Accept': 'application/json'}
    jamf_user = keyring.get_password("system", "JAMF_RTS_U")
    jamf_password = keyring.get_password("system", "JAMF_RTS_C")
    if jamf_user is None or len(jamf_user) == 0:
        print("No jamf user detected on keychain.")
        jamf_user = input('Please enter your service account\'s jamf username:\n')
        if jamf_user is not None and len(jamf_user) > 0:
            keyring.set_password("system", "JAMF_RTS_U", jamf_user)
        else:
            exit('Unable to read/set Jamf User')
    if jamf_password is None or len(jamf_password) == 0:
        print("No jamf credentials detected on keychain.")
        jamf_password = getpass.getpass('Enter your service account\'s jamf password:\n')
        if jamf_password is not None and len(jamf_password) > 0:
            keyring.set_password("system", "JAMF_RTS_C", jamf_password)
        else:
            exit('Unable to read/set Jamf Password')
    response = requests.post(url=jamf_api_url, headers=headers, auth=(jamf_user, jamf_password))
    response_json = response.json()
    try:
        bearer_token = BearerToken(response_json['token'], datetime.datetime.strptime(response_json['expires'],
                                                                                      '%Y-%m-%dT%H:%M:%SZ').replace(
            tzinfo=datetime.timezone.utc).astimezone(tz=None))
    except Exception:
        bearer_token = BearerToken(response_json['token'], datetime.datetime.strptime(response_json['expires'],
                                                                                      '%Y-%m-%dT%H:%M:%S.%fZ').replace(
            tzinfo=datetime.timezone.utc).astimezone(tz=None))
    return bearer_token


class BearerToken:
    def __init__(self, token, expiry: datetime):
        self.expiry = expiry
        self.token = token

    def is_valid(self):
        return datetime.datetime.now().astimezone(tz=None) + datetime.timedelta(milliseconds=1000) < self.expiry

    def get_token(self):
        return self.token


def get_bearer_token():
    global bearer_token
    if bearer_token is None or not bearer_token.is_valid():
        bearer_token = get_uapi_token()
    return bearer_token.token


def invalidate():
    global bearer_token
    bearer_token = None

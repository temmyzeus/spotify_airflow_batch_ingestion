import base64
import os
import time
import urllib.parse

import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv()
USERNAME: str = os.environ["SPOTIFY_USERNAME"]
PASSWORD: str = os.environ["SPOTIFY_PASSWORD"]
CLIENT_ID: str = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET: str = os.environ["SPOTIFY_CLIENT_SECRET"]

chrome_driver_path = "./chromedriver"
driver = webdriver.Chrome(chrome_driver_path)

CLIENT_KEY_B64: str = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

# headers:dict = {
#     "Content-Type" : "application/x-www-form-urlencoded",
#     "Authorization" : "Basic {}".format(CLIENT_KEY_B64)
# }

# body = {
#     "grant_type": "client_credentials"
# }
# r = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=body)

# body["code"] = r.json()["access_token"]
# body["redirect_uri"] = "https://google.com/"
# r2 = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=body)

# headers:dict = {
#     "Content-Type" : "application/json",
#     "Authorization" : "Bearer {}".format(r.json()["access_token"])
# }
# r3 = requests.get("https://api.spotify.com/v1/me/player/recently-played")

OAUTH_AUTHORIZE_URL: str = "https://accounts.spotify.com/authorize"
OAUTH_ACCESS_TOKEN_URL: str = "https://accounts.spotify.com/api/token"

payload: dict[str, str] = {
    "client_id": os.environ["SPOTIFY_CLIENT_ID"],
    "response_type": "code",
    "redirect_uri": "https://google.com/",
    "show_dialog": "false",
    "scope": "user-read-recently-played",
}
url_params = urllib.parse.urlencode(payload)
open_url: str = f"{OAUTH_AUTHORIZE_URL}?{url_params}"

# Start Selenium doings
driver.get(open_url)
driver.find_element(By.ID, "login-username").send_keys(USERNAME)
driver.find_element(By.ID, "login-password").send_keys(PASSWORD)
driver.find_element(
    By.XPATH,
    "/html/body/div[1]/div/div[2]/div/div/div[2]/div[3]/div[2]/button/div[1]/p",
).click()

time.sleep(15)
current_url = driver.current_url
driver.close()
response_params = current_url.split("?", maxsplit=2)[1]
code = urllib.parse.parse_qs(response_params)["code"]

headers: dict = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": "Basic {}".format(CLIENT_KEY_B64),
}

payload = {
    "grant_type": "authorization_code",
    "code": code,
    "redirect_uri": "https://google.com/",
}
r = requests.post(OAUTH_ACCESS_TOKEN_URL, headers=headers, data=payload)
token_api_response = r.json()

headers = {
    "Authorization": "{} {}".format(
        token_api_response["token_type"], token_api_response["access_token"]
    ),
    "Content-Type": "application/json",
}
recently_played_response = requests.get(
    "https://api.spotify.com/v1/me/player/recently-played", headers=headers
)


class Spotify(object):
    OAUTH_AUTHORIZE_URL: str = "https://accounts.spotify.com/authorize"
    OAUTH_ACCESS_TOKEN_URL: str = "https://accounts.spotify.com/api/token"

    """
    Steps:
    ------
    1. Init
    2. Get Auth url
    3. Get Code from auth URL
    4. Get access token with code , client_id and client_secret
    """

    def __init__(
        self,
        username,
        password,
        client_id,
        client_secret,
        scope: list = ["user-read-recently-played"],
        redirect_uri=None,
    ) -> None:
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = " ".join(scope)
        if redirect_uri:
            self.redirect_uri = redirect_uri
        else:
            self.redirect_uri = "https://google.com/"

    def get_auth_url(self) -> str:
        payload: dict[str, str] = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "show_dialog": "false",
            "scope": self.scope,
        }
        url_params = urllib.parse.urlencode(payload)
        auth_url: str = f"{OAUTH_AUTHORIZE_URL}?{url_params}"
        return auth_url

    def get_code(self, auth_url) -> str:
        driver.get(auth_url)

        # enter username(or email), password and click login
        driver.find_element(By.ID, "login-username").send_keys(USERNAME)
        driver.find_element(By.ID, "login-password").send_keys(PASSWORD)
        driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div[2]/div/div/div[2]/div[3]/div[2]/button/div[1]/p",
        ).click()

        time.sleep(15)
        current_url = driver.current_url
        driver.close()
        response_params = current_url.split("?", maxsplit=2)[1]
        code = urllib.parse.parse_qs(response_params)["code"]
        return code

    def get_access_token(self) -> dict:
        headers: dict = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic {}".format(CLIENT_KEY_B64),
        }

        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        r = requests.post(OAUTH_ACCESS_TOKEN_URL, headers=headers, data=payload)
        token_api_response = r.json()
        return token_api_response

    def recently_played(self) -> dict:
        self.recently_played_url: str = (
            "https://api.spotify.com/v1/me/player/recently-played"
        )
        headers: dict[str, str] = {
            "Authorization": "{} {}".format(
                token_api_response["token_type"], token_api_response["access_token"]
            ),
            "Content-Type": "application/json",
        }
        recent_plays = requests.get(self.recent_plays_url, headers=headers)
        if recent_plays.status_code not in range(200, 299):
            raise
        return recent_plays.json()


spotify = Spotify(
    username=USERNAME,
    password=PASSWORD,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
)
recent_plays = spotify.recent_plays()

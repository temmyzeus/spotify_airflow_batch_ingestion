import base64
import json
import os
import time
import urllib.parse
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict

import airflow
import boto3
import pandas as pd
import psycopg2
import requests
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

USERNAME: str = os.environ["SPOTIFY_USERNAME"]
PASSWORD: str = os.environ["SPOTIFY_PASSWORD"]
CLIENT_ID: str = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET: str = os.environ["SPOTIFY_CLIENT_SECRET"]

DRIVER_PATH = "http://selenium:4444/wd/hub"
OAUTH_AUTHORIZE_URL: str = "https://accounts.spotify.com/authorize"
OAUTH_ACCESS_TOKEN_URL: str = "https://accounts.spotify.com/api/token"


CLIENT_KEY_B64: str = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()


def fetch_spotify_data() -> Any:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920x1080")
    
    payload: dict[str, str] = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": "https://google.com/",
        "show_dialog": "false",
        "scope": "user-read-recently-played",
    }
    url_params = urllib.parse.urlencode(payload)
    open_url: str = f"{OAUTH_AUTHORIZE_URL}?{url_params}"
    print("OPEN URL:", open_url)

    # Start Selenium processes
    driver = webdriver.Remote(
        command_executor=DRIVER_PATH,
        desired_capabilities=DesiredCapabilities.CHROME,
        options=options
    )
    driver.get(open_url)
    driver.find_element(By.ID, "login-username").send_keys(USERNAME)
    driver.find_element(By.ID, "login-password").send_keys(PASSWORD)
    driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div/div[2]/div/div/div[2]/div[3]/div[2]/button/div[1]/p",
    ).click()
    
    try:
        element = WebDriverWait(driver, timeout=240).until(
            EC.title_is("Google")
        )
        current_url = driver.current_url
    finally:
        driver.quit()
    # Stop Selenium processes

    print("SPOTIFY ACCESS TOKEN URL:", current_url)
    response_params = current_url.split("?", maxsplit=2)[1]
    print(response_params)
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
    recently_played = recently_played_response.json()

    listens = defaultdict(list)
    artists = defaultdict(list)

    print(recently_played.keys())
    for n, item in enumerate(recently_played["items"]):
        artist_id: str = item["track"]["artists"][0]["id"]

        listens["artist_id"].append(artist_id)
        listens["artists_name"].append(item["track"]["artists"][0]["name"])
        listens["track_id"].append(item["track"]["id"])
        listens["track_name"].append(item["track"]["name"])
        listens["time_played"].append(item["played_at"])
        listens["duration_ms"].append(item["track"]["duration_ms"])
        listens["is_explicit"].append(item["track"]["explicit"])
        listens["is_album"].append(
            True if (item["track"]["album"]["album_type"] == "album") else False
        )
        # next_url = recent_plays["next"]
        # history["track_release_date"] = item["track"]["release_date"]

        # artist_reponse = spotify.artist(artist_id)

    listens_df = pd.DataFrame(listens)
    print(listens_df)
    # How does return work in airflow?


def upload_to_aws_rds():
    """Task to upload to AWS RDS Database"""
    rds_resource = boto3.resource("rds")
    pass


default_args: Dict[str, str] = {"email": "awoyeletemiloluwa@gmail.com"}
dag = DAG(
    dag_id="spotify-ingestion-dag",
    # schedule_interval="50 23 * * *", # 11:50 pm everyday
    schedule_interval=None,
    start_date=days_ago(5),
    default_args=default_args,
)

fetch_spotify_data = PythonOperator(
    task_id="Fetch-Spotify-Data", python_callable=fetch_spotify_data, dag=dag
)

upload_to_aws_rds = PythonOperator(
    task_id="Upload-to-AWS-Rds", python_callable=upload_to_aws_rds, dag=dag
)

fetch_spotify_data >> upload_to_aws_rds

import base64
import os
import urllib.parse
from collections import OrderedDict, defaultdict
from datetime import datetime, time
from typing import Any, Dict

import airflow
import pandas as pd
import requests
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

USERNAME: str = os.environ["SPOTIFY_USERNAME"]
PASSWORD: str = os.environ["SPOTIFY_PASSWORD"]
CLIENT_ID: str = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET: str = os.environ["SPOTIFY_CLIENT_SECRET"]

DRIVER_PATH = "http://selenium:4444/wd/hub"
OAUTH_AUTHORIZE_URL: str = "https://accounts.spotify.com/authorize"
OAUTH_ACCESS_TOKEN_URL: str = "https://accounts.spotify.com/api/token"


CLIENT_KEY_B64: str = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()


def fetch_spotify_data(dag_date, ti) -> Any:
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
        options=options,
    )
    driver.get(open_url)
    driver.find_element(By.ID, "login-username").send_keys(USERNAME)
    driver.find_element(By.ID, "login-password").send_keys(PASSWORD)
    driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div/div[2]/div/div/div[2]/div[3]/div[2]/button/div[1]/p",
    ).click()

    try:
        element = WebDriverWait(driver, timeout=240).until(EC.title_is("Google"))
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

    listens: defaultdict = defaultdict(list)
    artists: OrderedDict = OrderedDict(
        {
            "id": [],
            "name": [],
            "genre": [],
            "followers": [],
            "popularity": [],
            "url": [],
        }
    )
    tracks: OrderedDict = OrderedDict(
        {
            "id": [],
            "name": [],
            "artist_id": [],
            "duration_ms": [],
            "popularity": [],
            "is_in_album": [],
            "is_explicit": [],
            "external_url": [],
        }
    )

    for n, item in enumerate(recently_played["items"]):
        artist_id: str = item["track"]["artists"][0]["id"]
        track_id: str = item["track"]["id"]

        listens["track_id"].append(track_id)
        listens["artist_id"].append(artist_id)
        listens["time_played"].append(item["played_at"])
        listens["play_duration_ms"].append(item["track"]["duration_ms"])

        artist_response = requests.get(
            f"https://api.spotify.com/v1/artists/{artist_id}", headers=headers
        )
        artist = artist_response.json()

        if artist_id not in artists["id"]:
            artists["id"].append(artist_id)
            artists["name"].append(artist["name"])
            artists["genre"].append(artist["genres"])
            artists["followers"].append(artist["followers"]["total"])
            artists["popularity"].append(artist["popularity"])
            artists["url"].append(artist["external_urls"]["spotify"])

        track_response = requests.get(
            f"https://api.spotify.com/v1/tracks/{track_id}", headers=headers
        )
        track = track_response.json()

        if track_id not in tracks["id"]:
            tracks["id"].append(track_id)
            tracks["name"].append(track["name"])
            tracks["artist_id"].append(artist_id)
            tracks["duration_ms"].append(track["duration_ms"])
            tracks["popularity"].append(track["popularity"])
            tracks["is_in_album"].append(
                True if track["album"]["album_type"] == "album" else False
            )
            tracks["is_explicit"].append(track["explicit"])
            tracks["external_url"].append(track["external_urls"]["spotify"])

    ti.xcom_push(key="artists", value=artists)
    ti.xcom_push(key="tracks", value=tracks)
    ti.xcom_push(key="listens", value=listens)

    listens_df = pd.DataFrame(listens)
    print(listens_df)


def insert_to_aws_rds_postgres(ti):
    """Task to upload to AWS RDS Database"""
    postgres_hook = PostgresHook("aws_rds_postgres")
    conn = postgres_hook.get_conn()
    conn.set_session(autocommit=True)
    cursor = conn.cursor()

    listens = ti.xcom_pull(task_ids="Fetch-Spotify-Data", key="listens")
    artists = ti.xcom_pull(task_ids="Fetch-Spotify-Data", key="artists")
    tracks = ti.xcom_pull(task_ids="Fetch-Spotify-Data", key="tracks")

    for index in range(len(artists["id"])):
        artist_values = tuple(
            [
                artists[key][index] if (key != "genre") else str(artists[key][index])
                for key in artists.keys()
            ]
        )
        print(artist_values)

        cursor.execute(
            """
            INSERT INTO artists (id, name, genre, followers, popularity, url) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;
            """,
            vars=artist_values,
        )

    for index in range(len(tracks["id"])):
        track_values = tuple([tracks[key][index] for key in tracks.keys()])

        cursor.execute(
            """
            INSERT INTO tracks (id, name, artist_id, duration_ms, popularity, is_in_album, is_explicit, external_url) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;
            """,
            vars=track_values,
        )

    for listen_values in zip(*listens.values()):
        cursor.execute(
            """
            INSERT INTO listens (track_id, artist_id, time_played, play_duration_ms) VALUES (%s, %s, %s, %s);
            """,
            vars=listen_values,
        )

    cursor.close()
    conn.close()


default_args: Dict[str, str] = {"email": "awoyeletemiloluwa@gmail.com"}
dag = DAG(
    dag_id="spotify-ingestion-dag",
    # schedule_interval="50 23 * * *", # 11:50 pm everyday
    schedule_interval=None,
    start_date=days_ago(5),
    default_args=default_args,
)

fetch_spotify_data = PythonOperator(
    task_id="Fetch-Spotify-Data",
    python_callable=fetch_spotify_data,
    dag=dag,
    op_kwargs={"dag_date": "{{ ds }}"},
)

upload_to_aws_rds = PythonOperator(
    task_id="Insert-to-AWS-RDS-Postgres",
    python_callable=insert_to_aws_rds_postgres,
    dag=dag,
)

fetch_spotify_data >> upload_to_aws_rds

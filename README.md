# Spotify Airflow Batch Ingestion Project

#### Tools & Tech Stack: Python, Apache Airflow, Terraform, AWS

TLDR: Ingest data from Spotify's API(no SDK used) using Apache Airflow as Orchestrator

If you listen to songs on Spotify, how would you like to know more about your listening traits or habits such as: 
- what song do you listen to the most
- Which artist comes up more in the songs you listen to
- What are the audio characters of the songs you listen to
- and possibly what kind of lyrics are contained in the songs you listen to.

This is what this project deals with, by ingesting data daily from Spotify's API(no SDK used) and orchestrating the data pipeline with Apache Airflow. This Airflow server is to be deployed on AWS EC2, terraform is the IaaC tool used to setup our AWS resources.

## Architecture

![](./assets/spotify.drawio.png)



### Database ER Diagram

![](./assets/database_er.drawio.png)

### Directory Tree
assets (Images and draw.io diagrams)
├── dags
│   └── spotify
│       ├── spotify-dag.py (file where dags are saved)
├── docker-compose.yml (Docker Compose file to setup airflow)
├── Dockerfile.airflow (Dockerfile for airflow)
├── LICENSE
├── logs (Airflow logs folder)
├── Makefile
├── notebooks
│   ├── listens.csv
│   ├── Testing API.ipynb
│   └── Test Writer.ipynb
├── plugins (Airflow plugins folder)
├── README.md
├── requirements.txt (Project dependency not present in the airflow docker image)
├── sql_scripts (SQL scripts used)
│   └── create_tables.sql
└── terraform (terraform files)

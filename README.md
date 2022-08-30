# Spotify Airflow Batch Ingestion Project

TLDR: Ingest data from spotify data using Apache Airflow as Orchestrator

If you listen to songs on Spotify, how would you like to know more about your listening traits or habits such as: 
- what song do you listen to the most
- Which artist comes up more in the songs you listen to
- What are the audio characters of the songs you listen to
- and possibly what kind of lyrics are contained in the songs you listen to.

This is what this project deals with, by ingesting data daily from Spotify's API(no SDK used) and orchestrating the data pipeline with Apache Airflow. This Airflow server is to be deployed on AWS EC2.

## Architecture

![](./assets/spotify.drawio.png)



### Database ER Diagram

![](./assets/database_er.drawio.png)

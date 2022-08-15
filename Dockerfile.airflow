FROM apache/airflow:2.3.3
USER root

RUN apt-get update \
	&& apt-get install -y wget

# download chrome .deb file & webdriver for same version, 3 retries(incase of fails) & wait 5 seconds between each retry.
RUN wget \
	--tries=3 \
	--wait=5 \
	-P chrome-dev-tools \
	http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_104.0.5112.79-1_amd64.deb

RUN wget \
	--tries=3 \
	--wait=5 \
	-P chrome-dev-tools \
	https://chromedriver.storage.googleapis.com/104.0.5112.79/chromedriver_linux64.zip

RUN apt-get install -y \
	./chrome-dev-tools/google-chrome-stable_104.0.5112.79-1_amd64.deb

RUN apt-get install -y unzip
RUN unzip -q -d chrome-dev-tools  ./chrome-dev-tools/chromedriver_linux64.zip

USER airflow

COPY requirements.txt .

RUN pip install -r requirements.txt
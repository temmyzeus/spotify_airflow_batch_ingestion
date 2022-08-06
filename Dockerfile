FROM apache/airflow:2.3.3
COPY requirements.txt .
RUN pip install -r requirements.txt
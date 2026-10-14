FROM python:alpine
COPY requirements.txt .
COPY mqtt2SQL.py .
RUN pip install -r requirements.txt
ENV MQTT_BROKER=127.0.0.1
ENV MQTT_TOPIC=localhost/sql
ENV MQTT_PORT=1883
ENV SQL_SERVER=127.0.0.1
ENV SQL_PORT=3306
ENV SQL_DB=my_database
ENV SQL_USER=sa
ENV SQL_PASSWORD=password
ENV SQL_SECRET=""
CMD ["python","-u","mqtt2SQL.py"]
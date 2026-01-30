FROM python:alpine
COPY requirements.txt .
COPY mqtt2SQL.py .
RUN pip install -r requirements.txt
CMD ["python", "mqtt2SQL.py"]
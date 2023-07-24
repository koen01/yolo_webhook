FROM python:3.8-slim-buster

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt

EXPOSE 5000

# Set default values for MQTT broker details as environment variables
ENV MQTT_BROKER_HOST=192.168.1.191
ENV MQTT_BROKER_PORT=1883
ENV MQTT_TOPIC_RESULTS=yolo_detection/results
ENV MQTT_TOPIC_IMAGE=yolo_detection/image
ENV FLASK_PORT=5000
ENV MODELCONF=0.50

CMD ["python", "yolo-check.py"]

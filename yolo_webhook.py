from flask import Flask, request
import torch
import numpy as np
from PIL import Image
import paho.mqtt.client as mqtt
import requests
from io import BytesIO
import json

app = Flask(__name__)

# Set the MQTT broker details
MQTT_BROKER_HOST = "192.168.1.191"
MQTT_BROKER_PORT = 1883
MQTT_TOPIC = "yolo_detection"

# Function to send MQTT message
def publish_mqtt_message(results_json):
    client = mqtt.Client()
    client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)

    # Publish
    client.publish(MQTT_TOPIC, str(results_json))
    client.loop(2)
    client.disconnect()

# Function to count the occurrences
def count_name_occurrences(json_array):
    name_counts = {}
    data = json.loads(json_array)

    for item in data:
        name = item.get('name')
        if name:
            name_counts[name] = name_counts.get(name, 0) + 1

    return json.dumps(name_counts)

# Load the YOLO model
model = torch.hub.load('ultralytics/yolov5', 'yolov5x')

# setup the flask webhook route
@app.route('/yolo_webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()  # Parse the JSON data from the request
        url = data.get('url')  # Get the 'url' value from the JSON data

        if url:

           # Get the image
           response = requests.get(url)
           image = Image.open(BytesIO(response.content))
           image = np.asarray(image)

           # run the prediction
           results = model(image)
           results_json = results.pandas().xyxy[0].to_json(orient="records")

           results_counted = count_name_occurrences(results_json)

           # Publish to mqtt
           publish_mqtt_message(results_counted)

           print(results.pandas().xyxy[0].value_counts('name'))

           # Return the json results
           return("MQTT Message sent!"), 200

        else:
            return "Invalid JSON data or missing 'url' field", 400

    except Exception as e:
        return str(e), 500

app.run(host='0.0.0.0', port=5000)

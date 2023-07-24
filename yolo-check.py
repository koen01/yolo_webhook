from flask import Flask, request
import torch
import numpy as np
from PIL import Image
import paho.mqtt.publish as publish
import requests
from io import BytesIO
import json
import os
import base64

app = Flask(__name__)

# Get the environment variables passed by the container
MQTT_BROKER_HOST = os.environ['MQTT_BROKER_HOST']
MQTT_BROKER_PORT = int(os.environ['MQTT_BROKER_PORT'])
MQTT_TOPIC_RESULTS = os.environ['MQTT_TOPIC_RESULTS']
MQTT_TOPIC_IMAGE = os.environ['MQTT_TOPIC_IMAGE']
MODELCONF = float(os.environ['MODELCONF'])
FLASK_PORT = int(os.environ['FLASK_PORT'])

# Function to send MQTT message
def publish_mqtt_message(results_counted, results_image):
    # Publish the results
    publish.single(MQTT_TOPIC_RESULTS, results_counted, hostname=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)

    # Publish the image
    binary_fc = open(results_image, 'rb').read()
    base64_utf8_str = base64.b64encode(binary_fc).decode('utf-8')
    publish.single(MQTT_TOPIC_IMAGE, base64_utf8_str, hostname=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)

# Function to count the occurrences
def count_name_occurrences(json_array):
    name_counts = {}
    data = json.loads(json_array)

    for item in data:
        name = item.get('name')
        confidence = item.get('confidence')
        if name:
            if name in name_counts:
                name_counts[name]['count'] += 1
                name_counts[name]['confidence'].append(confidence)
            else:
                name_counts[name] = {'count': 1, 'confidence': [confidence]}

    return json.dumps(name_counts)

# Load the YOLO model
model = torch.hub.load('ultralytics/yolov5', 'yolov5x')
model.classes = [0]
model.conf = MODELCONF

# Setup the flask webhook route
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

            # Run the prediction
            results = model(image)
            results_json = results.pandas().xyxy[0].to_json(orient="records")
            print(results_json)
            # Generate an image with the bounding boxes
            results.render()  # updates results.imgs with boxes and labels
            img_savename = f"results.png"
            results_image = Image.fromarray(results.ims[0]).save(img_savename)

            # Count the results by name
            results_counted = count_name_occurrences(results_json)

            if results_json != '[]':
                # Publish to MQTT
                publish_mqtt_message(results_counted, img_savename)

                # Return the JSON results
                return "MQTT Message sent!", 200
            else:
                return "No person in results",200
        else:
            return "Invalid JSON data or missing 'url' field", 400

    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=FLASK_PORT)

# YOLOv5 Object Detection Webhook

This code implements a Flask web application that serves as a webhook for performing object detection using the YOLOv5 model. The webhook accepts JSON data containing an image URL, runs the YOLOv5 model on the image, counts the occurrences of detected objects, and publishes the results to an MQTT broker. The webhook can be run as a Docker container, and certain environment variables need to be set for proper configuration.

## How to Run with Docker

To run this webhook using Docker, follow these steps:

1. Make sure you have Docker installed on your system.

2. Clone the repository and navigate to the directory containing the `Dockerfile` and this `README.md`.

3. Build the Docker image by running the following command:
   ```
   docker build -t yolo_webhook .
   ```

4. Set the necessary environment variables before running the Docker container. These environment variables configure the MQTT broker and other parameters used by the webhook. The required environment variables are as follows:

   - `MQTT_BROKER_HOST`: The hostname or IP address of the MQTT broker.
   - `MQTT_BROKER_PORT`: The port number used to connect to the MQTT broker (integer).
   - `MQTT_TOPIC_RESULTS`: The MQTT topic where the results will be published.
   - `MQTT_TOPIC_IMAGE`: The MQTT topic where the annotated image will be published.
   - `MODELCONF`: The confidence threshold for object detection (float). This determines the minimum confidence score required for an object to be detected.
   - `FLASK_PORT`: The port on which the Flask server will run inside the container (integer).

   Set these environment variables when running the Docker container. For example:
   ```
   docker run -d -p 5000:5000 -e MQTT_BROKER_HOST=<MQTT_BROKER_HOST> -e MQTT_BROKER_PORT=<MQTT_BROKER_PORT> -e MQTT_TOPIC_RESULTS=<MQTT_TOPIC_RESULTS> -e MQTT_TOPIC_IMAGE=<MQTT_TOPIC_IMAGE> -e MODELCONF=<MODELCONF> -e FLASK_PORT=<FLASK_PORT> yolo_webhook
   ```
   Replace `<MQTT_BROKER_HOST>`, `<MQTT_BROKER_PORT>`, `<MQTT_TOPIC_RESULTS>`, `<MQTT_TOPIC_IMAGE>`, `<MODELCONF>`, and `<FLASK_PORT>` with the appropriate values.

5. The webhook should now be running inside the Docker container and accessible on the specified port (`FLASK_PORT`). It will be ready to accept JSON data for object detection.

## How the Webhook Works

The webhook provides a single endpoint, `/yolo_webhook`, that accepts HTTP POST requests containing JSON data. The JSON data must include a field named `url` with the URL of the image to be processed.

1. When a POST request is received, the webhook retrieves the JSON data from the request and extracts the image URL.

2. It then downloads the image from the specified URL.

3. The YOLOv5 model is loaded (`yolov5x` version) using the `torch.hub.load` function.

4. The downloaded image is processed using the YOLOv5 model to perform object detection.

5. The results are counted, and a JSON object is generated with the counts of each detected object class and their corresponding confidences.

6. If any objects are detected, the webhook publishes the JSON results to the specified MQTT broker and topic using the `publish_mqtt_message` function.

7. Additionally, the webhook generates an image with bounding boxes around the detected objects and publishes the base64-encoded image to the MQTT broker as well.

8. The webhook responds with an appropriate message indicating whether the detection was successful or if there were no detected objects.

9. If any error occurs during the process, an error message with the corresponding status code is returned.


## Example `curl` Command for Calling the Webhook

To make a POST request to the webhook endpoint `/yolo_webhook` with JSON data containing the image URL, use the following `curl` command:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"url": "<IMAGE_URL>"}' http://localhost:<FLASK_PORT>/yolo_webhook
```

### Explanation of the Command:

- `curl`: The command-line tool used for transferring data with URLs.

- `-X POST`: Specifies that the request should be a POST request.

- `-H "Content-Type: application/json"`: Sets the "Content-Type" header to indicate that the request body contains JSON data.

- `-d '{"url": "<IMAGE_URL>"}'`: The JSON data to be sent in the request body. Replace `<IMAGE_URL>` with the URL of the image you want to process.

- `http://localhost:<FLASK_PORT>/yolo_webhook`: The URL of the webhook's endpoint. Replace `<FLASK_PORT>` with the port number on which the Flask server is running inside the Docker container (the same port used when running the container with the `-e FLASK_PORT=<PORT>` option).


### Example Usage with Actual Values:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"url": "https://example.com/image.jpg"}' http://localhost:5000/yolo_webhook
```

In this example, the `curl` command sends a POST request to the webhook with the image URL `https://example.com/image.jpg`. The webhook will process the image and perform object detection using the YOLOv5 model.

Please ensure that the webhook is running as a Docker container on your system before making the `curl` request. Adjust the `localhost` part of the URL accordingly if the webhook is running on a different host.

---

## Explanation of the JSON Output in the "Results" Topic

The JSON output published to the "results" topic contains information about the detected objects, specifically the count of each detected object class and the confidence scores associated with each detection. Let's break down the sample JSON output you provided:

```json
{
  "person": {
    "count": 1,
    "confidence": [0.8423805237]
  }
}
```

### Explanation of the JSON Fields:

- `"person"`: This is the class label of the detected object. In this case, it represents the "person" class.

- `"count": 1`: This indicates the number of instances of the "person" class detected in the image. In the sample output, there is one instance of a person detected.

- `"confidence": [0.8423805237]`: This is an array containing the confidence scores for the detections of the "person" class. Confidence score represents the model's confidence level in the correctness of the detection. It ranges from 0 to 1, where 1 is the highest confidence. In the sample output, the detected person has a confidence score of approximately 0.842 (or 84.2%).

If there were multiple "person" instances detected in the image, the JSON output might look like this:

```json
{
  "person": {
    "count": 2,
    "confidence": [0.8423805237, 0.9261578324]
  }
}
```

In this case, two instances of the "person" class were detected, and the associated confidence scores for each detection are given in the `confidence` array.

The webhook's purpose is to count the occurrences of different object classes and their respective confidences and then publish this summarized information to the "results" topic, allowing clients subscribed to this topic to receive and process the detection results.

---

**Important**: Before running the webhook with Docker, make sure to properly configure the MQTT broker. Also, ensure that the proper permissions are given for accessing the MQTT broker from within the Docker container.

For more information about YOLOv5, Flask, and Paho MQTT, refer to their respective documentations.

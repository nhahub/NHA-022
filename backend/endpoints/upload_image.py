from flask import request, jsonify
from model import detect
import numpy as np
from kafka_producer import kafka_producer
from datetime import datetime
import json

def detect_endpoint():

  # Check if image is in request
  if 'image' not in request.files:
    return jsonify({'error': 'No image part in the request'}), 400
  
  file = request.files['image']

  # Check if a file was actually selected
  if file.filename == '':
    return jsonify({'error': 'No file selected'}), 400
  
  try:
    in_memory_image = file.read()

    # Convert the byte data to a NumPy array
    nparr = np.frombuffer(in_memory_image, np.uint8)

    lon = float(request.form.get("lon"))
    lat = float(request.form.get("lat"))
    time = datetime.now().isoformat()
    ppm = float(request.form.get("ppm"))

    # list of cracks and its confidence
    # lon, lat, time to be identifier for the image name
    # that will be saved to the data lake
    labels_list = detect(nparr, lon, lat, time)

    # Organize the data
    res = {
      "lon": lon,
      "lat": lat,
      "time": time,
      "labels": labels_list,
      "ppm": ppm, # pixel per meter
      "image": f"{lon}_{lat}_{time}.jpg" # image name in azure datalake in folder /raw
    }

    # Send data to kafka topic
    kafka_producer.send('test', json.dumps(res))
    kafka_producer.flush()

    # Response to the user
    return jsonify(res)
  
  except Exception as e:
    return jsonify({'error': str(e)}), 500
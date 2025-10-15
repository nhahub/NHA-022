from flask import request, jsonify
from model import detect
import numpy as np
from kafka_producer import kafka_producer
from datetime import datetime
import json
import base64

def detect_endpoint(data):
  
  try:
    # prepare comming base64 images for the model
    base64_string = data['img']
        
    # Remove data URL prefix if present
    if base64_string.startswith('data:image'):
      base64_string = base64_string.split(',')[1]
        
    # 1. Decode base64 to bytes
    image_bytes = base64.b64decode(base64_string)
        
    # 2. Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)

    # prepare other metadata
    lon = float(data["lon"])
    lat = float(data["lat"])
    ppm = float(data["ppm"])
    time = datetime.now().isoformat()

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

    # Response to the user
    return res
  
  except Exception as e:
    return {'error': str(e)}
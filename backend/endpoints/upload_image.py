import os
from flask import request, jsonify, send_file
from model import detect
import numpy as np

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

    labels_list = detect(nparr)

    return jsonify(labels_list)
  
  except Exception as e:
    return jsonify({'error': str(e)}), 500
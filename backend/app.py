from flask import Flask, request, jsonify, send_file
import os
from model import detect

app = Flask(__name__)

# Create folders if not exists ------------------------------------------------------------
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Just to test the backend is running ------------------------------------------------------
@app.route('/', methods=['GET'])
def init():
  return "App is working !"

# -------------------------------------------------------------------------------------------
"""
Get image from flutter application
Save them into "uploads" directory
Apply DL model on it
"""
@app.route('/upload-image', methods=['POST'])
def detect_endpoint():

  # Check if image is in request
  if 'image' not in request.files:
    return jsonify({'error': 'No image part in the request'}), 400
  
  file = request.files['image']

  # Check if a file was actually selected
  if file.filename == '':
    return jsonify({'error': 'No file selected'}), 400
  
  try:
    # Optional: save uploaded image
    image_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(image_path)

    detect(image_path)
    
    return send_file('./processed/output.jpg')
  
  except Exception as e:
    return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------------------------------------------
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
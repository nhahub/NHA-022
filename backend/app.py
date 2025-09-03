from flask import Flask
import os

# Upload endpoints functions
from endpoints.upload_image import detect_endpoint
from endpoints.test import test

app = Flask(__name__)

# Create folders if not exists ------------------------------------------------------------
os.makedirs('processed', exist_ok=True)

# Just to test the backend is running ------------------------------------------------------
@app.route('/', methods=['GET'])
def root():
  return test()

# -------------------------------------------------------------------------------------------
"""
Get image from flutter application
Save them into "uploads" directory
Apply DL model on it
"""
@app.route('/upload-image', methods=['POST'])
def upload_image():
  return detect_endpoint()

# ---------------------------------------------------------------------------------------------
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
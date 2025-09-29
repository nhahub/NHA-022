import cv2
import numpy as np
from ultralytics import YOLO
from upload_to_datalake import upload_to_datalake
from upload_to_osb import upload_to_s3_compatible

# Load the model (Yolo v8s)
model = YOLO("../models/yolo v8/YOLOv8_Small_RDD.pt")

def detect(nparr, lon, lat, time):
  # Decode the image using OpenCV
  image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

  # Run inference on a folder
  results = model.predict(source=image, conf=0.25, save=False)

  # to check if any object was detected
  labels = []

  # Iterate through results
  for result in results:
      boxes = result.boxes  # Boxes object

      # Convert to CPU and numpy for easier access
      for box in boxes:
          cls_id = int(box.cls.cpu().numpy()[0])        # Class ID
          conf = float(box.conf.cpu().numpy()[0])        # Confidence
          xyxy = box.xyxy.cpu().numpy()[0]               # Bounding box (x1, y1, x2, y2)

          # Get class name from model.names dictionary
          class_name = model.names[cls_id]

          labels.append({
            "label": class_name,
            "confidence": float(conf),
            "x1": float(xyxy[0]),
            "y1": float(xyxy[1]),
            "x2": float(xyxy[2]),
            "y2": float(xyxy[3]),
          })
  
  # if there is labels Save processed image with labels 
  # Will store in Azure data lake in the future
  if len(labels) > 0:
    pass
    # For local testing only
    # cv2.imwrite('./processed/output.jpg', image)

    # Successfully working
    # If you want to push images that have cracks to Azure Data Lake
    # Just uncomment on real prodction or simple tests to avoid wasting the free plan
    # upload_to_datalake(image, f'raw/{lon}_{lat}_{time}.jpg')

    # If you want to push images that have cracks to OBS
    upload_to_s3_compatible(image, f'raw/{lon}_{lat}_{time}.jpg')

  # Return whether any labels were detected
  return labels
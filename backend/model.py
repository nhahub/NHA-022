import cv2
import numpy as np
import matplotlib.pyplot as plt

def detect(image_path):

  # Load YOLOv2 model
  net = cv2.dnn.readNet(
    './yolo v2/dpm-cfg/backup/yolo-dpm_final.weights', 
    './yolo v2/cfg/yolo-dpm.cfg')

  # Load the COCO class labels
  with open('./yolo v2/cfg/dpm.names', 'r') as f:
      classes = [line.strip() for line in f.readlines()]


  # Load an image
  image = cv2.imread(image_path)
  height, width, _ = image.shape

  # Prepare the image for YOLOv2
  blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
  net.setInput(blob)
  layer_names = net.getLayerNames()
  output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

  # Run the model
  outputs = net.forward(output_layers)

  # Process the outputs
  for out in outputs:
      for detection in out:
          scores = detection[5:]
          class_id = np.argmax(scores)
          confidence = scores[class_id]
          if confidence > 0.5:  # Filter predictions with low confidence
              center_x = int(detection[0] * width)
              center_y = int(detection[1] * height)
              w = int(detection[2] * width)
              h = int(detection[3] * height)
              x = center_x - w // 2
              y = center_y - h // 2

              # Draw bounding box
              cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
              cv2.putText(image, f'{classes[class_id]} {confidence:.2f}', (x, y - 10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
              
  # Run the model
  outputs = net.forward(output_layers)

  # Process the outputs
  for out in outputs:
      for detection in out:
          scores = detection[5:]
          class_id = np.argmax(scores)
          confidence = scores[class_id]
          if confidence > 0.5:  # Filter predictions with low confidence
              center_x = int(detection[0] * width)
              center_y = int(detection[1] * height)
              w = int(detection[2] * width)
              h = int(detection[3] * height)
              x = center_x - w // 2
              y = center_y - h // 2

              # Draw bounding box
              cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
              cv2.putText(image, f'{classes[class_id]} {confidence:.2f}', (x, y - 10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
              
  cv2.imwrite('./processed/output.jpg', image)
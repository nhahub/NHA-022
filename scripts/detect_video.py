from ultralytics import YOLO
import cv2
import torch

# -------------------- SETTINGS --------------------
MODEL_PATH = "../models/fine_tunning/runs/main_trainging/yolov8s/weights/best.pt"  # path to your YOLOv8s model
VIDEO_PATH = r"C:\Users\yahia\Downloads\case study 3 merged video - Made with Clipchamp.mp4"                    # path to your large video
OUTPUT_PATH = "../data/output_with_boxes.mp4"             # output video with detections
IMG_SIZE = 640                                    # inference image size
# --------------------------------------------------

# Load YOLOv8 model
model = YOLO(MODEL_PATH)

# Use GPU if available
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)
print(f"Using device: {device}")

# Open input video
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise Exception(f"Cannot open video file: {VIDEO_PATH}")

# Get video properties
fps = int(cap.get(cv2.CAP_PROP_FPS))
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

print(f"Processing video: {VIDEO_PATH}")
print(f"Resolution: {frame_width}x{frame_height}, FPS: {fps}, Total frames: {total_frames}")

# Set up video writer (MP4 output)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(OUTPUT_PATH, fourcc, fps, (frame_width, frame_height))

# Process frames
frame_idx = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLOv8 detection
    results = model(frame, imgsz=IMG_SIZE, verbose=False)
    annotated_frame = results[0].plot()  # draw detections on frame

    # Write the annotated frame to output
    out.write(annotated_frame)

    # Print progress every 50 frames
    frame_idx += 1
    if frame_idx % 50 == 0:
        print(f"Processed {frame_idx}/{total_frames} frames...")

# Release resources
cap.release()
out.release()

print(f"✅ Done! Saved annotated video to: {OUTPUT_PATH}")

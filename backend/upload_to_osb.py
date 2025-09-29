import io
import cv2
import boto3
from dotenv import load_dotenv
import os
from botocore.exceptions import ClientError
from botocore.client import Config

load_dotenv()

HUAWEI_AK = os.getenv("HUAWEI_AK")
HUAWEI_SK = os.getenv("HUAWEI_SK")
HUAWEI_ENDPOINT = os.getenv("HUAWEI_ENDPOINT")
BUCKET = os.getenv("BUCKET")

s3 = boto3.client(
  "s3",
  region_name="ap-southeast-3",
  endpoint_url=HUAWEI_ENDPOINT,
  aws_access_key_id=HUAWEI_AK,
  aws_secret_access_key=HUAWEI_SK,
    config=Config(
        signature_version="s3",
        s3={"addressing_style": "virtual"}
    )
)

def upload_to_s3_compatible(image, object_key, bucket=BUCKET, client=s3):
    ok, buffer = cv2.imencode(".jpg", image)
    if not ok:
        raise ValueError("Could not encode image to JPG")

    data = io.BytesIO(buffer.tobytes())

    try:
        client.upload_fileobj(
            data,
            bucket,
            object_key,
            ExtraArgs={"ContentType": "image/jpeg"}
        )
        print(f"✅ Uploaded {object_key} to {bucket} via S3-compatible endpoint")
    except ClientError as e:
        print(f"❌ Upload failed: {e}")
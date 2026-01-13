import cv2
import io
import os
import time
import random
import numpy as np
from datetime import datetime
from minio import Minio
from collections import namedtuple

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "host.docker.internal:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

bucket_name = "camera-dataset"
if not client.bucket_exists(bucket_name):
    client.make_bucket(bucket_name)

Box = namedtuple("Box", ["cls", "xywhn"])

def upload_to_minio(img, boxes_list, cam_id, timestamp):
    _, img_encoded = cv2.imencode('.jpg', img)
    img_data = img_encoded.tobytes()
    img_path = f"{cam_id}/{timestamp}.jpg"
    client.put_object(bucket_name, img_path, io.BytesIO(img_data), len(img_data))
    
    label_content = ""
    for box in boxes_list:
        c = int(box.cls)
        coords = box.xywhn[0].tolist()
        label_content += f"{c} {' '.join(map(str, coords))}\n"
    if label_content:
        label_data = label_content.encode('utf-8')
        label_path = f"{cam_id}/{timestamp}.txt"
        client.put_object(bucket_name, label_path, io.BytesIO(label_data), len(label_data))

def stream_test(num_frames=10, interval_sec=2, cam_id="cam_test"):
    for i in range(num_frames):
        img = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        num_boxes = random.randint(0, 3)
        boxes = [Box(cls=random.randint(0, 2), xywhn=np.random.rand(1, 5)) for _ in range(num_boxes)]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        upload_to_minio(img, boxes, cam_id, timestamp)
        print(f"Uploaded frame {i+1}/{num_frames} -> {cam_id}/{timestamp}.jpg (+labels)")
        time.sleep(interval_sec)

if __name__ == "__main__":
    stream_test(num_frames=5, interval_sec=1)

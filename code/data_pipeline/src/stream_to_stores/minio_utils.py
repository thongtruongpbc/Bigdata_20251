import cv2
import io, os
from minio import Minio

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "host.docker.internal:9000") # Dùng host.docker.internal nếu chạy trong container
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

def upload_to_minio(img, boxes_list, cam_id, timestamp):
    # 1. Upload Image
    _, img_encoded = cv2.imencode('.jpg', img)
    img_data = img_encoded.tobytes()
    img_path = f"{cam_id}/{timestamp}.jpg"
    client.put_object(bucket_name, img_path, io.BytesIO(img_data), len(img_data))

    # 2. Upload YOLO Labels (YOLO format: class x_center y_center width height)
    label_content = ""
    for box in boxes_list:
        c = int(box.cls)
        coords = box.xywhn[0].cpu().numpy().tolist() 
        label_content += f"{c} {' '.join(map(str, coords))}\n"
    
    if label_content:
        label_data = label_content.encode('utf-8')
        label_path = f"{cam_id}/{timestamp}.txt"
        client.put_object(bucket_name, label_path, io.BytesIO(label_data), len(label_data))
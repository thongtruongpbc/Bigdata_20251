from kafka import KafkaProducer
import json
import base64

producer = KafkaProducer(
    bootstrap_servers='localhost:29092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

payload = {
    "id_camera": "cam_001",
    "timestamp": "2026-01-12T18:50:00",
    "image_data": base64.b64encode(b"fake_image_data").decode()
}

producer.send("camera_stream", payload)
producer.flush()
print("Message sent")

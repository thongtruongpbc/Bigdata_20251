from kafka import KafkaProducer, KafkaConsumer
import json

TOPIC = "camera_stream"
BROKER = "localhost:29092"

# --- Producer test ---
producer = KafkaProducer(
    bootstrap_servers=BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

msg = {
    "id_camera": "cam_001",
    "timestamp": "2026-01-12T18:30:00",
    "image_data": "BASE64_STRING"
}

producer.send(TOPIC, msg)
producer.flush()
print("Message sent")

# --- Consumer test ---
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BROKER,
    auto_offset_reset="earliest",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    consumer_timeout_ms=2000
)

for m in consumer:
    print("Received:", m.value)

import argparse
import json
import logging
import sys
import base64
import cv2
import asyncio

from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import NoBrokersAvailable, KafkaTimeoutError

from cameras import cameras
from utils import get_image, get_cur_time
from tornado.httpclient import AsyncHTTPClient

#LOGGING
logger = logging.getLogger("CameraProducer")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

logging.getLogger('tornado.general').setLevel(logging.ERROR)
logging.getLogger('tornado.access').setLevel(logging.ERROR)
logging.getLogger('tornado.application').setLevel(logging.ERROR)


# KAFKA CONNECT
async def connect_kafka(args, retry=20, delay=10):
    for i in range(1, retry + 1):
        try:
            producer = KafkaProducer(
            bootstrap_servers=args.bootstrap_servers,
            client_id="camera_stream_producer",
            acks=1,
            retries=5,
            linger_ms=100,                 # gom batch
            batch_size=65536,              # 64KB
            buffer_memory=134217728,       # 128MB
            request_timeout_ms=30000,
            max_block_ms=30000,
            metadata_max_age_ms=300000,
            max_request_size=10485760,     # 10MB
            key_serializer=lambda k: k.encode("utf-8"),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )


            admin = KafkaAdminClient(
                bootstrap_servers=args.bootstrap_servers,
                client_id="camera_stream_admin",
                request_timeout_ms=30000
            )

            logger.info(f"Kafka connected successfully (attempt {i})")
            return producer, admin

        except Exception as e:
            logger.error(f"Kafka connection failed ({i}/{retry}): {e}")
            await asyncio.sleep(delay)

    return None, None


async def main(args):
    http_client = AsyncHTTPClient(max_clients=10)

    producer, admin = await connect_kafka(args)
    if not producer:
        logger.error("Could not connect to Kafka. Exiting.")
        return

    #Create topic 
    try:
        admin.create_topics([
            NewTopic(
                name=args.topic_name,
                num_partitions=len(cameras),
                replication_factor=1
            )
        ])
        logger.info(f"Created topic: {args.topic_name}")
    except Exception:
        logger.info(f"Topic '{args.topic_name}' already exists")

    logger.info("Starting camera streaming...")

    while True:
        for cam_info in cameras:
            url = (
                "http://giaothong.hochiminhcity.gov.vn/"
                f"render/ImageHandler.ashx?id={cam_info['id_camera']}"
            )

            try:
                # -------- Fetch image --------
                image_np = await get_image(url, http_client)
                if image_np is None:
                    logger.warning(f"No image from {cam_info['name']}")
                    continue

                success, buffer = cv2.imencode('.jpg', image_np)
                if not success:
                    logger.error(f"Encode failed: {cam_info['name']}")
                    continue

                payload = {
                    "id_camera": cam_info["id_camera"],
                    "name_camera": cam_info["name"],
                    "timestamp": get_cur_time(),
                    "image_data": base64.b64encode(buffer).decode("utf-8")
                }

                # -------- Send to Kafka --------
                try:
                    future = producer.send(
                        args.topic_name,
                        key=cam_info["id_camera"],
                        value=payload
                    )
                    future.get(timeout=30) 
                    logger.info(f"Sent: {cam_info['name']} at {payload['timestamp']}")

                except (NoBrokersAvailable, KafkaTimeoutError) as e:
                    logger.error(f"Kafka lost: {e}. Reconnecting...")

                    try:
                        producer.close(timeout=5)
                        admin.close()
                    except Exception:
                        pass

                    producer, admin = await connect_kafka(args)
                    if not producer:
                        logger.error("Reconnect failed. Sleeping...")
                        await asyncio.sleep(10)
                        continue

            except Exception as e:
                logger.error(f"Error processing {cam_info['name']}: {e}")

            await asyncio.sleep(0.5)

        # Flush mỗi cycle
        try:
            producer.flush(timeout=5)
        except Exception:
            pass

        logger.info(f"Cycle completed. Waiting {args.interval}s...")
        await asyncio.sleep(args.interval)


# ================= ENTRY =================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kafka Live Camera Streaming")
    parser.add_argument(
        "-b", "--bootstrap_servers",
        default="localhost:9092",
        help="Kafka bootstrap servers"
    )
    parser.add_argument(
        "-t", "--topic_name",
        default="camera_stream",
        help="Kafka topic name"
    )
    parser.add_argument(
        "-i", "--interval",
        type=int,
        default=12,
        help="Sleep time between cycles (seconds)"
    )

    args = parser.parse_args()

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        logger.info("Stopping streaming...")

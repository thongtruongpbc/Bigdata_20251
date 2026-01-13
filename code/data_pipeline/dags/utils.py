from pathlib import Path
import pendulum
from airflow.models import Variable
from docker.types import Mount

class AppConst:
    DOCKER_USER = Variable.get("DOCKER_USER", "thongtx")
    # network 
    DOCKER_NETWORK = Variable.get("DOCKER_NETWORK", "stream_emitting_default") #for both (Kafka, MinIO, Redis)

class AppPath:
    CODE_DIR = '/workspaces/python3-poetry-pyenv/code'
    DATA_PIPELINE_DIR = CODE_DIR / "data_pipeline"
    FEATURE_REPO = DATA_PIPELINE_DIR / "feature_repo"
    MODEL_DIR = DATA_PIPELINE_DIR / "models" 

class DefaultConfig:
    DEFAULT_DAG_ARGS = {
        "owner": "thongtx",
        "retries": 1,
        "retry_delay": pendulum.duration(seconds=30),
    }

    DEFAULT_DOCKER_OPERATOR_ARGS = {
        "image": f"{AppConst.DOCKER_USER}/code/data_pipeline:latest",
        "api_version": "auto",
        "auto_remove": True,
        "network_mode": AppConst.DOCKER_NETWORK, 
        "mounts": [
            # Mount Feature Repo to Feast read Registry
            Mount(
                source=AppPath.FEATURE_REPO.absolute().as_posix(),
                target="/data_pipeline/feature_repo",
                type="bind",
            ),
            # Mount Model YOLO to ovoid weighted image
            Mount(
                source=AppPath.MODEL_DIR.absolute().as_posix(),
                target="/data_pipeline/models",
                type="bind",
            ),
        ],
        "environment": {
            "MINIO_ENDPOINT": "minio:9000",
            "MINIO_ACCESS_KEY": "minioadmin",
            "MINIO_SECRET_KEY": "minioadmin",
            "KAFKA_BROKER": "broker:9092",
            "REDIS_URL": "redis:6379",
        },
        "network_mode": "stream_emitting_default",
        # "docker_url": "unix://var/run/docker.sock", # for local 
    }
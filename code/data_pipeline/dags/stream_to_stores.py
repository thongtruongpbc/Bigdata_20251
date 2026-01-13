import sys
import os
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import pendulum
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from utils import DefaultConfig

# DAG
with DAG(
    dag_id="stream_to_stores",
    default_args=DefaultConfig.DEFAULT_DAG_ARGS,
    schedule_interval="@once", 
    start_date=pendulum.datetime(2022, 1, 1, tz="UTC"),
    catchup=False,
    tags=["traffic_ai", "streaming", "feast"],
) as dag:

    # Task 1: Ingest data to Online Store (Redis) for Real-time Dashboard
    stream_to_online_task = DockerOperator(
        task_id="stream_to_online_task",
        command="/bin/bash -c 'cd /data_pipeline/src/stream_to_stores && python ingest.py --mode setup --store online'",
        **DefaultConfig.DEFAULT_DOCKER_OPERATOR_ARGS,
    )

    # Task 2: Ingest data Offline Store (File) for Re-training
    stream_to_offline_task = DockerOperator(
        task_id="stream_to_offline_task",
        command="/bin/bash -c 'cd /data_pipeline/src/stream_to_stores && python ingest.py --mode setup --store offline'",
        **DefaultConfig.DEFAULT_DOCKER_OPERATOR_ARGS,
    )
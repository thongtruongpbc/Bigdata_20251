# Stage 1: Build
FROM python:3.10-slim AS build

RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY dev_requirements.txt /tmp/dev_requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r /tmp/dev_requirements.txt && \
    pip install opencv-python-headless

# Stage 2: Runtime
FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 && rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY src/stream_emitting.py src/utils.py src/cameras.py ./

ENV BOOTSTRAP_SERVERS="localhost:9092" \
    TOPIC_NAME="camera_stream" \
    INTERVAL=15

CMD ["sh", "-c", "python stream_emitting.py --bootstrap_servers ${BOOTSTRAP_SERVERS} --topic_name ${TOPIC_NAME} --interval ${INTERVAL}"]
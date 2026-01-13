# # Stage 1: Build
# FROM python:3.10-slim AS build

# RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev

# RUN python -m venv /opt/venv
# ENV PATH="/opt/venv/bin:$PATH"
# COPY requirements.txt ../tmp/requirements.txt

# RUN --mount=type=cache,target=/root/.cache/pip \
#     pip install --upgrade pip && \
#     pip install -r /tmp/requirements.txt && \
#     pip install opencv-python-headless

# # Stage 2: Runtime
# FROM python:3.10-slim

# RUN apt-get update && apt-get install -y --no-install-recommends \
#     wget ca-certificates gnupg \
#     libglib2.0-0 \
#     libssl-dev \
#     libkrb5-dev \
#     zlib1g-dev \
#     && rm -rf /var/lib/apt/lists/*

# # Install Temurin Java 11
# RUN wget -O - https://packages.adoptium.net/artifactory/api/gpg/key/public \
#     | gpg --dearmor > /usr/share/keyrings/adoptium.gpg && \
#     echo "deb [signed-by=/usr/share/keyrings/adoptium.gpg] https://packages.adoptium.net/artifactory/deb bookworm main" \
#     > /etc/apt/sources.list.d/adoptium.list && \
#     apt-get update && \
#     apt-get install -y temurin-11-jre && \
#     rm -rf /var/lib/apt/lists/*

# ENV JAVA_HOME=/usr/lib/jvm/temurin-11-jre-amd64
# ENV PATH="$JAVA_HOME/bin:$PATH"


# # Copy venv 
# COPY --from=build /opt/venv /opt/venv

# # Copy code 
# WORKDIR /data_pipeline
# COPY . .
############################
# Stage 1: Build
############################
FROM python:3.10-slim-bookworm AS build

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_PREFER_BINARY=1 \
    PIP_DEFAULT_TIMEOUT=100

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libglib2.0-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY deployment/requirements.txt /tmp/requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip \
    && pip install -r /tmp/requirements.txt \
    && pip install opencv-python-headless

############################
# Stage 2: Runtime
############################
FROM python:3.10-slim-bookworm

ENV JAVA_HOME=/usr/lib/jvm/temurin-11-jre-amd64
ENV PATH="/opt/venv/bin:$JAVA_HOME/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    gnupg \
    libglib2.0-0 \
    libssl3 \
    zlib1g \
    libkrb5-3 \
    && rm -rf /var/lib/apt/lists/*

# Install Temurin Java 11 (JRE only)
RUN wget -O - https://packages.adoptium.net/artifactory/api/gpg/key/public \
    | gpg --dearmor > /usr/share/keyrings/adoptium.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/adoptium.gpg] https://packages.adoptium.net/artifactory/deb bookworm main" \
    > /etc/apt/sources.list.d/adoptium.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends temurin-11-jre \
    && rm -rf /var/lib/apt/lists/*

# Copy venv only
COPY --from=build /opt/venv /opt/venv

WORKDIR /data_pipeline
COPY . .

#!/bin/bash

cmd=$1

# constants
DOCKER_USER="thongtx"
PROJECT="bigdata"
IMAGE_NAME="data_pipeline"
IMAGE_TAG=$(git describe --always)
FULL_IMAGE_NAME="$DOCKER_USER/$PROJECT/$IMAGE_NAME"

if [[ -z "$DOCKER_USER" ]]; then
    echo "Missing \$DOCKER_USER env var"
    exit 1
fi

usage() {
    echo "deploy.sh <command>"
    echo "Available commands:"
    echo " build          build image (using BuildKit)"
    echo " push           push image"
    echo " build_push     build and push image"
    echo " dags           deploy airflow dags"
    echo " feast_apply    apply feast changes locally"
    echo " feature_repo   deploy feature repo to other services"
    echo " test_run       run container locally for testing"
}

if [[ -z "$cmd" ]]; then
    echo "Missing command"
    usage
    exit 1
fi

build() {
    echo "📦 Building image with BuildKit..."
    # Kích hoạt BuildKit để dùng --mount=type=cache trong Dockerfile
    DOCKER_BUILDKIT=1 docker build \
        --tag $FULL_IMAGE_NAME:$IMAGE_TAG \
        -f deployment/Dockerfile .
    
    docker tag $FULL_IMAGE_NAME:$IMAGE_TAG $FULL_IMAGE_NAME:latest
}

push() {
    echo "🚀 Pushing image to Docker Hub..."
    docker push $FULL_IMAGE_NAME:$IMAGE_TAG
    docker push $FULL_IMAGE_NAME:latest
}

deploy_dags() {
    if [[ -z "$DAGS_DIR" ]]; then
        echo "Missing DAGS_DIR env var"
        exit 1
    fi
    mkdir -p "$DAGS_DIR"
    cp dags/* "$DAGS_DIR"
    echo "✅ DAGS deployed to $DAGS_DIR"
}

feast_apply() {
    echo "🍴 Applying Feast changes..."
    cd feature_repo
    source /opt/venv/bin/activate    # activate venv
    feast apply
    deactivate                        # optional
    cd ..
}

deploy_feature_repo() {
    feast_apply

    services=("training_pipeline" "model_serving" "monitoring_service")
    for service in "${services[@]}"; do
        dest="../$service"
        if [ -d "$dest" ]; then
            echo "🚚 Syncing feature_repo to $service..."
            rsync -avr data_sources "$dest/"
            rsync -avr feature_repo "$dest/" --exclude registry --exclude "*.db"
        fi
    done
    
    rsync -avr scripts ../monitoring_service/
}

test_run() {
    echo "🧪 Running test container with resource limits..."
    docker run --rm -it \
        --network host \
        --memory="2g" \
        --memory-swap="4g" \
        --cpus="1.5" \
        -e BOOTSTRAP_SERVERS="localhost:9092" \
        -v $(pwd):/data_pipeline \
        $FULL_IMAGE_NAME:latest /bin/bash
}

shift

case $cmd in
build) build "$@" ;;
push) push "$@" ;;
build_push) build "$@" && push "$@" ;;
dags) deploy_dags "$@" ;;
feast_apply) feast_apply "$@" ;;
feature_repo) deploy_feature_repo "$@" ;;
test_run) test_run "$@" ;;
*)
    echo "Unknown command: $cmd"
    usage
    exit 1
    ;;
esac
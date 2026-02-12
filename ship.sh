#!/bin/bash
set -euo pipefail

IMAGE="natbusa/open-webui-lite"
TAG="${1:-latest}"
BUILD_HASH=$(git rev-parse --short HEAD)

TAGS=("${TAG}")
if [[ "${TAG}" == "latest" ]]; then
  VERSION=$(jq -r '.version' package.json)
  TAGS+=("${VERSION}")
fi

TAG_ARGS=()
for t in "${TAGS[@]}"; do
  TAG_ARGS+=(-t "${IMAGE}:${t}")
done

echo "Building ${IMAGE} tags=[${TAGS[*]}] (SLIM=true, hash=${BUILD_HASH})"

docker build \
  --build-arg USE_SLIM=true \
  --build-arg BUILD_HASH="${BUILD_HASH}" \
  "${TAG_ARGS[@]}" \
  .

for t in "${TAGS[@]}"; do
  echo "Pushing ${IMAGE}:${t}"
  docker push "${IMAGE}:${t}"
done

echo "Done: ${IMAGE} tags=[${TAGS[*]}] (${BUILD_HASH})"

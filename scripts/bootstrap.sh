#!/usr/bin/env bash
set -euo pipefail

CLUSTER=status-dashboard
IMAGE=status-dashboard-api:0.1.0

if ! kind get clusters 2>/dev/null | grep -qx "$CLUSTER"; then
  kind create cluster --name "$CLUSTER" --config k8s/kind-config.yaml
fi

docker build -t "$IMAGE" .
kind load docker-image "$IMAGE" --name "$CLUSTER"

helm upgrade --install status charts/status \
  --namespace status --create-namespace \
  --set image.repository=status-dashboard-api \
  --set image.tag=0.1.0 \
  --wait --timeout 120s

kubectl -n status get pods

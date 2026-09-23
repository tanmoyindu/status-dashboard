# Status Dashboard

A small service that pings a set of URLs and reports their health as JSON.
Built to demonstrate a complete, tight DevOps pipeline: a tested Python app,
a non-root multi-stage container, a Kubernetes deployment via Helm with real
probes, and a CI pipeline that lints, tests, builds, and scans on every pull
request.

## Live demo output

**Deployed on a local Kubernetes cluster (kind):**
```
$ kubectl -n status get pods
NAME                      READY   STATUS    RESTARTS   AGE
status-65b7c48f9c-jgz5f   1/1     Running   1 (25s ago)   4h29m

$ kubectl -n status get deploy,svc
NAME                     READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/status   1/1     1            1           4h29m
NAME             TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)   AGE
service/status   ClusterIP   10.96.37.9    <none>        80/TCP    4h29m
```

The one restart above happened automatically after several hours of runtime
(a Docker Desktop pause during laptop sleep) — Kubernetes detected it via the
liveness probe and recovered the pod with no manual intervention, which is
the self-healing behavior the Deployment and probes are there to provide.

**Calling the API through the Service:**
```
$ curl -s localhost:9000/status | python -m json.tool
{
    "targets": [
        {
            "url": "https://github.com",
            "up": true,
            "status_code": 200,
            "latency_ms": 249.4
        },
        {
            "url": "https://example.com",
            "up": true,
            "status_code": 200,
            "latency_ms": 87.4
        }
    ],
    "all_up": true
}
```

**CI pipeline:** [PR #1](https://github.com/tanmoyindu/status-dashboard/pull/1)
— lint, test, Docker build, and a Trivy vulnerability scan, all running on
every pull request.

## Architecture

```
GitHub Actions CI ──> Docker build ──> Trivy scan
                                          │
                                          ▼
                                   kind (local k8s)
                                          │
                        Helm chart: Deployment + Service
                                          │
                              FastAPI app (2 pods max)
                              ├── /healthz  (liveness/readiness)
                              └── /status   (pings targets, returns JSON)
```

## Run it locally

**Directly with Python:**
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
curl localhost:8000/status
```

**With Docker:**
```bash
docker compose up --build
curl localhost:8000/status
```

**On Kubernetes (kind + Helm):**
```bash
./scripts/bootstrap.sh
kubectl -n status port-forward svc/status 9000:80
curl localhost:9000/status
```

## What this demonstrates

- **Containerization**: multi-stage Docker build, non-root user (UID 10001),
  dropped Linux capabilities, read-only root filesystem, built-in healthcheck
- **Kubernetes**: a Helm chart with readiness/liveness probes, resource
  requests/limits, and a ConfigMap wired to the app via `checksum/config` so
  pods roll automatically when config changes
- **CI/CD**: a GitHub Actions pipeline that fails fast on lint/test errors
  before building the image, then scans it for CRITICAL/HIGH vulnerabilities
  with Trivy
- **Self-healing**: demonstrated live above — the pod recovered automatically
  after an unexpected termination, with zero manual steps

## Possible extensions

- Push images to a registry (GHCR) and add a real CD deploy step
- Prometheus metrics endpoint and a Grafana dashboard
- GitOps deployment via Argo CD
- Horizontal Pod Autoscaler driven by request load

## Tech stack
Python · FastAPI · Docker · Kubernetes (kind) · Helm · GitHub Actions · Trivy
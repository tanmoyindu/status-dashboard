# Status Dashboard

A small service that pings a few URLs and reports their health as JSON
and a simple status page. Built to demonstrate a complete, tight
CI/CD pipeline: containerization, Kubernetes deployment via Helm,
and automated build/test/scan on every push.

## Status
 Work in progress. See the roadmap below.

## Roadmap
- [ ] 1. App: ping targets, expose /status and /healthz
- [ ] 2. Dockerfile (multi-stage, non-root)
- [ ] 3. Helm chart (Deployment, Service, probes)
- [ ] 4. CI: lint, test, build, Trivy scan
- [ ] 5. README writeup with demo screenshot

## Tech stack
Python · FastAPI · Docker · Kubernetes (kind) · Helm · GitHub Actions · Trivy

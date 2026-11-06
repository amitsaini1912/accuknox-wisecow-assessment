# Wisecow on Kubernetes (AccuKnox QA Trainee Assessment)

Cow-wisdom web server (`fortune | cowsay`) containerised and deployed to Kubernetes with CI/CD and TLS.

## Repo layout
| Path | Purpose |
|---|---|
| `wisecow.sh` | Original app (port 4499) |
| `Dockerfile` | Ubuntu image with fortune/cowsay/netcat, runs as non-root UID 10001 |
| `k8s/deployment.yaml` | 2 replicas, probes, resource limits |
| `k8s/service.yaml` | ClusterIP service `wisecow-svc` (80 → 4499) |
| `k8s/cluster-issuer.yaml`, `k8s/ingress.yaml` | TLS via cert-manager + ingress-nginx (host `wisecow.local`) |
| `.github/workflows/ci-cd.yaml` | Tests → build & push image to GHCR → deploy to kind cluster and verify |
| `scripts/` | Problem Statement 2: system health monitor + application health checker (Python) |
| `tests/` | pytest unit tests for both scripts |

## Problem Statement 1 – run locally
```bash
docker build -t wisecow . && docker run -p 4499:4499 wisecow   # http://localhost:4499

# Kubernetes (kind/minikube) with ingress-nginx + cert-manager installed
kubectl apply -f k8s/
echo "127.0.0.1 wisecow.local" | sudo tee -a /etc/hosts
curl -k https://wisecow.local
```

### CI/CD
On every push to `main`:
1. **script-tests** – runs pytest for the scripts.
2. **build-push** – builds the image, pushes `ghcr.io/<owner>/wisecow:latest` and `:<sha>`, smoke-tests the container.
3. **deploy** *(challenge)* – spins up a kind cluster, installs ingress-nginx + cert-manager, deploys the manifests, waits for rollout and the TLS certificate, then curls the service.

### TLS *(challenge)*
cert-manager issues `wisecow-tls` for `wisecow.local`; ingress-nginx terminates TLS and redirects HTTP → HTTPS. For a public domain, replace the self-signed `ClusterIssuer` with a Let's Encrypt ACME issuer.

## Problem Statement 2 – scripts (chosen: #1 and #4)
```bash
pip install -r scripts/requirements.txt
python3 scripts/system_health_monitor.py --interval 5          # alerts when CPU/mem/disk > 80% or procs > 400
python3 scripts/app_health_checker.py https://wisecow.local --insecure   # prints UP/DOWN, exit 0/1
pytest -q tests
```
- **Health monitor**: logs to console and `system_health.log`; on alert lists top-5 CPU processes.
- **App health checker**: 2xx/3xx = UP; 4xx = DOWN (no retry); 5xx/timeout/connection error retried with backoff, then DOWN; TLS errors reported.

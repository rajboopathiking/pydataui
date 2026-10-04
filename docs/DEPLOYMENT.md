> **Multi-Worker & Persistent Storage:** PyDataUI v0.2.1 includes a zero-infrastructure SQLite WAL storage engine (`pydataui.storage`).
> For multi-worker deployments (`--workers 4+`) or container volume mounts, configure `PYDATAUI_STORAGE=sqlite:///var/data/pydataui_storage.db`
> or let PyDataUI auto-configure `.pydataui_storage.db`.
> Read [the production readiness guide](PRODUCTION_READINESS.md) for architecture details.

# Production Deployment Guide

PyDataUI is designed from the ground up for high-throughput production workloads. Built on the **pyrustapi** engine (Rust/Tokio/Hyper), it does not require external Python application servers like Uvicorn or Gunicorn.

---

## Table of Contents
1. [One-Click Docker Build via CLI](#1-one-click-docker-build-via-cli)
2. [Production Dockerfile](#2-production-dockerfile)
3. [Docker Compose Deployment](#3-docker-compose-deployment)
4. [Kubernetes Manifests](#4-kubernetes-manifests)
5. [Systemd Service (Linux Server)](#5-systemd-service-linux-server)
6. [Nginx Reverse Proxy Configuration](#6-nginx-reverse-proxy-configuration)
7. [Environment Variables Reference](#7-environment-variables-reference)
8. [Production Security Checklist](#8-production-security-checklist)

---

## 1. One-Click Docker Build via CLI

PyDataUI includes an automated build command that creates a production-ready container directory:

```bash
pydataui build app.py --output dist
```

This packages:
- `dist/app.py`
- `dist/static/` (bundled HTMX & CSS assets)
- `dist/Dockerfile`
- `dist/docker-compose.yml`
- `dist/requirements.txt`

Build and run:
```bash
cd dist
docker compose up --build -d
```

---

## 2. Production Dockerfile

If creating your own Dockerfile:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set production environment variables
ENV PYDATAUI_HOST=0.0.0.0
ENV PYDATAUI_PORT=8000
ENV PYDATAUI_DEBUG=false
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Run with pyrustapi multi-worker engine
CMD ["pydataui", "run", "app.py", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
```

---

## 3. Docker Compose Deployment

```yaml
version: '3.8'

services:
  pydataui:
    build: .
    restart: always
    ports:
      - "8000:8000"
    environment:
      - PYDATAUI_HOST=0.0.0.0
      - PYDATAUI_PORT=8000
      - PYDATAUI_SESSION_SECRET=${PYDATAUI_SESSION_SECRET:-a-very-long-production-secret-token-min-32-chars}
      - PYDATAUI_SESSION_MAX_AGE=86400
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/_pdu/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2048M
```

---

## 4. Kubernetes Manifests

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pydataui-app
  labels:
    app: pydataui
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pydataui
  template:
    metadata:
      labels:
        app: pydataui
    spec:
      containers:
      - name: web
        image: your-registry.com/data/pydataui-app:v0.2.0
        ports:
        - containerPort: 8000
        env:
        - name: PYDATAUI_HOST
          value: "0.0.0.0"
        - name: PYDATAUI_PORT
          value: "8000"
        - name: PYDATAUI_SESSION_SECRET
          valueFrom:
            secretKeyRef:
              name: pdu-secrets
              key: session-secret
        livenessProbe:
          httpGet:
            path: /_pdu/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /_pdu/health
            port: 8000
          initialDelaySeconds: 2
          periodSeconds: 5
        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
          limits:
            cpu: "1000m"
            memory: "1024Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: pydataui-service
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: pydataui
```

---

## 5. Systemd Service (Linux Server)

Create `/etc/systemd/system/pydataui.service`:

```ini
[Unit]
Description=PyDataUI Production Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/my-pydataui-app
Environment="PATH=/var/www/my-pydataui-app/venv/bin"
Environment="PYDATAUI_HOST=127.0.0.1"
Environment="PYDATAUI_PORT=8000"
Environment="PYDATAUI_SESSION_SECRET=your-32-char-random-secret-key-here"
ExecStart=/var/www/my-pydataui-app/venv/bin/pydataui run app.py --host 127.0.0.1 --port 8000 --workers 1
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now pydataui
```

---

## 6. Nginx Reverse Proxy Configuration

```nginx
server {
    listen 80;
    server_name analytics.company.internal;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name analytics.company.internal;

    ssl_certificate /etc/letsencrypt/live/analytics.company.internal/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/analytics.company.internal/privkey.pem;

    # Static assets cache
    location /_pdu/static/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        expires 7d;
        add_header Cache-Control "public, no-transform";
    }

    # Application & HTMX traffic
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket / Long-lived requests
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 300s;
    }
}
```

---

## 7. Environment Variables Reference

All PyDataUI settings can be configured via environment variables prefixed with `PYDATAUI_`:

| Variable | Default | Description |
|---|---|---|
| `PYDATAUI_TITLE` | `PyDataUI App` | Application browser title |
| `PYDATAUI_HOST` | `127.0.0.1` | Network interface to bind to |
| `PYDATAUI_PORT` | `8000` | Port number |
| `PYDATAUI_DEBUG` | `false` | Enable verbose logging |
| `PYDATAUI_SESSION_SECRET` | Auto-generated | Secret key for signing session cookies |
| `PYDATAUI_SESSION_MAX_AGE`| `86400` | Session lifetime in seconds (24 hours) |
| `PYDATAUI_API_PREFIX` | `/api` | Base path for auto-generated REST APIs |
| `PYDATAUI_THEME` | `light` | Default theme: `light` or `dark` |

---

## 8. Production Security Checklist

- [ ] **Secret Key**: Set `PYDATAUI_SESSION_SECRET` to a high-entropy string (e.g. `openssl rand -hex 32`).
- [ ] **HTTPS**: Terminate SSL/TLS at your load balancer or Nginx reverse proxy.
- [ ] **API Keys**: Revoke test keys before promoting to production.
- [ ] **Workers**: Use one worker; shared persistent session/auth storage is not implemented.
- [ ] **CORS**: Configure `cors_origins` in `AppConfig` to restrict cross-origin API calls.

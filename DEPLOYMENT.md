# Deployment Guide (Docker Compose on a Linux VPS)

This repository ships as a 2-service Docker Compose app:

- **frontend** (Nginx serving the React build) on port **80**
- **backend** (FastAPI) on port **8000**

The fastest production deployment is: **VPS + Docker + `docker compose up -d`**.

---

## 0) Prereqs

- A Linux server (Ubuntu 22.04+ recommended)
- A public IP (domain optional)
- Ports opened on the server firewall/security group:
  - **80/tcp** (required)
  - **8000/tcp** (required for the “quick deploy” option below)

> If you want **80/443 only** (best practice), see **Option B**.

---

## 1) Server setup (Ubuntu)

### Install Docker Engine + Compose

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

(Optional) allow your user to run docker without sudo:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

---

## 2) Get the code onto the server

```bash
cd ~
git clone <YOUR_GITHUB_REPO_URL> cricket-team-optimizer
cd cricket-team-optimizer
```

---

## 3) Quick deploy (Expose ports 80 + 8000)

This uses the current `docker-compose.yml` exactly as-is.

```bash
docker compose up --build -d

docker compose ps
```

Expected:
- frontend: **healthy** (port 80)
- backend: **healthy** (port 8000)

### Verify

- Frontend: `http://<SERVER_IP>/`
- Backend: `http://<SERVER_IP>:8000/players`

---

## 4) Option B (Recommended): Single-domain deployment (80/443 only)

Goal:
- Serve the UI at `/`
- Proxy the backend under the same domain at `/api`
- Do **not** expose port 8000 publicly

### B1) Enable API proxy in Nginx

In `frontend/nginx_custom.conf`, uncomment the `/api` location block:

```nginx
location /api {
    proxy_pass http://backend:8000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
}
```

### B2) Make frontend call `/api` instead of `http://localhost:8000`

Set the environment variable at build time:

- In the server shell (or in your deployment pipeline):

```bash
export VITE_API_URL=/api
```

Then rebuild:

```bash
docker compose up --build -d
```

### B3) Close port 8000

- Cloud security group / firewall: remove **8000/tcp** inbound.
- Keep **80** open (and **443** if you add TLS).

---

## 5) HTTPS (Optional)

If you have a domain, the simplest way is to run **Caddy** or a reverse proxy in front of this stack.

Two common approaches:

- **Caddy on host** (recommended for ease): terminates TLS and proxies to the Docker frontend.
- **Nginx on host**: same idea but more manual.

If you tell me your target (EC2 / DigitalOcean / Render / etc) + domain name, I can generate the exact config.

---

## 6) Operations

### View logs

```bash
docker compose logs -f --tail=200
```

### Restart

```bash
docker compose restart
```

### Update to latest `main`

```bash
git pull origin main
docker compose up --build -d
```

### Health check

```bash
docker compose ps
```

---

## 7) Notes

- The backend mounts `./backend/players.csv` into the container as read-only.
- If you switch to Postgres in production, you’ll want to add a `db` service + volume and update the backend configuration accordingly.

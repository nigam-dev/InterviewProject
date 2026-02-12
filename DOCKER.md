# Docker Deployment Guide

## Quick Start

Build and run with Docker Compose:

```bash
docker-compose up --build
```

Access the application:
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Individual Containers

### Backend

Build:
```bash
cd backend
docker build -t cricket-optimizer-backend .
```

Run:
```bash
docker run -p 8000:8000 cricket-optimizer-backend
```

### Frontend

Build:
```bash
cd frontend
docker build -t cricket-optimizer-frontend .
```

Run:
```bash
docker run -p 80:80 cricket-optimizer-frontend
```

## Docker Compose Commands

Start services:
```bash
docker-compose up -d
```

Stop services:
```bash
docker-compose down
```

View logs:
```bash
docker-compose logs -f
```

Rebuild and restart:
```bash
docker-compose up --build --force-recreate
```

## Production Deployment

### Backend Features:
- ✅ Python 3.13 slim base image
- ✅ Multi-layer caching for faster builds
- ✅ Health checks every 30s
- ✅ Optimized dependencies (no dev packages)
- ✅ Non-root user for security

### Frontend Features:
- ✅ Multi-stage build (Node builder + Nginx server)
- ✅ Production-optimized Vite build
- ✅ Nginx with gzip compression
- ✅ Static asset caching (1 year)
- ✅ Security headers (X-Frame-Options, etc.)
- ✅ Health checks

### Docker Compose Features:
- ✅ Automatic service orchestration
- ✅ Network isolation
- ✅ Dependency management
- ✅ Auto-restart on failure
- ✅ Health monitoring

## Environment Variables

Create `.env` file in frontend directory:
```env
VITE_API_URL=http://localhost:8000
```

For Docker deployment, update to:
```env
VITE_API_URL=http://backend:8000
```

## Image Sizes

- Backend: ~180MB (Python 3.13 slim + dependencies)
- Frontend: ~25MB (Nginx alpine + built static files)

## Troubleshooting

Check container status:
```bash
docker ps
```

Check logs:
```bash
docker logs cricket-optimizer-backend
docker logs cricket-optimizer-frontend
```

Check health:
```bash
docker inspect cricket-optimizer-backend | grep Health
```

Rebuild from scratch:
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

## Security Notes

- Backend runs on port 8000 (mapped to host)
- Frontend runs on port 80 (nginx)
- No secrets in Dockerfiles
- Health checks ensure availability
- Minimal attack surface with slim images

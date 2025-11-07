# Stage 2: Docker Deployment 🐳

## 🎯 Educational Purpose

Containerization introduces key DevOps concepts:

- **Reproducibility:** Identical environment for dev/staging/prod
- **Isolation:** No dependency conflicts with host
- **Portability:** "Build once, run anywhere"
- **Orchestration:** Docker Compose for multi-container apps

**Level:** Intermediate
**Time:** 2-3 hours
**Requirements:** Docker Desktop, Docker Compose

## ⚠️ Prerequisites

**IMPORTANT: Train the model before building Docker images.**

```bash
cd backend/
uv sync
uv run python "0. train.py"  # Creates autogluon-iowa-daily/ directory
```

See [backend/README.md](backend/README.md) for details.

## 📐 Architecture

### Single Containers
```
┌────────────────────┐         ┌────────────────────┐
│ Docker Host (macOS/Linux/Windows)                  │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │ Container: iowa_backend                      │ │
│  │ Image: iowa-backend:v1                       │ │
│  │                                              │ │
│  │ FastAPI (port 8003)                          │ │
│  │ + AutoGluon model                            │ │
│  │ + Data files                                 │ │
│  └──────────────────────────────────────────────┘ │
│              ↓ port mapping (-p 8003:8003)        │
│  Host: localhost:8003                             │
└───────────────────────────────────────────────────┘
```

### Docker Compose (Multi-Container)
```
┌─────────────────────────────────────────────────────┐
│ Docker Compose Network: iowa_default                │
│                                                     │
│  ┌──────────────────────┐    ┌─────────────────┐  │
│  │ frontend             │    │ backend         │  │
│  │ (Streamlit)          │    │ (FastAPI)       │  │
│  │ Port: 8501           │────▶ Port: 8003     │  │
│  │                      │    │                 │  │
│  │ API_URL=            │    │ AutoGluon       │  │
│  │  http://backend:8003 │    │ Model           │  │
│  └──────────────────────┘    └─────────────────┘  │
│           ↓                          ↓              │
│  Host: localhost:8501    Host: localhost:8003      │
└─────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

**Fastest way for multi-container deployment:**

```bash
# Build and start all containers
docker compose up --build

# Or in detached mode (background)
docker compose up -d --build

# View logs
docker compose logs -f

# Stop all containers
docker compose down

# Stop and remove volumes
docker compose down -v
```

**Access:**
- Frontend: http://localhost:8501
- Backend: http://localhost:8003
- Backend Docs: http://localhost:8003/docs

### Option 2: Manual Docker Commands

**For education - understanding each step:**

#### Step 1: Build Images
```bash
# Build backend
cd backend/
docker build -t iowa-backend:v1 .

# Build frontend
cd ../frontend/
docker build -t iowa-frontend:v1 .
```

#### Step 2: Create Docker Network
```bash
# Create custom network for container communication
docker network create iowa-network
```

#### Step 3: Run Containers
```bash
# Run backend
docker run -d \
  --name iowa_backend \
  --network iowa-network \
  -p 8003:8003 \
  iowa-backend:v1

# Wait for backend to be ready (check logs)
docker logs -f iowa_backend

# Run frontend (in new terminal)
docker run -d \
  --name iowa_frontend \
  --network iowa-network \
  -p 8501:8501 \
  -e API_URL=http://iowa_backend:8003 \
  iowa-frontend:v1
```

#### Step 4: Test
```bash
# Test backend
curl http://localhost:8003/

# Test frontend (open browser)
open http://localhost:8501
```

#### Step 5: Cleanup
```bash
docker stop iowa_frontend iowa_backend
docker rm iowa_frontend iowa_backend
docker network rm iowa-network
```

## 📂 Project Structure

```
2-docker/
├── README.md                        # This file
├── docker-compose.yml               # Multi-container orchestration
│
├── backend/                         # FastAPI backend
│   ├── Dockerfile                   # Container definition
│   ├── .dockerignore               # Files to exclude from image
│   ├── 0. train.py                 # Training script (run before Docker build)
│   ├── main.py                     # Application code
│   ├── pyproject.toml              # Dependencies (uv)
│   ├── README.md                   # Backend-specific docs
│   ├── data/iowa_sales.csv
│   └── autogluon-iowa-daily/       # Pre-trained model (created by train.py)
│
└── frontend/                        # Streamlit frontend
    ├── Dockerfile                   # Container definition
    ├── .dockerignore               # Files to exclude from image
    ├── app.py                      # Application code
    ├── pyproject.toml              # Dependencies (uv)
    └── README.md                   # Frontend-specific docs
```

## 🔑 Key Concepts

### 1. Container Networking

**Problem:** Containers are isolated. How does frontend communicate with backend?

**Solution 1: Docker Networks**
```bash
docker network create iowa-network
docker run --network iowa-network --name backend iowa-backend
docker run --network iowa-network -e API_URL=http://backend:8003 iowa-frontend
```

**Key Point:** Containers in the same network can find each other by name (`backend`)

**Solution 2: Docker Compose**
```yaml
services:
  backend:
    ...
  frontend:
    environment:
      - API_URL=http://backend:8003  # Service name as hostname!
```

**Docker Compose automatically:**
- Creates network for all services
- Configures DNS (service name → container IP)

### 2. Port Mapping

**Concept:**
```
Host Port → Container Port
  8003   →     8003        (backend)
  8501   →     8501        (frontend)
```

**In practice:**
```bash
# Format: -p <HOST_PORT>:<CONTAINER_PORT>
docker run -p 8003:8003 iowa-backend    # Standard mapping
docker run -p 8080:8003 iowa-backend    # Custom host port
```

**Important:** Inside container network, use container port (8003), not host port

### 3. Environment Variables

**Purpose:** Configuration without code modifications

**Backend:**
```dockerfile
ENV PORT=8003
```

**Frontend:**
```yaml
environment:
  - API_URL=http://backend:8003
```

**Runtime override:**
```bash
docker run -e API_URL=http://different-backend:8003 iowa-frontend
```

### 4. Build Context & .dockerignore

**Problem:** Docker copies everything to build context (slow, large images)

**Solution:** `.dockerignore`
```
.venv/          # Exclude local virtual environment
__pycache__/    # Exclude Python cache
*.pyc           # Exclude compiled Python
.git/           # Exclude git history
```

**Impact:**
- Faster builds (less data transferred)
- Smaller images
- No accidental secrets in image

### 5. Layer Caching

**Dockerfile order matters!**

❌ **Bad (slow):**
```dockerfile
COPY . .                    # Copy everything (changes often)
RUN uv sync                 # Rebuilds on any file change
```

✅ **Good (fast):**
```dockerfile
COPY pyproject.toml ./      # Copy dependencies (changes rarely)
RUN uv sync                 # Cached unless pyproject changes
COPY main.py ./             # Copy code (changes often)
```

**Result:** Dependency layer cached → 10x faster builds!

## 🎓 Learning Objectives

After completing this module, students will be able to:

### Basics
- [ ] Build Docker image with Dockerfile
- [ ] Run container with port mapping
- [ ] Use docker ps, logs, stop, rm
- [ ] Understand the difference between image and container

### Intermediate
- [ ] Create Docker network and connect containers
- [ ] Use Docker Compose for multi-container apps
- [ ] Configure environment variables
- [ ] Debug container networking issues

### Advanced
- [ ] Optimize Dockerfile for fast builds
- [ ] Use `.dockerignore` effectively
- [ ] Understand layer caching
- [ ] Implement health checks
- [ ] Use multi-stage builds

## 🧪 Exercises

### Exercise 1: Custom Network
Create your own Docker network and run containers:
```bash
docker network create my-network
docker run --network my-network --name backend iowa-backend
docker run --network my-network -e API_URL=http://backend:8003 iowa-frontend
```

Verify connectivity:
```bash
docker exec frontend ping backend
```

### Exercise 2: Port Mapping
Run frontend on port 8080 (host) instead of 8501:
```bash
docker run -p 8080:8501 iowa-frontend
```

Access at: http://localhost:8080

### Exercise 3: Image Optimization
Measure image sizes:
```bash
docker images | grep iowa
```

Try to reduce size by:
1. Adding more files to `.dockerignore`
2. Using multi-stage build
3. Cleaning up caches in same RUN command

### Exercise 4: Docker Compose Customization
Modify `docker-compose.yml` to:
1. Add restart policy: `restart: always`
2. Add resource limits:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1'
         memory: 2G
   ```
3. Add volume for logs:
   ```yaml
   volumes:
     - ./logs:/app/logs
   ```

## 🔍 Troubleshooting

### Problem: "Cannot connect to Docker daemon"
**Solution:** Start Docker Desktop
```bash
# macOS
open -a Docker

# Linux
sudo systemctl start docker
```

### Problem: Port already in use
**Error:** `Bind for 0.0.0.0:8003 failed: port is already allocated`

**Solution:**
```bash
# Find process using port
lsof -ti:8003

# Kill process
lsof -ti:8003 | xargs kill -9

# Or use different host port
docker run -p 8080:8003 iowa-backend
```

### Problem: Frontend can't reach backend
**Error:** `Connection refused` in frontend logs

**Debug steps:**
```bash
# 1. Check backend is running
docker ps | grep backend

# 2. Check backend logs
docker logs iowa_backend

# 3. Test backend from host
curl http://localhost:8003/

# 4. Test network connectivity
docker exec frontend ping backend

# 5. Verify API_URL environment variable
docker exec frontend env | grep API_URL
```

### Problem: Image build fails
**Error:** Various build errors

**Solutions:**
```bash
# Clear build cache
docker builder prune

# Build without cache
docker build --no-cache -t iowa-backend .

# Check Dockerfile syntax
docker build --check -t iowa-backend .
```

### Problem: Slow builds
**Solution:**
1. Check `.dockerignore` excludes `.venv/`, `__pycache__/`
2. Verify dependency layer cached:
   ```bash
   docker build -t iowa-backend .    # First build
   # Change only main.py
   docker build -t iowa-backend .    # Should be fast (cached deps)
   ```

## 📊 Performance Benchmarks

| Metric | Value | Notes |
|--------|-------|-------|
| **Backend image size** | ~2.5 GB | Includes PyTorch, AutoGluon |
| **Frontend image size** | ~800 MB | Includes Streamlit, Pandas |
| **First build (backend)** | 3-5 min | Downloads all dependencies |
| **Rebuild (code change)** | 5-10s | Cached dependency layer |
| **Container startup** | 5-10s | Model loading (backend) |
| **Memory (backend)** | ~1.5 GB | AutoGluon models in memory |
| **Memory (frontend)** | ~200 MB | Streamlit |

## 🆚 Local vs Docker Comparison

| Aspect | Local (Stage 1) | Docker (Stage 2) |
|--------|-----------------|------------------|
| **Setup** | `uv sync` in 2 directories | One `docker compose up` |
| **Dependencies** | Must match host Python | Isolated in container |
| **Portability** | "Works on my machine" | Works everywhere |
| **Networking** | localhost only | Container DNS |
| **Isolation** | Shared host filesystem | Separate filesystems |
| **Resource Usage** | Lower | Slightly higher (container overhead) |
| **Debugging** | Easier (direct access) | Requires `docker exec` |
| **Production Ready** | ❌ | ✅ (with orchestration) |

## 🔗 Next Steps

1. **[Stage 3: Cloud Deployment](../3-cloud/README.md)**
   - Push images to GCP Artifact Registry
   - Deploy to Cloud Run
   - Serverless auto-scaling

2. **Advanced Docker**
   - Multi-stage builds
   - Docker secrets
   - Health checks
   - Resource limits

3. **Kubernetes** (Module 10)
   - Pod, Deployment, Service concepts
   - Horizontal auto-scaling
   - Production orchestration

## 💡 Best Practices Summary

### Dockerfile
- ✅ Use specific base image versions (`python:3.11-slim`)
- ✅ Copy dependencies before code (layer caching)
- ✅ Use `.dockerignore`
- ✅ Set `WORKDIR` explicitly
- ✅ Use exec form for CMD (`["cmd", "arg"]`)

### Docker Compose
- ✅ Use `depends_on` with health checks
- ✅ Define networks explicitly (or use default)
- ✅ Use environment variables for configuration
- ✅ Add restart policies

### Operations
- ✅ Tag images with versions (`iowa-backend:v1.2.3`)
- ✅ Clean up unused images/containers
- ✅ Monitor resource usage (`docker stats`)
- ✅ Review logs regularly (`docker logs`)

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Spec](https://docs.docker.com/compose/compose-file/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [uv in Docker](https://docs.astral.sh/uv/guides/integration/docker/)

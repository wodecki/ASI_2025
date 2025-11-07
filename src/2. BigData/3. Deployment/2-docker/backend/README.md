# Backend Docker - Containerization

## 📚 Educational Purpose

Backend API containerization demonstrates:

1. **Reproducible Environments** - Identical environment everywhere (dev/prod)
2. **Dependency Isolation** - No conflicts with system packages
3. **Portable Deployment** - One image works locally, on servers, and in the cloud
4. **Modern Tooling** - uv in Docker for faster builds

## ⚠️ Prerequisites

**IMPORTANT: You must train the model before building the Docker image.**

The Docker image packages a **pre-trained** model. The training happens **outside** the container to keep image builds fast and reproducible.

### Step 0: Train the Model (Required!)

```bash
# Install dependencies locally
uv sync

# Train the model (creates autogluon-iowa-daily/ directory)
uv run python "0. train.py"
```

This creates:
- `autogluon-iowa-daily/` - Trained model artifacts (will be copied into Docker image)
- Training takes ~3 minutes and requires ~4GB RAM

**Why train locally, not in Docker?**
- Faster image builds (model training takes 3+ minutes)
- Smaller images (no training dependencies in production)
- Separation of concerns (train once, deploy many times)

## 🏗️ Docker Architecture

```
┌─────────────────────────────────────┐
│   Docker Image: iowa-backend:latest │
│                                     │
│   Base: python:3.11-slim            │
│   + uv (package manager)            │
│   + Dependencies (from pyproject.toml) │
│   + Application code (main.py)      │
│   + Model artifacts (pre-trained)   │
│   + Data files                       │
│                                     │
│   EXPOSE: 8003                       │
│   CMD: uv run uvicorn main:app      │
└─────────────────────────────────────┘
          ↓ docker run -p 8003:8003
┌─────────────────────────────────────┐
│   Running Container                  │
│   - Isolated filesystem             │
│   - Own network namespace           │
│   - Port 8003 mapped to host        │
└─────────────────────────────────────┘
```

## 🐳 Docker Commands

### Build Image

```bash
# Basic build (make sure model is trained first!)
docker build -t iowa-backend:v1 .

# Build with specific platform (for GCP/AWS)
docker build --platform linux/amd64 -t iowa-backend:v1 .

# Build with no cache (for troubleshooting)
docker build --no-cache -t iowa-backend:v1 .
```

**Expected output:**
```
[+] Building 45.3s (12/12) FINISHED
 => [1/7] FROM python:3.11-slim
 => [2/7] COPY --from=ghcr.io/astral-sh/uv...
 => [3/7] WORKDIR /app
 => [4/7] COPY pyproject.toml ./
 => [5/7] RUN uv sync --no-dev
 => [6/7] COPY main.py ./
 => [7/7] COPY data/ autogluon-iowa-daily/ ./
 => exporting to image
```

### Run Container

```bash
# Run interactively (see logs in terminal)
docker run -p 8003:8003 iowa-backend:v1

# Run in detached mode (background)
docker run -d -p 8003:8003 --name iowa_backend iowa-backend:v1

# Run with custom port
docker run -d -p 8080:8003 --name iowa_backend iowa-backend:v1
# Access at: http://localhost:8080

# Run with environment variable
docker run -d -p 8003:8003 -e PORT=8003 --name iowa_backend iowa-backend:v1
```

### Container Management

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# View logs
docker logs iowa_backend

# Follow logs (live)
docker logs -f iowa_backend

# Stop container
docker stop iowa_backend

# Start stopped container
docker start iowa_backend

# Remove container
docker rm iowa_backend

# Remove container (force, even if running)
docker rm -f iowa_backend
```

### Image Management

```bash
# List images
docker images

# Remove image
docker rmi iowa-backend:v1

# Remove unused images
docker image prune

# Remove all unused images
docker image prune -a
```

### Troubleshooting

```bash
# Enter running container (for debugging)
docker exec -it iowa_backend /bin/bash

# Check container resource usage
docker stats iowa_backend

# Inspect container details
docker inspect iowa_backend

# View container filesystem
docker exec iowa_backend ls -la /app
```

## 📝 Dockerfile Anatomy

### Line-by-Line Explanation

```dockerfile
FROM python:3.11-slim
```
**Educational Note:** Base image selection
- `python:3.11` - Specific Python version (not `latest` - important for reproducibility)
- `-slim` - Smaller image (~130MB vs ~900MB for full Python)
- Trade-off: Slim lacks build tools, but sufficient for our use case

```dockerfile
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
```
**Educational Note:** Multi-stage copy
- Copies `uv` binary from official uv image
- Avoids installing uv from scratch
- Modern alternative to `RUN pip install uv`

```dockerfile
WORKDIR /app
```
**Educational Note:** Working directory
- All subsequent commands run in `/app`
- Creates directory if it doesn't exist
- Standard convention for application code

```dockerfile
COPY pyproject.toml ./
RUN uv sync --no-dev
```
**Educational Note:** Dependency layer caching
- Copy dependencies **before** code
- Docker caches this layer → faster rebuilds when only code changes
- `--no-dev` excludes dev dependencies (pytest, etc.)

```dockerfile
COPY main.py ./
COPY data/ ./data/
COPY autogluon-iowa-daily/ ./autogluon-iowa-daily/
```
**Educational Note:** Application code and artifacts
- Copied **after** dependencies (cache optimization)
- Model artifacts bundled in image (immutable deployment)
- **Requires model to be trained locally first!**

```dockerfile
EXPOSE 8003
```
**Educational Note:** Port documentation
- Documents which port the container listens on
- **Does NOT** actually publish port (that's `-p` flag in `docker run`)
- Metadata for developers and orchestration tools

```dockerfile
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
```
**Educational Note:** Container startup command
- **Exec form** (JSON array) - proper signal handling
- `--host 0.0.0.0` - Listen on all interfaces (required in container)
- `uv run` - Automatically activates virtual environment

## 🎓 Key Concepts

### 1. Layer Caching

**Why order matters:**

❌ **Bad (slow rebuilds):**
```dockerfile
COPY . .                    # Copies everything (code + deps)
RUN uv sync                 # Reinstalls on ANY file change
```

✅ **Good (fast rebuilds):**
```dockerfile
COPY pyproject.toml ./      # Only dependencies
RUN uv sync                 # Cached if pyproject unchanged
COPY main.py ./             # Code changes don't rebuild deps
```

**Result:** 10x faster rebuilds when only code changes!

### 2. Image Size Optimization

| Image | Size | Use Case |
|-------|------|----------|
| `python:3.11` | ~900 MB | Full development environment |
| `python:3.11-slim` | ~130 MB | Production (our choice) |
| `python:3.11-alpine` | ~50 MB | Ultra-minimal (compatibility issues) |

**Trade-offs:**
- Slim: Good balance (smaller, sufficient for most apps)
- Alpine: Smallest, but requires musl libc (not glibc) → can break some packages

### 3. Port Mapping

```bash
docker run -p <HOST_PORT>:<CONTAINER_PORT> image
```

**Examples:**
```bash
# Standard: host 8003 → container 8003
docker run -p 8003:8003 iowa-backend

# Custom: host 8080 → container 8003
docker run -p 8080:8003 iowa-backend
# Access at: http://localhost:8080

# Multiple mappings
docker run -p 8003:8003 -p 9090:9090 iowa-backend
```

### 4. Immutable Deployments

**Container Philosophy:**
- Build once, run anywhere
- Model artifacts **baked into** image
- No runtime dependencies on host filesystem

**Benefits:**
- ✅ Reproducibility (same image everywhere)
- ✅ Rollback (keep old images)
- ✅ Testing (test exact production image)

**Trade-offs:**
- ❌ Larger images (includes model artifacts)
- ❌ Rebuild required for model updates

## 🧪 Testing

### 1. Train Model (if not done yet)
```bash
uv sync
uv run python "0. train.py"
```

### 2. Build and Run
```bash
docker build -t iowa-backend:v1 .
docker run -d -p 8003:8003 --name test_backend iowa-backend:v1
```

### 3. Health Check
```bash
curl http://localhost:8003/
```

Expected:
```json
{
  "status": "running",
  "message": "Iowa Sales Predictor API"
}
```

### 4. Test Prediction
```bash
curl "http://localhost:8003/predict/BLACK%20VELVET"
```

Expected: JSON with 7-day forecast

### 5. View Logs
```bash
docker logs test_backend
```

Expected:
```
INFO: Loading AutoGluon predictor...
INFO: ✓ Predictor loaded successfully
INFO: Uvicorn running on http://0.0.0.0:8003
```

### 6. Cleanup
```bash
docker stop test_backend
docker rm test_backend
```

## 🔍 Troubleshooting

### Problem: Build fails - "autogluon-iowa-daily/ not found"
**Error:** `COPY failed: file not found in build context`

**Solution:** You forgot to train the model!
```bash
uv sync
uv run python "0. train.py"
docker build -t iowa-backend:v1 .
```

### Problem: Container starts but crashes immediately
**Check logs:**
```bash
docker logs <container_id>
```

**Common causes:**
- Model directory missing (forgot to train)
- Data file missing (check data/iowa_sales.csv exists)
- Syntax error in main.py

### Problem: Cannot connect to container
**Error:** `Connection refused`

**Solution:**
1. Check container is running: `docker ps`
2. Check port mapping: `docker port <container_id>`
3. Verify app binds to `0.0.0.0` (not `localhost` or `127.0.0.1`)

### Problem: Build is very slow
**Solution:** Leverage layer caching
1. Don't change pyproject.toml frequently
2. Use `.dockerignore` to exclude unnecessary files
3. Consider multi-stage builds for large dependencies

### Problem: Image is too large
**Check size:**
```bash
docker images iowa-backend
```

**Optimization tips:**
1. Use `-slim` base image (already done)
2. Add `.dockerignore` file (already done)
3. Use multi-stage build (advanced)
4. Remove unnecessary files in same layer:
   ```dockerfile
   RUN uv sync --no-dev && rm -rf /root/.cache
   ```

## 📊 Performance

**Typical values:**

| Metric | Value | Notes |
|--------|-------|-------|
| Image size | ~2.5 GB | Includes AutoGluon + PyTorch |
| Build time (first) | 3-5 min | Downloads all dependencies |
| Build time (cached) | 5-10s | Only code layer rebuilt |
| Container startup | 5-8s | Model loading |
| Memory usage | ~1.5 GB | AutoGluon ensemble models |

## 🔗 Next Steps

1. **Frontend Docker:** Containerize Streamlit app (see ../frontend/)
2. **Docker Compose:** Multi-container orchestration (see ../docker-compose.yml)
3. **Cloud Deployment:** Push to registry and deploy to GCP Cloud Run

## 💡 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [uv in Docker](https://docs.astral.sh/uv/guides/integration/docker/)
- [FastAPI Docker Deployment](https://fastapi.tiangolo.com/deployment/docker/)

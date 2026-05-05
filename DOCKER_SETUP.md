# EyeNed Docker Development Setup

## Built Images (amd64)

Three Docker images have been built for the eyened-develop platform:

### 1. **danielcyrus/eyened-server:latest** (493MB)
- **Base**: Python 3.12-slim
- **Contents**: FastAPI server with all dependencies
- **Ports**: 8000
- **Features**:
  - Multi-stage build for optimized size
  - Gunicorn with uvicorn workers (4 workers default)
  - Health checks enabled
  - Supports environment variables for configuration

### 2. **danielcyrus/eyened-client:latest** (84MB)
- **Base**: Node 24-slim
- **Contents**: Pre-built serve runtime for static assets
- **Ports**: 3000
- **Features**:
  - Minimal footprint with pre-built dist
  - Volume mount for `/app/dist` for flexibility
  - Health checks enabled

### 3. **danielcyrus/eyened-worker:latest** (3.64GB)
- **Base**: PyTorch 2.6.0-cuda11.8
- **Contents**: Background task processing with GPU support
- **Features**:
  - Full ML/image processing stack (retinalysis, albumentations)
  - Configurable Huey workers
  - Resource limits set (2 CPU, 4GB memory max)

## Quick Start

### 1. Build and Push to Docker Hub

```bash
# First, ensure you're logged in
docker login

# Tag and push server image
docker tag danielcyrus/eyened-server:latest danielcyrus/eyened-server:latest
docker push danielcyrus/eyened-server:latest

# Repeat for client and worker
docker push danielcyrus/eyened-client:latest
docker push danielcyrus/eyened-worker:latest
```

### 2. Start Services with Docker Compose

```bash
# Set environment variables from env.txt
export $(cat env.txt | xargs)

# Start all services
docker compose up -d

# Check logs
docker compose logs -f server
docker compose logs -f worker

# Stop services
docker compose down
```

### 3. Access Services

- **API Server**: http://localhost:3875 (or custom API_SERVER_PORT)
- **Client**: http://localhost:3874 (or custom CLIENT_PORT)
- **Adminer (DB)**: http://localhost:3878 (or custom ADMINER_PORT)
- **Health Check**: curl http://localhost:3875/health

## Docker Compose Services

```yaml
- docker-dind: Docker-in-Docker for testing
- server: FastAPI application
- client: Node.js web client
- worker: Background task processor
- db: PostgreSQL 16
- redis: Redis cache/queue
- adminer: Database management UI
```

## Environment Variables (from env.txt)

All variables from `env.txt` are automatically used by `docker-compose.yml`:

- `API_SERVER_PORT`: API server port
- `CLIENT_PORT`: Web client port
- `DATABASE_PORT`: PostgreSQL port
- `REDIS_PORT`: Redis port
- `ADMINER_PORT`: Adminer UI port
- `DATABASE_USER`, `DATABASE_PASSWORD`: DB credentials
- `IMAGES_BASEPATH`, `STORAGE_BASEPATH`, `DATABASE_PATH`: Storage paths
- `USERID`, `GROUPID`: User/group for file permissions

## Network Connectivity

- All services communicate over the `eyened-network` bridge
- External access through mapped ports
- Internal DNS: service name (e.g., `db`, `redis`, `server`)

## Troubleshooting

### Images won't push to Docker Hub
- Check network connectivity: `docker push` is timing out
- Retry with `docker push <image>` or use `docker buildx build --push`
- Alternatively, use Docker Build Cloud

### Server won't start
- Check logs: `docker compose logs server`
- Ensure PostgreSQL is healthy: `docker compose logs db`
- Verify environment variables are set

### Build failures
- **npm install**: Network timeout - use `npm install --fetch-timeout=60000`
- **apt-get**: Mirror issues - use `--fix-missing` flag
- Python packages: Check `/root/.local/bin` PATH inclusion

## Files Generated

1. **docker/Dockerfile.server** - Multi-stage Python build
2. **docker/Dockerfile.client** - Node.js with serve
3. **docker/Dockerfile.worker** - PyTorch with inference stack
4. **docker-compose.yml** - Full stack orchestration
5. **Dockerfile.dind** - Docker-in-Docker for testing

## Next Steps

1. **Push images manually** when network is stable
2. **Build client from source** if needed (npm install issues resolved)
3. **Configure storage paths** to match your QNAP setup
4. **Set resource limits** for worker based on available GPU/CPU
5. **Enable database backups** using PostgreSQL volumes

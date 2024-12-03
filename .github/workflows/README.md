# Python Chat Application with Docker, Kubernetes, and GitHub Actions

A learning project demonstrating modern DevOps practices including containerization, orchestration, and CI/CD pipelines using a real-time chat application built with FastAPI.

## Project Overview

This project serves as a hands-on learning experience for:
- Container orchestration with Kubernetes
- Continuous Integration/Continuous Deployment (CI/CD)
- Container registry management (GitHub Container Registry)
- Real-time web applications with WebSocket
- Infrastructure as Code (IaC)

## Technical Stack

- **Backend**: FastAPI (Python)
- **Container**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions
- **Container Registry**: GitHub Container Registry (GHCR)
- **Protocol**: WebSocket for real-time communication

## Project Structure

```
python-chat-k8s/
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── tests/
│   └── test_server.py
├── Dockerfile
├── requirements.txt
├── server.py
└── deployment.yaml
```

## Key Learning Points

### 1. Docker
- Building custom images
- Dockerfile best practices
- Container management
- Multi-stage builds

### 2. Kubernetes
- Pod deployment
- Service configuration
- Resource management
- Kubernetes manifests

### 3. GitHub Actions
- CI/CD pipeline setup
- Automated testing
- Container image building
- Package registry integration

## Getting Started

1. **Clone the repository**
```bash
git clone https://github.com/jeans-all/python-chat-k8s.git
cd python-chat-k8s
```

2. **Local Development**
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Start the server
python server.py
```

3. **Docker Build**
```bash
docker build -t chat-app .
docker run -p 8000:8000 chat-app
```

4. **Kubernetes Deployment**
```bash
kubectl apply -f deployment.yaml
```

## CI/CD Pipeline

The project includes an automated pipeline that:
1. Runs tests on every push
2. Builds Docker image
3. Pushes to GitHub Container Registry
4. Updates deployment manifests

## Testing

Tests are written using pytest and can be run locally or through CI/CD:
```bash
pytest -v
```

## Container Registry

Images are stored in GitHub Container Registry:
```bash
docker pull ghcr.io/jeans-all/python-chat-k8s:latest
```

## Learning Resources

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)


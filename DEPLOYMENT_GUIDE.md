# LiteLLM MCP Server Deployment Guide

This guide provides a comprehensive overview of deploying the LiteLLM MCP Server, covering deployment options, production best practices, containerization, cloud deployment, monitoring, security, scaling, backup, CI/CD, and environment management.

---

## 1. Deployment Options

### a. **Python Package Deployment**
The LiteLLM MCP Server can be installed and run as a Python package. This is suitable for local development or lightweight deployments.

#### Steps:
1. Install the package:
   ```bash
   pip install lite-llm-mcp
   ```
2. Run the server:
   ```bash
   lite-llm-mcp --config /path/to/config.yaml
   ```

### b. **Containerized Deployment**
Containerizing the server ensures consistency across environments and simplifies deployment.

#### Steps:
1. Build the Docker image:
   ```bash
   docker build -t lite-llm-mcp:latest .
   ```
2. Run the container:
   ```bash
   docker run -d --name lite-llm-mcp -v /path/to/config.yaml:/app/config.yaml lite-llm-mcp:latest
   ```

### c. **Cloud Deployment**
Deploy the server to cloud providers like AWS, GCP, or Azure using container orchestration tools (e.g., Kubernetes).

---

## 2. Production Setup

### Best Practices:
- **Environment Configuration**: Use environment variables for sensitive data and environment-specific settings.
- **Resource Allocation**: Allocate sufficient CPU and memory for optimal performance.
- **Process Management**: Use a process manager like `systemd` or `supervisord` to manage the server.
- **Load Balancing**: Deploy behind a load balancer for high availability.

---

## 3. Docker Deployment

### Dockerfile Example:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py", "--config", "/app/config.yaml"]
```

### Commands:
1. Build the image:
   ```bash
   docker build -t lite-llm-mcp:latest .
   ```
2. Run the container:
   ```bash
   docker run -d --name lite-llm-mcp -v /path/to/config.yaml:/app/config.yaml lite-llm-mcp:latest
   ```

---

## 4. Cloud Deployment

### a. **AWS Deployment**
1. **ECS (Elastic Container Service)**:
   - Push the Docker image to Amazon ECR.
   - Create an ECS cluster and deploy the container.

2. **EC2 Deployment**:
   - Launch an EC2 instance.
   - Install Docker and run the container.

### b. **GCP Deployment**
1. Push the Docker image to Google Container Registry (GCR).
2. Deploy the container using Google Kubernetes Engine (GKE) or Compute Engine.

### c. **Azure Deployment**
1. Push the Docker image to Azure Container Registry (ACR).
2. Deploy the container using Azure Kubernetes Service (AKS) or Azure App Service.

---

## 5. Monitoring and Logging

### Monitoring:
- Use tools like **Prometheus** and **Grafana** to monitor CPU, memory, and custom metrics.
- Integrate with cloud monitoring services (e.g., AWS CloudWatch, GCP Monitoring).

### Logging:
- Use Python's `logging` module to log server activity.
- Redirect logs to a centralized logging system like **ELK Stack** or **Fluentd**.

Example logging configuration:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)
```

---

## 6. Security Configuration

### Best Practices:
- **Environment Variables**: Store sensitive data (e.g., API keys) in environment variables.
- **Firewall Rules**: Restrict access to the server using firewall rules.
- **User Permissions**: Run the server with a non-root user in Docker.
- **Encryption**: Use TLS for secure communication if applicable.

---

## 7. Scaling

### Horizontal Scaling:
- Deploy multiple instances of the server behind a load balancer (e.g., AWS ALB, NGINX).

### Vertical Scaling:
- Increase CPU and memory resources for the server.

### Kubernetes Example:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lite-llm-mcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: lite-llm-mcp
  template:
    metadata:
      labels:
        app: lite-llm-mcp
    spec:
      containers:
      - name: lite-llm-mcp
        image: lite-llm-mcp:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1"
```

---

## 8. Backup and Recovery

### Backup Strategies:
- Backup configuration files and logs regularly.
- Use cloud storage (e.g., S3, GCS) for backups.

### Recovery:
- Restore the configuration and logs from the backup.
- Re-deploy the server using the saved Docker image or package.

---

## 9. CI/CD Pipeline

### Example with GitHub Actions:
```yaml
name: CI/CD Pipeline

on:
  push:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.9

    - name: Install dependencies
      run: pip install -r requirements.txt

    - name: Run tests
      run: pytest

    - name: Build Docker image
      run: docker build -t lite-llm-mcp:latest .

    - name: Push to Docker Hub
      run: |
        echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
        docker tag lite-llm-mcp:latest your-dockerhub-username/lite-llm-mcp:latest
        docker push your-dockerhub-username/lite-llm-mcp:latest
```

---

## 10. Environment Management

### Configuration Files:
Use separate configuration files for each environment (e.g., `config.dev.yaml`, `config.prod.yaml`).

### Environment Variables:
Set environment variables to differentiate environments:
```bash
export ENV=production
```

### Example Code:
```python
import os
import yaml

env = os.getenv("ENV", "development")
config_file = f"config.{env}.yaml"

with open(config_file, "r") as f:
    config = yaml.safe_load(f)

print(f"Running in {env} environment")
```

---

By following this guide, you can deploy, secure, monitor, and scale the LiteLLM MCP Server effectively in various environments. 
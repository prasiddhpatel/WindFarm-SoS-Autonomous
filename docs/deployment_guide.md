# Deployment Guide

## Local full-stack bringup

```bash
cd infrastructure
docker compose -f docker-compose.full.yml up -d --build
```

## ROS 2 workspace build

```bash
cd ros2_ws
bash build.sh
source install/setup.bash
ros2 launch windfarm_bringup full_system.launch.py
```

## Cloud deployment

### Terraform edge server
```bash
cd infrastructure/terraform
terraform init
terraform apply -var="project_id=<your-gcp-project>"
```

### Kubernetes deployment
```bash
kubectl apply -f infrastructure/k8s/api-deployment.yaml
kubectl apply -f infrastructure/k8s/dashboard-deployment.yaml
```

## Operational flow

1. Start the backend stack.
2. Launch ROS 2 full system bringup.
3. Verify `/health` returns status ok.
4. Open dashboard on port 3000.
5. Confirm MQTT telemetry and database ingestion.
6. Execute aerial triage mission, then MRTA-assisted contact confirmation.

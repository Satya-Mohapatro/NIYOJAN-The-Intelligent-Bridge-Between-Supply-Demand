# Deployment Guide (AWS EC2)

## 1. Launch EC2 Instance
- Spin up an **Ubuntu 22.04 LTS** EC2 instance.
- Ensure the instance has enough RAM (at least 4GB recommended for TensorFlow).
- Configure Security Group to allow inbound traffic on ports `80` (HTTP) and `22` (SSH).

## 2. Connect to the Instance
SSH into your instance:
```bash
ssh -i your-key.pem ubuntu@<your-ec2-public-ip>
```

## 3. Run Setup Script
Clone or copy the `deploy/setup_ec2.sh` script to your instance and run it:
```bash
chmod +x deploy/setup_ec2.sh
./deploy/setup_ec2.sh
```
After it completes, run to apply docker group changes:
```bash
newgrp docker
```

## 4. Clone Repository
```bash
git clone <your-repository-url> niyojan
cd niyojan
```

## 5. Configure Environment Variables
Copy the example environment file and fill in your actual values:
```bash
cp .env.example .env
nano .env
```
*(Ensure `VITE_API_BASE=""` remains empty)*

## 6. Build and Run
Start the application using Docker Compose:
```bash
docker-compose build
docker-compose up -d
```

## 7. Access Application
Open your browser and navigate to:
`http://<your-ec2-public-ip>`

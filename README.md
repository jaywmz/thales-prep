# thales-prep

Pre-onboarding SRE project built to prepare for the **SRE CloudOps Engineer** role at Thales, Cybersecurity & Digital Identity Engineering Competency Center. Built across 6 days covering the full SRE stack — infrastructure provisioning, configuration management, containerisation, CI/CD, monitoring, and security hardening.

---

## Architecture Overview

```
git push
   ↓
GitHub Actions (CI/CD)
   ↓
Build Docker image → Trivy security scan → Push to AWS ECR
   ↓
Ansible SSHes into EC2
   ↓
EC2 pulls image from ECR → runs container
   ↓
nginx reverse proxy → HTTPS termination → Flask app on port 8080
   ↓
Datadog agent monitors EC2 + container metrics
```

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Terraform | Infrastructure as Code — provisions all AWS resources |
| Ansible | Configuration management — configures EC2 automatically |
| Docker | Containerises the Flask application |
| GitHub Actions | CI/CD pipeline — automates build, scan, deploy |
| Datadog | Monitoring, dashboards, alerting |
| AWS EC2 | Cloud server running the application |
| AWS ECR | Private Docker image registry |
| AWS S3 | Terraform remote state storage + CloudTrail logs |
| AWS IAM | Least privilege identity and access management |
| AWS Secrets Manager | Secure credential storage |
| AWS CloudTrail | Audit logging of all AWS API calls |
| AWS Elastic IP | Fixed public IP address |
| nginx | Reverse proxy + HTTPS/SSL termination |
| Flask | Lightweight Python web application |

---

## Project Structure

```
thales-prep/
├── terraform/
│   ├── main.tf              # All AWS infrastructure
│   ├── variables.tf         # Variable definitions
│   └── terraform.tfvars     # Variable values (gitignored)
├── ansible/
│   ├── inventory.ini        # EC2 host configuration
│   └── playbook.yml         # Server configuration tasks
├── app/
│   ├── app.py               # Flask application
│   ├── Dockerfile           # Container definition
│   └── requirements.txt     # Python dependencies
└── .github/
    └── workflows/
        └── deploy.yml       # GitHub Actions CI/CD pipeline
```

---

## Infrastructure (Terraform)

All AWS infrastructure is provisioned as code — zero manual console clicks.

**Resources provisioned:**

```
Networking      → VPC, Subnet, Internet Gateway, Route Table
Security        → Security Group (ports 22, 80, 443, 8080)
Compute         → EC2 t3.micro (Ubuntu 22.04)
Networking      → Elastic IP (fixed public IP)
Containers      → ECR repository with scan on push
Storage         → S3 bucket (Terraform state + CloudTrail logs)
Identity        → IAM Role, Policy, Instance Profile (least privilege)
Security        → AWS Secrets Manager (Datadog API key)
Auditing        → CloudTrail (logs all AWS API calls)
```

**To provision:**

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

**To tear down:**

```bash
terraform destroy
```

---

## Configuration Management (Ansible)

Ansible configures the EC2 automatically after Terraform provisions it. No manual SSH required.

**What the playbook does:**

```
1.  Update apt packages
2.  Install Docker dependencies
3.  Add Docker GPG key and repository
4.  Install Docker CE
5.  Start and enable Docker service
6.  Add ubuntu user to docker group
7.  Install Datadog agent (with Docker integration)
8.  Add dd-agent to docker group
9.  Restart Datadog agent
10. Authenticate to AWS ECR
11. Pull Docker image from ECR
12. Remove existing container (clean redeploy)
13. Run Docker container on port 8080
14. Install nginx and openssl
15. Generate self-signed SSL certificate
16. Configure nginx as reverse proxy with HTTPS
17. Enable site and restart nginx
```

**To run manually:**

```bash
cd ansible
ansible-playbook -i inventory.ini playbook.yml
```

---

## Application (Flask + Docker)

A simple Flask web application containerised with Docker. The app itself is intentionally minimal — the focus is the infrastructure and tooling around it.

**Endpoints:**

```
GET /        → Hello Thales page with server hostname and status
GET /health  → Health check endpoint returning JSON
```

**Build and run locally:**

```bash
cd app
docker build -t thales-app .
docker run -d -p 8080:8080 thales-app
```

**Access locally:**

```
http://localhost:8080
http://localhost:8080/health
```

---

## CI/CD Pipeline (GitHub Actions)

Every push to `main` triggers the full automated pipeline.

**Pipeline steps:**

```
1. Checkout code
2. Configure AWS credentials (from GitHub Secrets)
3. Login to Amazon ECR
4. Build Docker image
5. Tag and push image to ECR
6. Run Trivy security scan (CRITICAL + HIGH vulnerabilities)
7. Install Datadog Ansible collection
8. Deploy via Ansible:
   - Install Datadog agent collection
   - Write SSH key from secret to temp file
   - Replace EC2 IP in inventory.ini dynamically
   - Run ansible-playbook with all required env vars
   - Clean up SSH key
```

**GitHub Secrets required:**

```
AWS_ACCESS_KEY_ID       → IAM user access key
AWS_SECRET_ACCESS_KEY   → IAM user secret key
AWS_ACCOUNT_ID          → AWS account number
EC2_HOST                → EC2 Elastic IP address
EC2_SSH_KEY             → SSH private key contents
DD_API_KEY              → Datadog API key
```

---

## Monitoring (Datadog)

Datadog agent installed on EC2 via Ansible with Docker integration enabled.

**Metrics collected:**

```
System          → CPU usage, memory, disk I/O, network in/out
Docker          → container CPU, memory, uptime, restarts
Process         → per-process memory and CPU breakdown
```

**Tags applied:**

```
env:dev
project:thales-prep
owner:wmjay
```

**Alert configured:**

```
Monitor         → High CPU on thales-prep EC2
Metric          → system.cpu.user
Threshold       → alert > 80%, warning > 60%
Evaluation      → average over last 5 minutes
Notification    → email alert
```

---

## Security

| Feature | Implementation |
|---------|---------------|
| IAM least privilege | EC2 role only has ECR pull permissions |
| No hardcoded credentials | All secrets via GitHub Secrets + AWS Secrets Manager |
| HTTPS | Self-signed SSL certificate via nginx |
| HTTP redirect | All port 80 traffic redirected to 443 |
| Audit logging | CloudTrail logs every AWS API call to S3 |
| Container scanning | Trivy scans Docker image on every deploy |
| Key-based SSH | Password SSH disabled, key pair only |

---

## Traffic Flow

```
Browser → https://EC2_IP (port 443)
              ↓
          nginx (SSL termination)
              ↓
          localhost:8080
              ↓
          Docker container
              ↓
          Flask app
              ↓
          Response back to browser
```

HTTP traffic on port 80 is automatically redirected to HTTPS.

---

## Key Concepts Learned

**Server Immutability** — servers are never manually patched. Changes are made by destroying and redeploying from code. Treat servers like cattle, not pets.

**Infrastructure as Code** — all infrastructure defined in Terraform. Reproducible, version controlled, reviewable.

**CI/CD** — every code change automatically built, scanned, and deployed. Zero manual steps after `git push`.

**Least Privilege** — EC2 only has the IAM permissions it actually needs. Nothing more.

**Reverse Proxy** — nginx sits in front of the Flask app handling SSL, HTTP redirects, and forwarding requests.

---

## Daily Build Log

```
Day 1  → WSL2, VS Code, AWS account, IAM, billing alerts, GitHub
Day 2  → Terraform — VPC, EC2, Elastic IP, ECR, SSH keys
Day 3  → Ansible playbook, Docker, Flask app deployed
Day 4  → GitHub Actions CI/CD pipeline, Trivy, ECR integration
Day 5  → Datadog monitoring, dashboards, CPU alert, stress test
Day 6  → IAM roles, Secrets Manager, CloudTrail, nginx HTTPS
Day 7  → Documentation, cleanup
```
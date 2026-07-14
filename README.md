# Cloud-Native E-Commerce Platform

A production-grade, cloud-native e-commerce platform built on AWS to demonstrate 
end-to-end DevOps engineering capabilities across the full toolchain.

## Architecture

Three Python/FastAPI microservices (cart, orders, users) deployed on Amazon EKS 
via GitOps using ArgoCD, with full CI/CD, observability, and security hardening.

## Tech Stack

| Layer | Tools |
|---|---|
| Cloud | AWS (EKS, ECR, VPC, RDS, ElastiCache, GuardDuty) |
| Infrastructure as Code | Terraform (modular, remote state on S3 + DynamoDB) |
| Application | Python, FastAPI, Pytest |
| Containerisation | Docker, Amazon ECR |
| CI/CD | GitHub Actions |
| GitOps | ArgoCD, Argo Rollouts (canary deployments) |
| Observability | Prometheus, Grafana, Loki, OpenTelemetry |
| Security | OPA Gatekeeper, Falco, AWS GuardDuty |

## Project Structure
## CI/CD Pipeline

On every push to `master`:
1. Run pytest with coverage across all 3 services in parallel (matrix strategy)
2. Build Docker images
3. Scan images with Trivy for vulnerabilities
4. Push to Amazon ECR
5. Update image tags in GitOps repo
6. ArgoCD detects changes and syncs to cluster

## GitOps Flow
ArgoCD watches the `gitops/` directory. Any change to Helm chart values 
(including image tags) triggers an automatic sync to the cluster.

## Canary Deployments

Implemented via Argo Rollouts:
- Step 1: 10% traffic to new version → observe for 30s
- Step 2: 50% traffic → observe for 30s  
- Step 3: 100% traffic → rollout complete

Instant rollback available at any step via `kubectl argo rollouts abort`.

## Infrastructure Design Decisions

- **Single NAT Gateway** in dev (cost vs HA tradeoff — prod uses one per AZ)
- **SPOT instances** for EKS nodes (60-70% cost saving for dev workloads)
- **Ephemeral infrastructure** — destroy after each session, rebuild in 15 min
- **Remote state** in S3 with DynamoDB locking (survives infrastructure cycles)
- **force_delete = true** on ECR repos (supports ephemeral workflow)

## Running Locally

```bash
# Bootstrap remote state (once only)
./scripts/bootstrap-state.sh

# Spin up infrastructure
cd terraform && terraform apply -auto-approve

# Configure kubectl
aws eks update-kubeconfig --region us-east-1 --name ecommerce-dev

# Run tests
cd services/users && pytest tests/ -v
cd services/orders && pytest tests/ -v
cd services/cart && pytest tests/ -v

# Tear down (save costs)
cd terraform && terraform destroy -auto-approve
```

## Phases

- ✅ Phase 1 — VPC, ECR, Terraform remote state
- ✅ Phase 2 — FastAPI microservices with pytest
- ✅ Phase 3 — GitHub Actions CI pipeline
- 🔄 Phase 4 — EKS + ArgoCD GitOps + Argo Rollouts
- ⏳ Phase 5 — Prometheus, Grafana, Loki observability
- ⏳ Phase 6 — OPA Gatekeeper, Falco, GuardDuty security

## Author

Nkagisang Matshego — AWS Solutions Architect Associate  
[GitHub](https://github.com/NkagisangCloud) | 
[LinkedIn](https://linkedin.com/in/your-profile)

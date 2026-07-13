terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "ecommerce-tfstate-316777090793"
    key            = "dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "ecommerce-tfstate-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "ecommerce"
      Environment = "dev"
      ManagedBy   = "terraform"
    }
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

module "vpc" {
  source       = "./modules/vpc"
  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
  azs          = slice(data.aws_availability_zones.available.names, 0, 2)
}

module "ecr" {
  source       = "./modules/ecr"
  project_name = var.project_name
  environment  = var.environment
  repositories = ["cart", "orders", "users"]
}
module "eks" {
source = "./modules/eks"
project_name = var.project_name
environment = var.environment
cluster_version = var.eks_cluster_version
vpc_id = module.vpc.vpc_id
private_subnets = module.vpc.private_subnet_ids
node_instance_type = var.eks_node_instance_type
node_desired = var.eks_node_desired
node_min = var.eks_node_min
node_max = var.eks_node_max

depends_on = [module.vpc]
}

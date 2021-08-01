terraform {
  required_version = ">= 0.13"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
    kubernetes = {
      version = "~> 2.3.2"
    }
    helm = {
      version = "1.3.1"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

variable "cluster_name" {
  default = "sfl-etl-cluster"
}

variable "instance_type" {
  # default = "m5.large"
  default = "t2.small"
}

# All these data blocks are Terraform Data Sources for reading information we need from
# AWS. It sets the name of the Data Source to the ID of the EKS K8s cluster to ensure it is unique
data "aws_eks_cluster" "cluster" {
  name = module.eks.cluster_id
}

data "aws_eks_cluster_auth" "cluster" {
  name = module.eks.cluster_id
}


provider "kubernetes" {
  # Don't load the kubeconfig file, because we get cluster info from the
  # aws_eks_cluster Data Source
  # load_config_file       = false
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority.0.data)
  token                  = data.aws_eks_cluster_auth.cluster.token
}

# Data Source for grabbing Availability Zones in the Region we set on the
# AWS Provider
data "aws_availability_zones" "available" {
}

module "vpc" {
  # This pulls a module for creating VPCs from the public Terraform registry
  source  = "terraform-aws-modules/vpc/aws"
  version = "3.2.0"

  name                 = "k8s-${var.cluster_name}-vpc"
  cidr                 = "172.16.0.0/16"
  azs                  = data.aws_availability_zones.available.names
  private_subnets      = ["172.16.1.0/24", "172.16.2.0/24", "172.16.3.0/24"]
  public_subnets       = ["172.16.4.0/24", "172.16.5.0/24", "172.16.6.0/24"]
  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true

  public_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/elb"                    = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"           = "1"
  }
}

module "eks" {
  # This pulls a module for creating AWS EKS clusters from the public Terraform registry
  source  = "terraform-aws-modules/eks/aws"
  version = "12.2.0"

  cluster_name    = "eks-${var.cluster_name}"
  cluster_version = "1.17"
  subnets         = module.vpc.private_subnets

  vpc_id = module.vpc.vpc_id

  node_groups = {
    general-compute = {
      desired_capacity = 2
      max_capacity     = 10
      min_capacity     = 1

      instance_type = var.instance_type
    }
  }

  write_kubeconfig   = true
  config_output_path = "./"

  workers_additional_policies = [aws_iam_policy.worker_policy.arn]
}

resource "aws_iam_policy" "worker_policy" {
  name        = "worker-policy-${var.cluster_name}"
  description = "Worker policy for the ALB Ingress"

  # policy = file("k8s-worker-node-iam-policy.json")
  policy = file("cluster/k8s-worker-node-iam-policy.json")
}

# This instantiates the Terraform provider for Helm, and lets you deploy Helm
# charts using Terraform
provider "helm" {
  kubernetes {
    host                   = data.aws_eks_cluster.cluster.endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority.0.data)
    token                  = data.aws_eks_cluster_auth.cluster.token
    # load_config_file       = false
  }
}

# This deploys an instance of the Ingress Controller Helm Chart that uses an
# AWS Load Balancer as the "engine" for providing ingress to the K8s cluster
# and load balancing across Pods.
resource "helm_release" "ingress" {
  name       = "ingress"
  chart      = "aws-load-balancer-controller"
  repository = "https://aws.github.io/eks-charts"
  version    = "1.2.5"
  namespace  = "kube-system"

  # set {
  #   name  = "autoDiscoverAwsRegion"
  #   value = "true"
  # }
  # set {
  #   name  = "autoDiscoverAwsVpcID"
  #   value = "true"
  # }
  set {
    name  = "clusterName"
    value = var.cluster_name
  }
}

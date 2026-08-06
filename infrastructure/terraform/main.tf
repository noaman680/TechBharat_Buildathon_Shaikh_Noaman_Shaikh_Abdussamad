terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region = var.aws_region
}

module "eks" {
  source          = "./modules/eks"
  cluster_name    = "meetmind-${var.environment}"
  node_count      = var.node_count
}

module "rds" {
  source          = "./modules/rds"
  db_name         = "meetmind"
  instance_class  = var.db_instance_class
}

module "s3" {
  source      = "./modules/s3"
  bucket_name = "meetmind-media-${var.environment}"
}

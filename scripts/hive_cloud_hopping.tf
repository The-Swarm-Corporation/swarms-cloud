provider "aws" {
  region = "us-west-2"
  # Additional configuration such as credentials
}

provider "google" {
  credentials = file("<CREDENTIALS_FILE>.json")
  project     = "<GCP_PROJECT_ID>"
  region      = "us-central1"
  # Additional configuration
}

module "aws_cluster_1" {
  source = "./modules/aws_cluster"
  cluster_name = "cluster-1"
  region       = "us-west-2"
  # Additional variables
}

module "aws_cluster_2" {
  source = "./modules/aws_cluster"
  cluster_name = "cluster-2"
  region       = "eu-central-1"
  # Additional variables
}

module "gcp_cluster_1" {
  source = "./modules/gcp_cluster"
  cluster_name = "cluster-1"
  region       = "us-central1"
  # Additional variables
}

module "gcp_cluster_2" {
  source = "./modules/gcp_cluster"
  cluster_name = "cluster-2"
  region       = "europe-west1"
  # Additional variables
}

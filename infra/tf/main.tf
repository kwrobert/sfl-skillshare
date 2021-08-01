module "dev_cluster" {
  source        = "./cluster"
  cluster_name  = "dev"
  instance_type = "t2.medium"
}

# Uncomment this to deploy another very expensive cluster
# module "production_cluster" {
#   source        = "./cluster"
#   cluster_name  = "production"
#   instance_type = "m5.large"
# }

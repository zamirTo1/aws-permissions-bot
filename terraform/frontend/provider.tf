terraform {
  required_version = "=1.8.2"
  aws = {
    source = "hashicorp/aws"
    version = "5.59.0"
  }
}

provider "aws" {
  region = "us-west-2"
}

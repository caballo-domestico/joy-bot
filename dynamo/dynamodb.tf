terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
    }
  }
}

provider "aws" {
  profile = "default"
  region  = "us-east-1"
}

module "dynamodb_table" {
  source   = "terraform-aws-modules/dynamodb-table/aws"

  name     = "analisi"
  hash_key = "cf"

  attributes = [
    {
      name = "cf"
      type = "S"
    }

  ]

  tags = {
    Terraform   = "true"
    Environment = "staging"
  }
}
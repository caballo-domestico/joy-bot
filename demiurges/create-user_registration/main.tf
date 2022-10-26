terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_dynamodb_table" "users" {
  name           = "Users"
  hash_key       = "email"
  read_capacity  = 5
  write_capacity = 5
  attribute {
    name = "email"
    type = "S"
  }
}
variable "bucket_prescription_name" {
  type        = string
  description = "name of the s3 bucket to store prescriptions"
}

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

resource "aws_dynamodb_table" "prescription_analysis" {
  name           = "Prescription_analysis"
  hash_key       = "id"
  read_capacity  = 5
  write_capacity = 5
  attribute {
    name = "id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "prescriptions" {
  name           = "Prescriptions"
  hash_key       = "id"
  read_capacity  = 5
  write_capacity = 5
  attribute {
    name = "id"
    type = "S"
  }
}

resource "aws_s3_bucket" "prescriptions" {
  count  = var.bucket_prescription_name == "" ? 0 : 1
  bucket = var.bucket_prescription_name

  tags = {
    Name = "prescriptions"
  }
}

resource "aws_dynamodb_table" "users" {
  name           = "Users"
  hash_key       = "phone_num"
  read_capacity  = 5
  write_capacity = 5
  attribute {
    name = "phone_num"
    type = "S"
  }
}

resource "aws_dynamodb_table" "pin" {
  name           = "Pin"
  hash_key       = "phone"
  read_capacity  = 5
  write_capacity = 5
  attribute {
    name = "phone"
    type = "S"
  }
}
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

resource "aws_instance" "frontend" {
  ami                    = "ami-026b57f3c383c2eec"
  instance_type          = "t2.micro"
  key_name               = "prova"
  vpc_security_group_ids = [aws_security_group.example.id]
  tags = {
    Name = "frontend"
  }
}

resource "aws_security_group" "example" {
  ingress {
    from_port   = 22
    to_port     = 22
    cidr_blocks = ["0.0.0.0/0"]
    protocol    = "tcp"
  }
}

module "dynamodb_table" {
  source = "terraform-aws-modules/dynamodb-table/aws"

  name     = "analisi"
  hash_key = "cf"

  attributes = [
    {
      name = "cf"
      type = "S"
    }

  ]

  tags = {
    Name = "user-interface"
  }
}
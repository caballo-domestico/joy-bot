variable "key_name" {
  type        = string
  description = "name of the ssh key pair to use registered in AWS"
  nullable    = false
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

resource "aws_instance" "frontend" {
  ami                    = "ami-026b57f3c383c2eec"
  instance_type          = "t2.small"
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.allow_ssh.id]
  tags = {
    Name = "frontend"
  }
}

resource "aws_security_group" "allow_ssh" {
  name        = "allow_ssh&http"
  description = "Allow ssh e http inbound traffic"

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "allow_ssh&http"
  }
}

output "Retrieve_ip" {
  value = aws_instance.frontend.*.public_ip
}


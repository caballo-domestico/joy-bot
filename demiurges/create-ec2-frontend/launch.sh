#!/usr/bin/env bash

while [ "$1" != "" ]; do
    case $1 in
    --cfg-path)
        shift
        export AWS_CONFIG_FILE="$1"
        ;;
    --cdls-path)
        shift
        export AWS_SHARED_CREDENTIALS_FILE="$1"
        ;;
    -p)
        shift
        export AWS_PROFILE="$1"
        ;;
    *)
        echo "Usage: $0 --cfg-path <path> --cdls-path <path> -p <profile>"
        exit 1
    esac
    shift
done

trap 'echo "\"${BASH_COMMAND}\" command failed with exit code $?."' ERR # who made the mess???
terraform init  # initialize terraform environment if not done before

# starts transaction
set -e
terraform fmt   # makes terraform files more readable
terraform validate # Assures that the terraform files are syntatically correct
terraform apply # Applies the changes
terraform show  # Shows the current state of the infrastructure


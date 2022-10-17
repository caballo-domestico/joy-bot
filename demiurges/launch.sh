#!/usr/bin/env bash

usage="Usage: $0 TERRAFOM_SCRIPT_DIR --cfg-path <path> --cdls-path <path> --ssh-path <path> -p <profile>"

trap 'echo "\"${BASH_COMMAND}\" command failed with exit code $?."' ERR # who made the mess???

if [ $# -lt 1 ]
then
    echo "$usage"
    exit 1
fi

target=$1
shift

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
        echo "$usage"
        exit 1
    esac
    shift
done

# starts transaction
set -e
cd "$target"
terraform init  # initialize terraform environment if not done before
terraform fmt   # makes terraform files more readable
terraform validate # Assures that the terraform files are syntatically correct
terraform apply # Applies the changes
set +e

terraform show  # Shows the current state of the infrastructure


#!/usr/bin/env bash

# This script is used to deploy the application to an AWS ec2 instance

usage="Usage: $0 SSH_KEY_PATH [--skip-terraform]  [--skip-dependencies]"
trap 'echo "\"${BASH_COMMAND}\" command failed with exit code $?."' ERR # who made the mess???

if [ $# -lt 1 ]
then
    echo "$usage"
    exit 1
fi

while [ "$1" != "" ]; do
    case $1 in
    --skip-terraform)
        skipTerraform=true
        ;;
    --skip-dependencies)
        skipDependencies=true
        ;;
    *)
        export SSH_PATH=$1
        ;;
    esac
    shift
done

scriptDir="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
rootDir="$( cd -- "$(dirname "$scriptDir")" >/dev/null 2>&1 ; pwd -P )"
set -e

# prepare infrastructure with terraform
if [ -z "$skipTerraform" ]
then
    echo "$0": deploying infrastructure with terraform
    cd "$rootDir"/demiurges
    ./launch.sh "create-ec2-frontend" "create-microservices-resources" --cfg-path ~/.aws/config --cdls-path ~/.aws/credentials
    terraform -chdir=create-ec2-frontend output -json > "$scriptDir/infrastructure.json"
fi

# compile protobuf and grpc files
echo "$0": compiling protobuf and grpc stubs
make -C "$rootDir"/frontend stubs

# setup ansible hosts file
echo "$0": setting up ansible hosts file
cd "$scriptDir" 
python3 getIp.py

# prepare docker environment and install app with ansible
echo "$0": deploying app to remote host with ansible
export ANSIBLE_HOST_KEY_CHECKING=False
if [ -z "$skipDependencies" ]
then
    playbooks+=("docker.yml")
fi
playbooks+=("deployApp.yml")
ansible-playbook -v -i hosts -K "${playbooks[@]}"

set +e


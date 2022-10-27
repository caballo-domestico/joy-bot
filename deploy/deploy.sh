#!/usr/bin/env bash

# This script is used to deploy the application to AWS
usage="Usage: $0 SSH_KEY_PATH"
trap 'echo "\"${BASH_COMMAND}\" command failed with exit code $?."' ERR # who made the mess???

if [ $# -lt 1 ]
then
    echo "$usage"
    exit 1
fi


scriptDir="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
rootDir="$( cd -- "$(dirname "$scriptDir")" >/dev/null 2>&1 ; pwd -P )"
export SSH_PATH=$1

set -e
cd "$rootDir"/demiurges
./launch.sh create-ec2-frontend --cfg-path ~/.aws/config --cdls-path ~/.aws/credentials
cd create-ec2-frontend || exit 1
terraform output -json > "$scriptDir/infrastructure.json"

cd "$scriptDir" 
#setup ansible hosts file
python3 getIp.py 
#execute ansible file
sudo ansible-playbook -i hosts -K "$rootDir/docker.yml"  # TODO: add a playbook to deploy joy-bot

set +e


#!/usr/bin/env bash

usage="Usage: $0 TERRAFOM_SCRIPT_DIR --cfg-path <path> --cdls-path <path> -p <profile>"

trap 'echo "\"${BASH_COMMAND}\" command failed with exit code $?."' ERR # who made the mess???

if [ $# -lt 1 ]
then
    echo "$usage"
    exit 1
fi

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
        targets+=("$1") 
        ;;
    esac
    shift
done

# starts transaction
set -e

for t in "${targets[@]}"; do
    echo launching terraform with target "$t"
    tf="terraform -chdir=$t"
    $tf init
    $tf fmt   # makes terraform files more readable
    $tf validate # Assures that the terraform files are syntatically correct
    $tf apply
    $tf show  # Shows the changes
done

set +e

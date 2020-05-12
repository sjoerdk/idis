#!/bin/bash

echo "Setting git and docker versions in environment. These can be used by make later"

export GIT_COMMIT_ID=$(git describe --always --dirty)
export GIT_BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD | sed "s/[^[:alnum:]]//g")
export DOCKER_GID=$(getent group docker | cut -d: -f3)

echo GIT_COMMIT_ID=$GIT_COMMIT_ID
echo GIT_BRANCH_NAME=$GIT_BRANCH_NAME
echo DOCKER_GID=$DOCKER_GID

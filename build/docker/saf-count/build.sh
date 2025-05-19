#!/bin/bash

readonly IMAGE_NAME="saf-count"

cd "$(dirname "$0")" || exit

exec docker build -t $IMAGE_NAME .

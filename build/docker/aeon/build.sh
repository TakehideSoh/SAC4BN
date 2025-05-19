#!/bin/bash

readonly IMAGE_NAME="aeon"

cd "$(dirname "$0")" || exit

exec docker build -t $IMAGE_NAME .

#!/bin/bash

readonly IMAGE_NAME="gen-an"

cd "$(dirname "$0")" || exit

exec docker build -t $IMAGE_NAME .

#!/bin/bash

if [[ $# -ne 3 ]]; then
    echo "Usage: $0 HEAP_SIZE STACK_SIZE AN_FILE"
    exit 1
fi

readonly JAR_FILE="/app/saf.jar"
readonly SOLVER="bdd_minisat_all_release"

exec java -Xms"$1" -Xmx"$1" -Xss"$2" -jar $JAR_FILE -k1solver $SOLVER -k 1 "$3"

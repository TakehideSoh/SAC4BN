#!/bin/bash

if [[ $# -ne 3 ]]; then
    echo "Usage: $0 HEAP_SIZE STACK_SIZE INPUT_FILE"
    exit 1
fi

set -x

INPUT_FILE=$(realpath "$3")
readonly INPUT_FILE

readonly BIOLQM_JAR_FILE="/app/target/bioLQM-0.8-SNAPSHOT.jar"
readonly PY_SCRIPT_FILE="/app/modify_an.py"

unset cmd_pid tmp_dir

kill_proc() {
    if [[ -n "${cmd_pid-}" ]]; then
        kill -s TERM "$cmd_pid"
    fi
}

rm_tmp() {
    if [[ -n ${tmp_dir-} ]]; then
        rm -rf "$tmp_dir"
    fi
}

trap 'kill_proc; exit' INT TERM
trap rm_tmp EXIT

tmp_dir=$(mktemp -d)
cd "$tmp_dir" || exit

an_file="$INPUT_FILE.an"

java -Xms"$1" -Xmx"$1" -Xss"$2" -jar $BIOLQM_JAR_FILE "$INPUT_FILE" "$an_file" &
cmd_pid=$!
wait $cmd_pid
exit_status=$?

if [[ $exit_status -eq 0 ]]; then
    ext=${INPUT_FILE##*.}
    case $ext in
    sbml)
        python3.11 $PY_SCRIPT_FILE -a "$an_file" -s "$INPUT_FILE" &
        cmd_pid="$!"
        wait "$cmd_pid"
        ;;
    esac

    chmod --reference="$INPUT_FILE" "$an_file"
    chown --reference="$INPUT_FILE" "$an_file"
fi

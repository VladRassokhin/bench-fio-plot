#!/bin/bash

set -euo pipefail

echo "Checking environment..."
which fio

rm -rf results testfile
mkdir -p results
echo "OK"

echo "Waiting for next full 5 minutes"
fix=300
date
sleep_for=$((fix - $(date +%s) % fix))
echo "Will wait $sleep_for seconds"
sleep ${sleep_for}

echo "Running benchmark..."
./benchmark_script/bench-fio.sh benchmark_script/fio-job-template-file.fio results . testfile 20G
echo "DONE"



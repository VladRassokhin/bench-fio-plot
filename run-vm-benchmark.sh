#!/bin/bash

set -euo pipefail

echo "Checking environment..."
which fio

rm -rf results testfile
mkdir -p results
echo "OK"

echo "Running benchmark..."
./benchmark_script/bench-fio.sh benchmark_script/fio-job-template-file.fio results . testfile 20G
echo "DONE"



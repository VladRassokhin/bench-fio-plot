#!/bin/bash

set -euo pipefail

name="$1"

if [ ! -d "out/$name" ]; then
	echo "Not exists out/$name"
	exit 1
fi

pushd fio_plot
pip3 install -r requirements.txt
popd

plot() {
	echo "Plotting $*"
	run="$1"
	shift
	./fio_plot/fio_plot -i "out/$name" -T "$name" -r "$run" "$@"
}

for run in randread randwrite read write; do
  # 3d plots looks a bit off
	plot $run -L -t iops
	plot $run -L -t lat
	plot $run -L -t bw
	for numjobs in 1 2 4 8 16; do
		plot $run -l -t bw -d 1 2 4 8 16 32 -n $numjobs
		plot $run -g -t bw -d 1 2 4 8 16 32 -n $numjobs
	done
sleep 1
done

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
	metric="$1"
	shift
	./fio_plot/fio_plot -i "out/$name" -T "$name-$metric" -r "$metric" "$@"
}

for metric in randread randwrite read write; do
  # 3d plots looks a bit off
	#plot $metric -L -t iops
	#plot $metric -L -t lat
	for numjobs in 1 2 4 8 16; do
		plot $metric -l -t bw -d 1 2 4 8 16 32 -n $numjobs
		plot $metric -g -t bw -d 1 2 4 8 16 32 -n $numjobs
	done
sleep 1
done

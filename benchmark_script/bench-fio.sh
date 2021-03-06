#!/bin/bash

set -euo pipefail

if [ $# -ne 5 ]
then
	echo "Usage: $0 <JOBFILE> <OUTPUT> <DIRECTORY> <FILE> <SIZE>"
	exit 1
fi

if [ -z ${FIO+x} ]
then
	FIO=fio
fi


export BLOCKSIZE=${BLOCKSIZE:-4k}
export RUNTIME=${RUNTIME:-60}
export ENGINE=${ENGINE:-libaio}
export JOBFILE=$1
export OUTPUT=$2
export DIRECTORY=$3
export FILE=$4
export SIZE=$5

if [ ! $($FIO --version | grep -i fio-3) ]
then
	echo "Fio version 3+ required because fio-plot expects nanosecond precision"
	exit 1
fi

if [ ! -e "$JOBFILE" ]
then
	echo "Fio job file $JOBFILE not found."
	exit 1
fi

if [ ! -e "$OUTPUT" ]
then
	echo "Directory for output $OUTPUT not found, will create"
	mkdir -p "$OUTPUT"
fi

for RW in randread randwrite read write
do
	for IODEPTH in 1 2 4 8 16 32 64
	do
		for NUMJOBS in 1 2 4 8 16 32
		do
			sync
			[[ -w /proc/sys/vm/drop_caches ]] && (echo 3 > /proc/sys/vm/drop_caches || true)
			echo "=== $FILE ============================================"
			echo "Running benchmark $RW with I/O depth of $IODEPTH and numjobs $NUMJOBS"
			export RW
			export IODEPTH
			export NUMJOBS
			$FIO "$JOBFILE" --output-format=json "--output=$OUTPUT/$RW-$IODEPTH-$NUMJOBS.json"
		done
	done
done

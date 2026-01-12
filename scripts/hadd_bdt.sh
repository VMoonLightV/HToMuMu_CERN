#!/bin/bash

channel_US=$1

path=./root_io/tuples/BDT_score/${channel_US}/BFull_SNottH
echo $path

cp ./scripts/hadd_template.sh $path/hadd.sh
cd $path
bash hadd.sh

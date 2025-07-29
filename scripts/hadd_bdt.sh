#!/bin/bash

path=./root_io/tuples/BDT_score/ggH/BFull_SNottH
echo $path

cp ./scripts/hadd_template.sh $path/hadd.sh
cd $path
bash hadd.sh

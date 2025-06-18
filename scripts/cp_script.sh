#!/bin/bash

if [[ $# -ne 2 ]]; then
    echo "Use cp user and data_set_type as arguments"
    exit
fi

CP_USER=$1
DATA_SET_TYPE=$2

# Define source and destination
host="root://cmseos.fnal.gov"
src_path="/store/user/lpchmumu/$CP_USER/analyzer_HiggsMuMu/$DATA_SET_TYPE"
dst_path="/store/user/lpchmumu/$USER/analyzer_HiggsMuMu/$DATA_SET_TYPE"

# List files in the remote source directory
xrdfs "$host" ls "$src_path" | while read -r full_src_file; do
    filename=$(basename "$full_src_file")
    echo $filename
    echo "xrdcp "$host/$full_src_file/SumGenWeight.root" "$host/$dst_path/$filename/SumGenWeight.root""
    xrdcp "$host/$full_src_file/SumGenWeight.root" "$host/$dst_path/$filename/SumGenWeight.root"

done



#!/bin/bash

#######################
# Debugging purposes
#######################
voms-proxy-info --all
ls -l

###############################
# Define input parameters
###############################
input_file=$1
output_folder=$2
era=$3
channel=$4
file_type=$5
cmssw_version=$6

is_data="F"
if [[ $file_type == *"Data"* ]]; then is_data="T"; fi

is_signal="F"
if [[ $file_type == *"signal"* ]]; then is_signal="T"; fi

###############################
# Define exec and setup cmssw
###############################
workDir=`pwd`
executable="CreateTuple"
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=el9_amd64_gcc12
#tar -zxvf cms_setup.tar.gz
scramv1 project CMSSW $cmssw_version

#######################################
# Copy input and exec to cmssw folder
#######################################
cp ${executable} $cmssw_version/src/.
xrdcp root://cmseos.fnal.gov/${input_file} $cmssw_version/src/input_file.root

###########################
# Get cmssw environment
###########################
cd $cmssw_version/src/
eval `scram runtime -sh`

###########################
# Run executable
###########################
echo "Executing Analysis executable:"
echo "./${executable} input_file.root ./ ${era} ${channel} ${is_data} ${is_signal}"
./${executable} input_file.root ./ ${era} ${channel} ${is_data} ${is_signal}

# Copy output to output_folder
ls -l
################################################################
# Copy output file to /eos space -- define in submitter code
################################################################
echo ${output_folder}
xrdcp -f ${channel}_${era}_tuples.root root://cmseos.fnal.gov/${output_folder}
echo "Output file saved in root://cmseos.fnal.gov/${output_folder}${channel}_${era}_tuples.root"
rm ${channel}_${era}_tuples.root

cd -

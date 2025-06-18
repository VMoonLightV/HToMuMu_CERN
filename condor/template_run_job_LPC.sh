#!/bin/bash

#######################
# Debugging purposes
#######################
voms-proxy-info --all
ls -l

###############################
# Define input parameters
###############################
output_name=$1
job_number=$2
is_data=$3
year=$4
output_Directory=$5
cmssw_version=$6

file_type="data"
if [ "$is_data" == "F" ]; then file_type="mc"; fi

###############################
# Define exec and setup cmssw
###############################
workDir=`pwd`
executable="HmmAnalyzer"
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=el9_amd64_gcc12
#tar -zxvf cms_setup.tar.gz
scramv1 project CMSSW $cmssw_version

DATA_FOLDER="$cmssw_version/src/data/"

###########################################
# Copy input list and exec to cmssw folder
###########################################
cp input_list.tgz $cmssw_version/src/
cp ${executable} $cmssw_version/src/.

mkdir -p ${DATA_FOLDER}/Rocco/
cp RoccoR${year}.txt ${DATA_FOLDER}/Rocco/

mkdir -p ${DATA_FOLDER}/btagSF/
cp DeepCSV_94XSF_V3_B_F.csv ${DATA_FOLDER}/btagSF/

mkdir -p ${DATA_FOLDER}/leptonSF/2016/
cp EfficienciesAndSF_*.root ${DATA_FOLDER}/leptonSF/2016/
cp Run*_SF_*.root ${DATA_FOLDER}/leptonSF/2016/

mkdir -p ${DATA_FOLDER}/pileup/
cp Pileup*.root ${DATA_FOLDER}/pileup/
cp RunII_*.root ${DATA_FOLDER}/pileup/

########################################################################
# Copy when running manually (this will lead to unharmed errors in job)
########################################################################
cp data/Rocco/RoccoR${year}.txt ${DATA_FOLDER}/Rocco/
cp data/btagSF/DeepCSV_94XSF_V3_B_F.csv ${DATA_FOLDER}/btagSF/
cp data/leptonSF/2016/*.root ${DATA_FOLDER}/leptonSF/2016/
cp data/pileup/*.root ${DATA_FOLDER}/pileup/

###########################
# Get cmssw environment
###########################
cd $cmssw_version/src/
eval `scram runtime -sh`
tar vxzf input_list.tgz
inputfilelist=input_list_${job_number}.txt

###################################
# Copy input files ahead of time
###################################
mkdir inputs/
for i in `cat $inputfilelist`
do
echo "Copying Input File: " $i
xrdcp $i ./inputs/
done
ls inputs/* > tmp_input_list.txt 

###########################
# Run executable
###########################
echo "Executing Analysis executable:"
echo "./${executable} tmp_input_list.txt ${output_name}_${job_number}.root ${file_type}"
./${executable} tmp_input_list.txt ${output_name}_${job_number}.root ${file_type} ${is_data} ${year}

ls -l
################################################################
# Copy output file to /eos space -- define in submitter code
################################################################
echo ${output_Directory}
xrdfs root://cmseos.fnal.gov mkdir -p /store/group/lpchmumu/${output_Directory}
xrdcp -f ${output_name}_${job_number}.root root://cmseos.fnal.gov//store/group/lpchmumu/${output_Directory}/${output_name}_${job_number}.root
echo "Output file saved in root://cmseos.fnal.gov//store/group/lpchmumu/${output_Directory}/${output_name}_${job_number}.root"
rm ${output_name}_${job_number}.root
rm inputs -rv

cd -

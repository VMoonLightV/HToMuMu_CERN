#!/bin/bash

###############################
# Define input parameters
###############################
dataset_name=$1
FILESDIR=$2
# cmssw_version=$3
cmssw_version="CMSSW_14_0_14"

###############################
# Define exec and setup cmssw
###############################
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=el9_amd64_gcc12
scramv1 project CMSSW $cmssw_version

DATA_FOLDER="$cmssw_version/src/"
mkdir -p ${DATA_FOLDER}
cd $DATA_FOLDER
eval `scram runtime -sh`

mkdir -p rootfiles
NFILES=$(xrdfs root://cmseos.fnal.gov ls -1 /${FILESDIR}|wc -l)
for i in $(seq 1 $NFILES); do
    xrdcp root://cmseos.fnal.gov//${FILESDIR}/HiggsMuMu_$i.root ./rootfiles/
done
ls -lh rootfiles
FILES2MERGE="rootfiles/HiggsMuMu_*.root"

NFILES=$(xrdfs root://cmseos.fnal.gov ls -1 /${FILESDIR}_ext1|wc -l)
if [[ $NFILES -ge 1 ]]; then
    mkdir -p rootfiles_ext1
    for i in $(seq 1 $NFILES); do
        xrdcp root://cmseos.fnal.gov//${FILESDIR}_ext1/HiggsMuMu_$i.root ./rootfiles_ext1/
    done
    ls -lh rootfiles_ext1
    FILES2MERGE="${FILES2MERGE} rootfiles_ext1/HiggsMuMu_*.root"
fi

echo $FILES2MERGE
echo "hadd SumGenWeight.root"
hadd SumGenWeight_${dataset_name}.root ${FILES2MERGE}

echo "Output file saved in root://cmseos.fnal.gov//${FILESDIR}/SumGenWeight.root"
xrdcp -f SumGenWeight_${dataset_name}.root root://cmseos.fnal.gov//${FILESDIR}/SumGenWeight.root
rm SumGenWeight_${dataset_name}.root
rm rootfiles* -rv

# Check file was saved correctly
echo "Checking output file is saved correctly"
xrdfs root://cmseos.fnal.gov ls -lh /${FILESDIR}/SumGenWeight.root

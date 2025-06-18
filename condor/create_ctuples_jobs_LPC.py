#!/usr/bin/python

import os
import sys
sys.path.append('../list')
from listDatasets_Run3 import datasets_info

# analyzer = "HmmAnalyzer"
# analysis = "HiggsMuMu"
# outputfile = analysis

# Skip these datasets
skip_dataset = [
    "DoubleMuon_2022A",
    "DoubleMuon_2022B",
    "Muon0_2023B",
    "Muon1_2023B",
]
skip_pattern = [
    ## Unwanted sets
    "DYJetstoLL",
    "DYto2L-2Jets",
    "4Q",
    "TbarWplustoLNu2Q",
    "2Q-t-channel",
    "WZtoLNu2Q",
    "ZZto2Nu2Q",
    "WWtoLNu2Q",
]

list_datasets = datasets_info.keys()
# # Use in case you want to run over a specific list of datasets!
# list_datasets = [
#     "DY120to200_Summer22",
#     "DY50to120_Summer22",
# ]

# Arguments
if (len(sys.argv) == 1):
    recreate_hadded_file = False
elif (len(sys.argv) > 2) or (sys.argv[1] not in ["T", "F"]):
    print("One argument is required! Add T or F if you want to recreate the hadded file")
    exit()
else:
    recreate_hadded_file = True if (sys.argv[1] == "T") else False

# cmsswReleaseVersion = "CMSSW_10_6_5"
CMSSW_BASE_DIR = os.getenv('CMSSW_BASE')
CONDOR_BASE_DIR = os.getcwd() + "/"
ANALYZER_DIR = CONDOR_BASE_DIR.split("condor/")[0]

cmsswReleaseVersion = CMSSW_BASE_DIR.split("/")[-1]
print("Using CMSSW version " + cmsswReleaseVersion)

# Create script to send all of the jobs directly
send_all_jobs = open(CONDOR_BASE_DIR + "/condor_ctuple_job_sender.sh", "w+")

# Create directory for condor jobs
for dataset_name in list_datasets:
    match_pattern = [True for pattern in skip_pattern if pattern in dataset_name]
    if (dataset_name in skip_dataset) or ("ext1" in dataset_name) or (True in match_pattern):
        continue

    print("\n----- %s -----"%(dataset_name))

    isData, _, era, type_info, _ = datasets_info[dataset_name]
    channel = dataset_name.split("_Summer")[0]

    user = os.getenv('LOGNAME')
    EOS_BASE_DIR = "/store/group/lpchmumu/" + user + "/analyzer_HiggsMuMu/"

    INPUT_FILE = EOS_BASE_DIR + type_info + "/%s/"%(dataset_name) + "SumGenWeight.root"
    if not os.path.exists("/eos/uscms/" + INPUT_FILE):
        print("Merged file does not exist. Skipping!")
        continue

    OUTPUT_DIR = EOS_BASE_DIR + "tuples/"
    os.system("xrdfs root://cmseos.fnal.gov mkdir -p "+ OUTPUT_DIR)
    file_name = channel + "_" + era + "_tuples.root"
    file_copy_name = channel + "_" + era + "_tuples_v1.root"

    hadd_exists = os.path.exists("/eos/uscms/" + OUTPUT_DIR + file_name)
    # print("Exists?", hadd_exists)
    hadd_copy_exists = os.path.exists("/eos/uscms/" + OUTPUT_DIR + file_copy_name)
    if hadd_exists:
        print("Tuples file already exists.")
        if recreate_hadded_file:
            if hadd_copy_exists:
                print("A tuple safe copy already exists! Overwriting.")
                comm = "xrdfs root://cmseos.fnal.gov rm /"
                comm+= OUTPUT_DIR + file_name
                os.system(comm)
            print("Creating new tuple safe copy!")
            comm = "xrdfs root://cmseos.fnal.gov mv /" + OUTPUT_DIR + file_name
            comm+= " /" + OUTPUT_DIR + file_copy_name
            os.system(comm)
        else:
            print("Skipping.")
            continue

    JOB_DIR = CONDOR_BASE_DIR + "ctuples/" + "%s/"%(dataset_name)

    if os.path.exists(JOB_DIR):
        if len(os.listdir(JOB_DIR+"/log/")) != len(os.listdir(JOB_DIR+"/out/")):
            print("Previous job didn't finish well. Try running manually.")
            comm = "./CreateTuple /eos/uscms/" + INPUT_FILE + " "
            comm += "/eos/uscms/" + OUTPUT_DIR + " " + era + " " + channel
            comm += " T" if "Data" in type_info else " F"
            comm += " T" if "signal" in type_info else " F"
            print(" > cd " + JOB_DIR + "; " + comm)
            send_all_jobs.write("cd " + JOB_DIR + "\n")
            send_all_jobs.write(comm + "\n")
            continue

    # Create condor directories
    os.system("mkdir -p " + JOB_DIR)
    os.system("mkdir -p " + JOB_DIR + "/log/")
    os.system("mkdir -p " + JOB_DIR + "/out/")
    os.system("mkdir -p " + JOB_DIR + "/err/")

    ###################################################
    # Copy run script, executable, and required files
    ###################################################
    os.system("cp " + "%s/template_create_tuples_job_LPC.sh"%(CONDOR_BASE_DIR) + " " + "%s/run_job_LPC.sh"%(JOB_DIR))
    os.system("cp " + "%s/bin/CreateTuple"%(ANALYZER_DIR) + " " + JOB_DIR)

    #####################################
    # Create Condor JDL file
    #####################################
    jobfile_JDL = open(JOB_DIR + "/task.jdl", "w+")
    jobfile_JDL.write("Universe  = vanilla" + "\n")
    jobfile_JDL.write("Executable = ./run_job_LPC.sh" + "\n")

    args = INPUT_FILE + " " + OUTPUT_DIR + " " + era + " " + channel + " " + type_info + " " + cmsswReleaseVersion
    jobfile_JDL.write("Arguments = " + args + "\n")

    jobfile_JDL.write("Log = log/job.$(Cluster).$(Process).log" + "\n")
    jobfile_JDL.write("Output = out/job.$(Cluster).$(Process).out" + "\n")
    jobfile_JDL.write("Error = err/job.$(Cluster).$(Process).err" + "\n")
    jobfile_JDL.write("x509userproxy = $ENV(X509_USER_PROXY)" + "\n")

    transfer_files = JOB_DIR + "/run_job_LPC.sh, "
    transfer_files += JOB_DIR + "/CreateTuple, "
    jobfile_JDL.write("transfer_input_files = " + transfer_files + "\n")

    jobfile_JDL.write("should_transfer_files = YES" + "\n")
    jobfile_JDL.write("when_to_transfer_output = ON_EXIT" + "\n\n# Resources request\n")
    jobfile_JDL.write("RequestMemory = 2100 \n\n# Jobs selection\n")

    jobfile_JDL.write("Queue 1\n")
    jobfile_JDL.close()

    print("Send single job with:")
    print(" > cd " + JOB_DIR + "; condor_submit task.jdl")
    send_all_jobs.write("cd " + JOB_DIR + "\n")
    send_all_jobs.write("condor_submit task.jdl" + "\n")

print("\n----- End -----")
print("Run all generated jobs with:")
print(" > bash condor_ctuple_job_sender.sh")
send_all_jobs.close()

#!/usr/bin/python

import os
import datetime
import time
import subprocess
import glob
import sys
from collections import OrderedDict

def all_jobs_were_saved(dataset_name):
    LOG_DIR = "analyzer_HiggsMuMu/" + dataset_name + "/log/"
    OUT_DIR = "analyzer_HiggsMuMu/" + dataset_name + "/out/"
    N_in_log = len(os.listdir(LOG_DIR))
    N_in_out = len(os.listdir(OUT_DIR))

    same_N_files = N_in_log == N_in_out
    if not same_N_files:
        ext = " in _ext1" if "_ext1" in dataset_name else ""
        print(" (!!!) There are " + str(N_in_log - N_in_out) + " missing jobs" + ext)
        print("       There might be missing jobs that ran out of space in farm!")

    return same_N_files

def create_task_to_submit(dataset_name):
    DATASET_DIR = "analyzer_HiggsMuMu/" + dataset_name
    i = 1
    while os.path.exists(DATASET_DIR + "/V%i"%(i)):
        i += 1
    OLD_DATASET_DIR = DATASET_DIR + "/V%i"%(i)
    os.makedirs(OLD_DATASET_DIR)
    os.system("mv " + DATASET_DIR + "/log " + OLD_DATASET_DIR + "/log")
    os.system("mv " + DATASET_DIR + "/out " + OLD_DATASET_DIR + "/out")
    os.system("mv " + DATASET_DIR + "/err " + OLD_DATASET_DIR + "/err")
    os.system("mkdir -p " + DATASET_DIR + "/log/")
    os.system("mkdir -p " + DATASET_DIR + "/out/")
    os.system("mkdir -p " + DATASET_DIR + "/err/")

    list_missing_files = []
    for file in os.listdir(OLD_DATASET_DIR + "/log"):
        file_name = file.split(".log")[0]
        if not os.path.exists(OLD_DATASET_DIR + "/out/%s.out"%(file_name)):
            list_missing_files.append(file_name.split(".")[0])

    print("Missing files")
    print(list_missing_files)
    task_original = open(DATASET_DIR + "/task.jdl", "r")
    task_new = open(DATASET_DIR + "/task_missing_files.jdl", "w")
    for line in task_original:
        if "RequestMemory" in line:
            # Edit this number to 6000-8000 ONLY if failed-runs persist
            line = "RequestMemory = 4000 \n\n# Jobs selection\n"
        elif "Queue I from (" in line:
            break
        task_new.write(line)
    for i, miss in enumerate(list_missing_files):
        newline = "" if i > 0 else "Queue I from ("
        newline += miss.replace("jobR", "")
        task_new.write(newline + "\n")
    task_new.write(")\n")
    task_new.close()
    task_original.close()

    Condor_BASE_DIR = os.getcwd() + "/"
    command_line = "cd " + Condor_BASE_DIR + DATASET_DIR + "; condor_submit task_missing_files.jdl; cd -"
    print(" --> Send job with: " + command_line)

    return command_line

# Arguments
if (len(sys.argv) == 1):
    recreate_hadded_file = False
elif (len(sys.argv) > 2) or (sys.argv[1] not in ["T", "F"]):
    print("One argument is required! Add T or F if you want to recreate the hadded file")
    exit()
else:
    recreate_hadded_file = True if (sys.argv[1] == "T") else False

list_datasets = []
analysis_job_sender = open("condor_job_sender.sh", "r")
for line in analysis_job_sender:
    line = line.strip()
    if line[0:3] != "cd ":
        continue

    setname = line.split("/")[-2]
    if "ext1" in setname:
        continue
    
    list_datasets.append(setname)
analysis_job_sender.close()

# # You can hardcode a list of datasets here if you want!
# list_datasets = [
#     "DY50to120_Summer23",
# ]

os.system("mkdir -p hadd/")

user = os.getenv('LOGNAME')
DIR_eos = "store/group/lpchmumu/" + user + "/analyzer_HiggsMuMu"

analysis_new_job_sender = open("condor_job_sender_missing_files.sh", "w")
manual_hadd = ""
for dataset in list_datasets:
    print("\n----- %s -----"%(dataset))

    FILESDIR = ""
    for dir_type in ["Data", "MC_background", "MC_signal"]:
        if os.path.exists("/eos/uscms/" + DIR_eos + "/%s/%s"%(dir_type, dataset)):
            print("Directory found!")
            FILESDIR = DIR_eos + "/%s/%s"%(dir_type, dataset)
            print("/eos/uscms/" + FILESDIR)
            break
    if not FILESDIR:
        print("No folder found for " + dataset + " :(. Skipping.")
        continue

    os.system("mkdir -p hadd/" + dataset + "/log/")
    os.system("mkdir -p hadd/" + dataset + "/out/")
    os.system("mkdir -p hadd/" + dataset + "/err/")

    hadd_exists = os.path.exists("/eos/uscms/" + FILESDIR + "/SumGenWeight.root")
    hadd_copy_exists = os.path.exists("/eos/uscms/" + FILESDIR + "/SumGenWeight_v1.root")
    if hadd_exists:
        print("Dataset already merged!")
        if recreate_hadded_file:
            if hadd_copy_exists:
                print("A SumGenWeight safe copy already exists! Overwriting.")
                comm = "xrdfs root://cmseos.fnal.gov rm /"
                comm+= FILESDIR + "/SumGenWeight_v1.root "
                os.system(comm)
            print("Creating new SumGenWeight safe copy!")
            comm = "xrdfs root://cmseos.fnal.gov mv /" + FILESDIR + "/SumGenWeight.root"
            comm+= " /" + FILESDIR + "/SumGenWeight_v1.root "
            os.system(comm)
        else:
            print("Skipping.")
            continue

    analysis_ran = os.path.exists("analyzer_HiggsMuMu/" + dataset)
    log_path = "analyzer_HiggsMuMu/" + dataset + "/log"
    if analysis_ran and (len(os.listdir(log_path)) == 0):
        print(" Analyzer /log/ already empty. Send analyzer jobs first!")
        continue
    hadd_ran = os.path.exists("hadd/" + dataset)
    out_path = "hadd/" + dataset + "/out"
    log_path = "hadd/" + dataset + "/log"
    if hadd_ran and (len(os.listdir(out_path)) != len(os.listdir(log_path))):
        print("Hadd job ran and didn't finish. Consider running manually with:")
        command = "cd /eos/uscms/" + FILESDIR + "; "
        command += "hadd SumGenWeight.root HiggsMuMu_*.root"
        if os.path.exists("analyzer_HiggsMuMu/" + dataset + "_ext1"):
            command += " ../" + dataset + "_ext1/HiggsMuMu_*.root"
        print(" > " + command)
        manual_hadd += command + "\n"
        continue

    skip = False
    if not all_jobs_were_saved(dataset):
        new_line = create_task_to_submit(dataset)
        analysis_new_job_sender.write(new_line + "\n")
        skip = True
    if os.path.exists("analyzer_HiggsMuMu/" + dataset + "_ext1"):
        if not all_jobs_were_saved(dataset + "_ext1"):
            new_line = create_task_to_submit(dataset + "_ext1")
            analysis_new_job_sender.write(new_line + "\n")
            skip = True
    if skip:
        continue

    #####################################
    # Create Condor JDL file
    #####################################
    jobfile = open("hadd_%s.jdl"%(dataset), "w+")
    jobfile.write("Universe  = vanilla" + "\n")
    jobfile.write("Executable = ./hadd_datasets.sh" + "\n")
    args = dataset + " " + FILESDIR
    jobfile.write("Arguments = " + args + "\n")

    jobfile.write("Log = hadd/%s/log/jobHadd.$(Cluster).log"%(dataset) + "\n")
    jobfile.write("Output = hadd/%s/out/jobHadd.$(Cluster).out"%(dataset) + "\n")
    jobfile.write("Error = hadd/%s/err/jobHadd.$(Cluster).err"%(dataset) + "\n")
    jobfile.write("x509userproxy = $ENV(X509_USER_PROXY)" + "\n")

    transfer_files = "hadd_datasets.sh, "
    jobfile.write("transfer_input_files = " + transfer_files + "\n")

    jobfile.write("should_transfer_files = YES" + "\n")
    jobfile.write("when_to_transfer_output = ON_EXIT" + "\n\n# Resources request\n")
    jobfile.write("RequestMemory = 4000 \n\n")
    jobfile.write("Queue 1" + "\n")

    jobfile.close()

    print("Submitting job")
    os.system("condor_submit " + "hadd_%s.jdl"%(dataset))

    os.remove("hadd_%s.jdl"%(dataset))

print("\n----- End -----")
print("Run missing-runs jobs with:")
print(" > bash condor_job_sender_missing_files.sh")
analysis_new_job_sender.close()

if manual_hadd:
    manual_hadd_script = open("condor_manual_hadd_sender.sh", "w")
    manual_hadd_script.write(manual_hadd)
    manual_hadd_script.close()
    print("Run remaining hadd sets manually:")
    print(" > bash condor_manual_hadd_sender.sh")

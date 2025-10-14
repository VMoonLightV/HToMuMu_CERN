import subprocess
import pandas as pd
import shutil
import sys
import os

# change to your own path
base_input_directory = "../root_io/tuples/"
output_directory = "../root_io/tuples/EVE_pt_eta/ZCR_75-105_calibrated_all_channel/"
coeff_head = "../plots/EVE_resolution_voigtian_merge_lowPt/"

# Define the path to your C++ executable
cpp_executable = "./bin/EVE_mass_reso_calibration"

# eras = ["2025"]
eras = ["2022", "2022EE", "2023", "2023BPix"]

background_datasets = [
    "DY",
    "TT",
    "DiBoson",
    "EWK",
]
signal_datasets = [
    "ggH",
    "VBF",
    "ttH",
]

input_arguments = []

for era in eras:
    for dataset in signal_datasets:
        input = base_input_directory + dataset + "_" + era + "_tuples.root"
        coeff = coeff_head + f"DY/{era}/BSC_Z_mass_reso_factors.csv"
        input_arguments.append([input, output_directory, era, dataset, "F", coeff])
    for dataset in background_datasets:
        input = base_input_directory + dataset + "_" + era + "_tuples.root"
        coeff = coeff_head + f"DY/{era}/BSC_Z_mass_reso_factors.csv"
        input_arguments.append([input, output_directory, era, dataset, "F", coeff])
    coeff = coeff_head + f"Data/{era}/BSC_Z_mass_reso_factors.csv"
    input = base_input_directory + "Data_" + era + "_tuples.root"
    input_arguments.append([input, output_directory, era, "Data", "T", coeff])


print(input_arguments)

# Loop over each set of input arguments and execute the C++ program
for args in input_arguments:
    # Run the C++ executable with the current arguments
    result = subprocess.run([cpp_executable] + args, capture_output=True, text=True)

    # Print the output and any error messages
    print("Output:", result.stdout)
    print("Errors:", result.stderr)

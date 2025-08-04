import subprocess
import os
import sys
import shutil

# Define the path to your C++ executable
cpp_executable = "./bin/reweighting_Zpt"
base_directory = "/eos/home-y/yulou/Fnal-hmm/hmm-tuples/njet_test/"
coeff_head = "/afs/cern.ch/user/y/yulou/CMSSW_14_0_14/src/A_test/plots/ratio/njet/"

njet_arg = sys.argv[1]
region = sys.argv[2]

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

# List of input arguments
input_arguments = []

if njet_arg == "nobin": njet_group = ["nobin_"]
if njet_arg == "bin": njet_group = ["0","1","2"]

for njet in njet_group:
    # normalization only for DY
    if "ZCR" in region:
        base_input_directory = base_directory + njet + "jet/ZCR_normalization/"
        output_directory = base_directory + njet + "jet/ZCR_self_reweighting/"
    if "SR" in region:
        base_input_directory = base_directory + njet + "jet/SR/"
        output_directory = base_directory + njet + "jet/SR_reweighting/"
    if not os.path.exists(output_directory):
            os.makedirs(output_directory, exist_ok=True)

    for era in eras:
        coeff = coeff_head + njet + "jet_ratio_table_dimuon_pt_ZCR_normalization/polynomial_" + era +"_coefficients.csv"
        input = base_input_directory + "Data_" + era + "_skim.root"
        shutil.copy2(input, output_directory)
        print("copy: ", input)
        #input_arguments.append([input, output_directory, era, "Data", "T", coeff])
        for dataset in signal_datasets:
            input = base_input_directory + dataset + "_" + era + "_skim.root"
            shutil.copy2(input, output_directory)
            print("copy: ", input)
            #input_arguments.append([input, output_directory, era, dataset, "F", coeff])
        for dataset in background_datasets:
            input = base_input_directory + dataset + "_" + era + "_skim.root"
            if dataset != "DY" : 
                shutil.copy2(input, output_directory)
                print("copy: ", input)
            else: input_arguments.append([input, output_directory, era, dataset, "F", coeff])
    
print(input_arguments)

# Loop over each set of input arguments and execute the C++ program
for args in input_arguments:
    # Run the C++ executable with the current arguments
    result = subprocess.run([cpp_executable] + args, capture_output=True, text=True)

    # Print the output and any error messages
    print("Output:", result.stdout)
    print("Errors:", result.stderr)

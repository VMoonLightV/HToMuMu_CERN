import subprocess
import os
import sys
import shutil

# Define the path to your C++ executable
cpp_executable = "./bin/reweighting_Zpt"

region = sys.argv[1]
if "ZCR" in region:
    base_input_directory = "/eos/home-y/yulou/Fnal-hmm/hmm-tuples/njet/nobin_jet/" + region + "_normalization/"
    output_directory = "/eos/home-y/yulou/Fnal-hmm/hmm-tuples/njet/nobin_jet/" + region + "_self_reweighting_6-th/"

if "SR" in region:
    base_input_directory = "/eos/home-y/yulou/Fnal-hmm/hmm-tuples/njet/nobin_jet/" + region + "/"
    output_directory = "/eos/home-y/yulou/Fnal-hmm/hmm-tuples/njet/nobin_jet/" + region + "_reweighting_6-th/"

coeff_head = "/afs/cern.ch/user/y/yulou/CMSSW_14_0_14/src/plots/ratio/njet/" + "nobin_jet_ratio_table_dimuon_pt_ZCR_normalization_eff_piecewise_6-th/polynomial_"


eras = ["2022", "2022EE", "2023", "2023BPix"]


# data_datasets = ["DoubleMuon_2022C", "Muon_2022C", "Muon_2022D", "Muon_2022E", "Muon_2022F", "Muon_2022G"]
# data_datasets = ["DoubleMuon_2022C"]
# data_datasets = ["Muon_2022C"]
# data_datasets = ["Muon_2022D"]
background_datasets = [
    # "TTto2L2Nu",
    # "TTtoLNu2Q",
    # "DY50to120",
    # "DY120to200",
    # "WWto2L2Nu",
    # "WZto2L2Q",
    # "WZto3LNu",
    # "ZZto2L2Nu",
    # "ZZto2L2Q",
    # "ZZto4L",
    # "EWK_2L2J",
    "DY",
    "TT",
    "DiBoson",
    "EWK",
    #"WWW_4F",
]
signal_datasets = [
     "ggH",
     "VBF",
     "ttH",
]

# List of input arguments


input_arguments = []

# normalization only for DY
for era in eras:
    coeff = coeff_head + era +"_coefficients.csv"
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

import subprocess
import sys

# change to your own path
base_input_directory = "/eos/home-y/yulou/Fnal-hmm/hmm-tuples/"
output_directory = "/eos/home-y/yulou/Fnal-hmm/hmm-tuples/njet_test/"

# Define the path to your C++ executable
cpp_executable = "./bin/Eff_on_split_tuple"
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

input_arguments = []

if njet_arg == "nobin": njet_group = ["nobin_"]
if njet_arg == "bin": njet_group = ["0","1","2"]

for njet in njet_group:
    for era in eras:
        input = base_input_directory + "Data_" + era + "_tuples.root"
        input_arguments.append([input, output_directory, era, "Data", "T", njet, region])
        for dataset in signal_datasets:
            input = base_input_directory + dataset + "_" + era + "_tuples.root"
            input_arguments.append([input, output_directory, era, dataset, "F", njet, region])
        for dataset in background_datasets:
            input = base_input_directory + dataset + "_" + era + "_tuples.root"
            input_arguments.append([input, output_directory, era, dataset, "F", njet, region])


print(input_arguments)

# Loop over each set of input arguments and execute the C++ program
for args in input_arguments:
    # Run the C++ executable with the current arguments
    result = subprocess.run([cpp_executable] + args, capture_output=True, text=True)

    # Print the output and any error messages
    print("Output:", result.stdout)
    print("Errors:", result.stderr)

import subprocess
import sys


# Define the path to your C++ executable
cpp_executable = "./bin/Eff_on_tuple"
region = sys.argv[1]

base_input_directory = "/eos/home-y/yulou/Fnal-hmm/hmm-tuples/"
output_directory = "/eos/home-y/yulou/Fnal-hmm/hmm-tuples/njet/nobin_jet/"


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
    input = base_input_directory + "Data_" + era + "_tuples.root"
    input_arguments.append([input, output_directory, era, "Data", "T", region])
    for dataset in signal_datasets:
        input = base_input_directory + dataset + "_" + era + "_tuples.root"
        input_arguments.append([input, output_directory, era, dataset, "F", region])
    for dataset in background_datasets:
        input = base_input_directory + dataset + "_" + era + "_tuples.root"
        input_arguments.append([input, output_directory, era, dataset, "F", region])
    
print(input_arguments)

# Loop over each set of input arguments and execute the C++ program
for args in input_arguments:
    # Run the C++ executable with the current arguments
    result = subprocess.run([cpp_executable] + args, capture_output=True, text=True)

    # Print the output and any error messages
    print("Output:", result.stdout)
    print("Errors:", result.stderr)

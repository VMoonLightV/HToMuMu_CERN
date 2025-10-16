import subprocess
import pandas as pd
import shutil
import sys
import os

# change to your own path
base_input_directory = "./root_io/tuples/"
base_output_directory = "./root_io/tuples/"

# Define the path to your C++ executable
cpp_executable = "./bin/normalization"

njet_arg = sys.argv[1]
count_file = sys.argv[2]

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

df = pd.read_csv(count_file)
variable = 'diMuon_bsConstrainedMass'

if njet_arg == "nobin": njet_group = ["nobin_"]
if njet_arg == "bin": njet_group = ["0","1","2"]

# List of input arguments
input_arguments = []

# normalization only for DY
for njet in njet_group:
    output_directory = base_output_directory + njet + "jet/ZCR_normalization/"
    if not os.path.exists(output_directory):
            os.makedirs(output_directory, exist_ok=True)
    for era in eras:
        input = base_input_directory + njet +"jet/ZCR/" + "Data_" + era + "_skim.root"
        #input_arguments.append([input, output_directory, era, "Data", "T", 
                                #str(df[(df['Era'] == era) & (df['Variable'] == variable)]['DY_factor'].values[0])])
        shutil.copy2(input, output_directory)
        print("copy: ", input)
        for dataset in signal_datasets:
            input = base_input_directory + njet +"jet/ZCR/" + dataset + "_" + era + "_skim.root"
            shutil.copy2(input, output_directory)
            print("copy: ", input)
            #input_arguments.append([input, output_directory, era, dataset, "F", 
                                #str(df[(df['Era'] == era) & (df['Variable'] == variable)]['DY_factor'].values[0])])
        for dataset in background_datasets:
            input = base_input_directory + njet +"jet/ZCR/" + dataset + "_" + era + "_skim.root"
            if dataset != "DY" : 
                shutil.copy2(input, output_directory)
                print("copy: ", input)
            else: input_arguments.append([input, output_directory, era, dataset, "F", 
                                str(df[(df['Era'] == era) & (df['Variable'] == variable) & (df['Njet'] == njet)]['DY_factor'].values[0])])
        
print(input_arguments)

# Loop over each set of input arguments and execute the C++ program
for args in input_arguments:
    # Run the C++ executable with the current arguments
    result = subprocess.run([cpp_executable] + args, capture_output=True, text=True)

    # Print the output and any error messages
    print("Output:", result.stdout)
    print("Errors:", result.stderr)

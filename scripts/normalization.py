import subprocess
import pandas as pd
import shutil



# Define the path to your C++ executable
cpp_executable = "./bin/normalization"

# base_input_directory = "/eos/uscms/store/user/csanmart/analyzer_HiggsMuMu/"
base_input_directory = "/eos/home-y/yulou/Fnal-hmm/hmm-tuples/njet/nobin_jet/ZCR_eff/"
output_directory = "/eos/home-y/yulou/Fnal-hmm/hmm-tuples/njet/nobin_jet/ZCR_eff_normalization/"
count_file = "/afs/cern.ch/user/y/yulou/CMSSW_14_0_14/src/HToMuMu/scripts/event_counts_ZCR_eff_inclusive.csv"

eras = ["2022EE", "2022", "2023", "2023BPix"]


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

df = pd.read_csv(count_file)
variable = 'diMuon_mass'
# List of input arguments
input_arguments = []

# normalization only for DY
for era in eras:
    input = base_input_directory + "Data_" + era + "_skim.root"
    #input_arguments.append([input, output_directory, era, "Data", "T", 
                            #str(df[(df['Era'] == era) & (df['Variable'] == variable)]['DY_factor'].values[0])])
    shutil.copy2(input, output_directory)
    print("copy: ", input)
    for dataset in signal_datasets:
        input = base_input_directory + dataset + "_" + era + "_skim.root"
        shutil.copy2(input, output_directory)
        print("copy: ", input)
        #input_arguments.append([input, output_directory, era, dataset, "F", 
                            #str(df[(df['Era'] == era) & (df['Variable'] == variable)]['DY_factor'].values[0])])
    for dataset in background_datasets:
        input = base_input_directory + dataset + "_" + era + "_skim.root"
        if dataset != "DY" : 
            shutil.copy2(input, output_directory)
            print("copy: ", input)
        else: input_arguments.append([input, output_directory, era, dataset, "F", 
                            str(df[(df['Era'] == era) & (df['Variable'] == variable)]['DY_factor'].values[0])])
    
print(input_arguments)

# Loop over each set of input arguments and execute the C++ program
for args in input_arguments:
    # Run the C++ executable with the current arguments
    result = subprocess.run([cpp_executable] + args, capture_output=True, text=True)

    # Print the output and any error messages
    print("Output:", result.stdout)
    print("Errors:", result.stderr)

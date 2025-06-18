import subprocess
import os

# Define the path to your C++ executable
cpp_executable = "./bin/CreateTuple"
base_input_directory = "/eos/uscms/store/user/lpchmumu/mbarrial/analyzer_HiggsMuMu/"
output_directory = "/eos/uscms/store/user/lpchmumu/mbarrial/analyzer_HiggsMuMu/tuples/"
os.makedirs(output_directory, exist_ok=True)

# eras = ["2022", "2022EE"]
# eras = ["2022"]
# eras = ["2022EE"]
# eras = ["2023", "2023BPix"]
eras = ["2023BPix"]


data_datasets = [
    ## 2022
     "DoubleMuon_2022C",
     "Muon_2022C",
    # "Muon_2022D",
    ## 2023E
    # "Muon_2022E",
    # "Muon_2022F",
    # "Muon_2022G",
    ## 2023
    # "Muon0_2023B",
    # "Muon1_2023B",
    # ## 2023
    # "Muon0_2023C_v1",
    # "Muon0_2023C_v2",
    # "Muon0_2023C_v3",
    # "Muon0_2023C_v4",
    # "Muon1_2023C_v1",
    # "Muon1_2023C_v2",
    # "Muon1_2023C_v3",
    # "Muon1_2023C_v4",
    # ## 2023Bpix
    # "Muon0_2023D_v1",
    # "Muon0_2023D_v2",
    # "Muon1_2023D_v1",
    # "Muon1_2023D_v2",
]
background_datasets = [
    "TTto2L2Nu",
    "TTtoLNu2Q",
    "DY50to120",
    "DY120to200",
    "WWto2L2Nu",
    "WZto2L2Q",
    "WZto3LNu",
    "ZZto2L2Nu",
    "ZZto2L2Q",
    "ZZto4L",
    "EWK_2L2J",
    # "WWW_4F",
    # "DYto2L-2Jets",
]
signal_datasets = [
 #   "ggH",
 #   "VBF",
 #   "ttH",
]

# List of input arguments
input_arguments = []

# ./bin/CreateHistograms /eos/uscms/store/user/csanmart/analyzer_HiggsMuMu/MC_background/TTto2L2Nu_Summer22/SumGenWeight.root ZZto4Lhist.root 2022 ZZto4L F
for dataset in data_datasets:
    input = base_input_directory + "Data/" + dataset + "/SumGenWeight.root"
    input_arguments.append([input, output_directory, "2022", dataset, "T", "F"])

for era in eras:
    dataset_extra = ""
    if era == "2022":
        dataset_extra = "_Summer22"
    elif era == "2022EE":
        dataset_extra = "_Summer22EE"
    if era == "2023":
        dataset_extra = "_Summer23"
    elif era == "2023BPix":
        dataset_extra = "_Summer23BPix"
    for dataset in signal_datasets:
        input = (
            base_input_directory
            + "MC_signal/"
            + dataset
            + dataset_extra
            + "/SumGenWeight.root"
        )
        input_arguments.append([input, output_directory, era, dataset, "F", "T"])
    for dataset in background_datasets:
        input = (
            base_input_directory
            + "MC_background/"
            + dataset
            + dataset_extra
            + "/SumGenWeight.root"
        )
        input_arguments.append([input, output_directory, era, dataset, "F", "F"])
print(input_arguments)

# Loop over each set of input arguments and execute the C++ program
for args in input_arguments:
    # Run the C++ executable with the current arguments
    result = subprocess.run([cpp_executable] + args, capture_output=True, text=True)

    # Print the output and any error messages
    print("Output:", result.stdout)
    print("Errors:", result.stderr)

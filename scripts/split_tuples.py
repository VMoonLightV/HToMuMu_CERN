import os
from sys import argv
import uproot
import numpy as np

def get_output_file_name(data_type, path):
    return os.path.join(
        path,
        {
            "data": "allData_combined.root",
            "signal": "output_signal_M125_13TeV_cats_pythia8.root",
        }[data_type],
    )


def get_input_file_name(data_type, path):
    return os.path.join(
        path,
        {"data": "data_Combined.root", "signal": "signal_2023BPix.root"}[data_type],
    )


def get_tree_name(data_type, channel, category_name):
    return {
        "data": f"Data_13TeV_{category_name}",
        "signal": f"{channel.lower()}_125_13TeV_{category_name}",
    }[data_type]


def split_tuples_by_category(
    data_type, channel, output_file_name, input_file_name, branching_ratio, bdt_cuts, use_bsConstrain,
):

    with uproot.recreate(output_file_name) as file_output:
        branches = {}
        selected_branches = [
            "pileup_weight",
            "diMuon_mass",
            "diMuon_bsConstrainedMass",
            f"BDT_{channel}",
            f"is_{channel}_category",
            "weight_no_lumi",
        ]
        print(f"[Info] Opening input file: {input_file_name}")
        branches = uproot.open(input_file_name)["tree_output"].arrays(
            selected_branches, library="np"
        )
        # Changing the weight from gen_weight*pu*br*1000/SumGenweight to gen_weight/SumGenweight
        branches["weight"] = branches["weight_no_lumi"] / (
            1000 * branching_ratio * branches["pileup_weight"]
        )
        # Renameing the mass variable to use the hgg fits code
        if use_bsConstrain:
            branches["CMS_hgg_mass"] = branches["diMuon_bsConstrainedMass"]
        else:
            print("we here right")
            branches["CMS_hgg_mass"] = branches["diMuon_mass"]
        for category in range(len(bdt_cuts[channel]) - 1):

            cuts = []
            selected_events = {}
            print(f"[Info] Inital events: {len(branches['diMuon_mass'])}")
            print(category)

            cuts = (
                (branches["BDT_" + channel] > bdt_cuts[channel][category])
                & (branches["BDT_" + channel] < bdt_cuts[channel][category + 1])
                & (branches["is_" + channel + "_category"] == 1)
                & (branches["CMS_hgg_mass"] < 180)
                & (branches["CMS_hgg_mass"] > 100)
            )

            selected_events = {name: array[cuts] for name, array in branches.items()}

            print(f"[Info] Final events: {len(branches['diMuon_mass'][cuts])}")

            category_name = channel + "cat" + str(len(bdt_cuts[channel]) - category - 1)

            category_name = f"{channel}cat{len(bdt_cuts[channel]) - category - 1}"
            tree_name = get_tree_name(data_type, channel, category_name)

            file_output[tree_name] = selected_events

    print(f"[Done] Created: {output_file_name}")


if __name__ == "__main__":
    if len(argv) != 3:
        print("[Error] python script.py <data_type: data|signal> <channel: ggH|VBF>")

    data_type = argv[1]
    channel = argv[2]
    branching_ratio = 2.176e-4
    use_bsConstrain = True

    if data_type not in ["data", "signal"]:
        print("[Error]: use data or signal for data_type")
        exit()
    if channel not in ["ggH", "VBF"]:
        print("[Error]: use ggH or VBF for production channel")
        exit()

    print(f"[Config] Using data_type = {data_type}")
    print(f"[Config] Using channel   = {channel}")
    print(f"[Config] Branching Ratio = {branching_ratio}")
    print(f"[Config] Use bsConstrain = {use_bsConstrain}")

    out_path = f"/eos/home-y/yulou/Fnal-hmm/root_io/tuples/split_tuples/{channel}"
    input_path = f"/eos/home-y/yulou/Fnal-hmm/root_io/tuples/BDT_score/{channel}/BFull_SNottH/"
    os.makedirs(out_path, exist_ok=True)
    if use_bsConstrain:
        #bdt_cuts = {
        #    "ggH": [0.0, 0.20969230769230757, 0.44615384615384546, 1.0],
        #    "VBF": [0.0, 0.44603999999999994, 0.7559999999999996, 0.9450000000000007, 1.0], 
        #}
        bdt_cuts = {"ggH": [0.0, 0.19815384615384574, 0.4307692307692301, 1.0], "VBF": [0.0, 0.4822335000000003, 0.7654499999999995, 0.9450000000000007, 1.0]}
        print("here pls")
    else:
        #bdt_cuts = {
            #"ggH": [0.0, 0.18615384615384592, 0.42307692307692246, 1.0],
#            "ggH": [0.0, 0.19184615384615372, 0.44615384615384546, 1.0],
       #     "VBF": [0.0, 0.3448846153846141, 0.7038461538461517, 0.938461538461536, 1.0],
            #"VBF" :[0.0, 0.3614625000000003, 0.7087499999999998, 0.9450000000000007, 1.0],

       # }
        bdt_cuts = {"ggH" : [0.0, 0.18615384615384592, 0.42307692307692246, 1.0], "VBF": [0.0, 0.41277600000000014, 0.7370999999999996, 0.9450000000000007, 1.0]}

    input_file_name = get_input_file_name(data_type, input_path)
    output_file_name = get_output_file_name(data_type, out_path)
    split_tuples_by_category(
        data_type, channel, output_file_name, input_file_name, branching_ratio, 
        bdt_cuts, use_bsConstrain
    )
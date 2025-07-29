import os
from sys import argv
import ROOT
import uproot
import numpy as np

data_type = "signal"
channel = "ggH"

out_path = "../../../split_tuples/" + channel + "/"
input_path = "./root_io/tuples/BDT_score/" + channel + "/BFull_SNottH/"
path = "./"
os.makedirs(out_path, exist_ok=True)
bdt_cuts = {"ggH" : [0.0, 0.058, 0.138, 1.0], "VBF": [0.0, 0.058, 0.138, 1.0]}
branching_ratio = 2.176e-4
print("[Info]: branching ratio =", branching_ratio)


output_file_name = ""
# Defining the output file name
if data_type == "data":
    output_file_name = "allData_combined.root"
    print("[Info]: using %s as data_type"%(data_type))
elif data_type == "signal":
    output_file_name = "output_signal_M125_13TeV_cats_pythia8.root"
    print("[Info]: using %s as data_type"%(data_type))
else:
    print("[Error]: use data or signal for data_type")

with uproot.recreate(out_path + output_file_name) as file_output:
    
    branches = {}
    # Generiting one tree for each category
    for category in range(len(bdt_cuts[channel]) - 1):

        selected_branches = ["pileup_weight", "diMuon_mass" , "BDT_" + channel, "is_" + channel + "_category", "weight_no_lumi"]

        # Defining the input file name
        if data_type == "data":
            file_name = input_path + "data_Combined.root"
        elif data_type == "signal":
            file_name = input_path + "signal_2023BPix.root"

        branches = uproot.open(path + file_name)["tree_output"].arrays(
            selected_branches, library="np"
        )

        print("inital events: ", len(branches["diMuon_mass"]))
        
        # Apply the category codes
        cut_expression = (
            (branches["BDT_" + channel] > bdt_cuts[channel][category])
            & (branches["BDT_" + channel] < bdt_cuts[channel][category + 1])
            & (branches["is_" + channel + "_category"] == 1)
        )


        # Changing the weight from gen_weight*br*1000/SumGenweight to gen_weight/SumGenweight
        branches["weight"] = branches["weight_no_lumi"]/(1000*branching_ratio)  
        branches["weight"] = branches["weight"]/branches["pileup_weight"]
        # Renameing the mass variable to use the hgg fits code
        branches["CMS_hgg_mass"] = branches["diMuon_mass"]

        print("weight:  ",branches["weight"] )
        print("weight no lumi: ",branches["weight_no_lumi"] )
        
        selected_events = {
            name: array[cut_expression] for name, array in branches.items()
        }
        
        total = 0 
        for a in selected_events["weight"]:
            total = total + a
        print("Sum of the weights:", total)
        print(cut_expression)
        
        print("Final events: ", len(selected_events["diMuon_mass"]))
        
        if data_type == "data":
            tree_name = "%s_%s_%s"%("Data","13TeV","cat" + str(len(bdt_cuts[channel]) - category))
        elif data_type == "signal":
            tree_name = "%s_%s_%s_%s"%(channel.lower(),"125","13TeV","cat" + str(category))

        

        file_output[tree_name] = selected_events

print(out_path + output_file_name + " has been created.")

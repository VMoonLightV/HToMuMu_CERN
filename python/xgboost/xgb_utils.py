import sys
import matplotlib
import os

import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

# import math
import pickle as pickle
import ROOT as root
import uproot as uproot

root.gROOT.Reset()
matplotlib.use("Agg")
use_skim = False

def copy_and_skim_tree(tuple_path, tuple_name, BDT_path, BDT_name, channel_US):

    original_file = root.TFile.Open(tuple_path + tuple_name)
    original_tree = original_file.Get("tree_output")
    cuts = "diMuon_mass > 100 && diMuon_mass < 180 && is_" + channel_US + "_category == 1"
    skim_file = root.TFile.Open(BDT_path + BDT_name, "RECREATE")
    skim_tree = original_tree.CopyTree(cuts)
    skim_tree.Write("tree_output")
    skim_file.Close()
    original_file.Close()

def append_BDT_score(file_type, channel_US, era, model_era, signal_subset, background_subset, variables, mean_map, std_map, variable_standatization, use_skim=False):

    subset_title = "B" + background_subset + "_S" + signal_subset
    tuple_subset = ""
    if file_type == "background" or file_type == "bkg":
        tuple_subset = background_subset
    elif file_type == "signal":
        tuple_subset = signal_subset

    if not use_skim:
        tuple_path = "../../root_io/tuples/"
        tuple_name = file_type + "_" + era + "_tuples.root"
        BDT_path = tuple_path + "BDT_score/" + channel_US + "/" + subset_title + "/"
        BDT_name = file_type + "_" + era + "_" + subset_title + ".root"
    else:
        tuple_path = "../../root_io/skim/" + channel_US + "/"
        tuple_name = file_type + "_" + era + "_skim_" + tuple_subset + ".root"
        BDT_path = "../../root_io/skim/BDT_score/" + channel_US + "/"
        BDT_name = file_type + "_" + era + "_skim_" + subset_title + ".root"

    os.system("mkdir -p " + BDT_path)
    print("File name: ", BDT_name)

    ## copy just useful events
    copy_and_skim_tree(tuple_path, tuple_name, BDT_path, BDT_name, channel_US)

    file_name = BDT_path + BDT_name
    File = root.TFile(file_name, "update")
    Tree = File.Get("tree_output")

    model_name = channel_US + "_" + model_era + "_" + subset_title
    model_file = "./models/model_" + model_name + ".pkl"

    with uproot.open(file_name) as file:
        df = pd.DataFrame(
            file["tree_output"].arrays([row[0] for row in variables], library="np"),
        )

    x_test = df.values
    y_test = np.zeros(len(df))
    if variable_standatization:
        for i, var in enumerate(variables):
            print("standarizing : ", var[0])
            print("Iterator : ", i)
            null_value = 0
            if var[0] in ["delta_phi_diJet", "pt_balance"]:
                null_value = -1

            mask = x_test[:,i] != null_value
            x_test[mask, i] = (x_test[mask, i] - mean_map[var[0]]) / std_map[var[0]]


    # get model from file
    with open(model_file, "rb") as pkl_file:
        model = pickle.load(pkl_file)

    # make predictions for test data
    y_pred = model.predict_proba(x_test)[:, 1]
    print("y_pred", y_pred)
    # predictions = [round(value) for value in y_pred]

    # make histogram of discriminator value for signal and bkg
    y_frame = pd.DataFrame({"truth": y_test, "disc": y_pred})
    print("y_frame", y_frame)
    disc = y_frame[y_frame["truth"] == 0]["disc"].values
    plt.figure()
    plt.hist(disc, bins=50, alpha=0.3)
    plt.savefig("mydiscriminator_" + era + ".png")

    ##Creating a new TTree with the discriminator

    nEntries = Tree.GetEntries()
    print("nEntries = ", nEntries)
    _disc_var_name = "BDT_" + channel_US

    root.gROOT.ProcessLine("struct MyStruct{float disc;};")

    from ROOT import MyStruct

    # Create branches in the tree
    my_s = MyStruct()
    print(my_s)
    print(root.addressof(my_s))
    print(root.addressof(my_s, "disc"))
    root.addressof(my_s, "disc")
    bpt = Tree.Branch(_disc_var_name, root.addressof(my_s, "disc"), _disc_var_name + "/F")

    for i in range(nEntries):
        Tree.GetEntry(i)
        if i % 10000 == 0:
            print("Processing event nr. %i of %i" % (i, nEntries))
        my_s.disc = disc[i]
        bpt.Fill()

    Tree.GetCurrentFile().Write()
    Tree.GetCurrentFile().Close()

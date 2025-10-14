# import uproot as ur
import mplhep as hep
import numpy as np
import matplotlib.pyplot as plt
import uproot as ur
import sys

from labels import x_labels, n_bins, x_range, variables_type
from helper import (
    get_canvas,
    save_figure,
    clean_null_values,
    get_output_directory,
)

#type_error = "no_error"
#type_error = "cali_weight"
def draw_sig_and_bg_from_tuple(variable, era, category="", bsubset="", ssubset=""):
    plt.style.use(hep.style.CMS)

    #files_path = f"/eos/home-y/yulou/Fnal-hmm/root_io/tuples/BDT_score_{type_error}/{category}/BFull_SNottH/"
    #if category == "VBF": files_path += "merged/"

    background_path_no_error = f"/eos/home-y/yulou/Fnal-hmm/root_io/tuples/BDT_score_no_error/{category}/BFull_SNottH/data_Combined.root"
    with ur.open(background_path_no_error + ":tree_output") as file:
        background_branches_no_error = file.arrays([variable, "weight_no_lumi"], library="np")
    signal_path_no_error = f"/eos/home-y/yulou/Fnal-hmm/root_io/tuples/BDT_score_no_error/{category}/BFull_SNottH/signal_2023BPix.root"
    with ur.open(signal_path_no_error + ":tree_output") as file:
        signal_branches_no_error = file.arrays([variable, "weight_no_lumi"], library="np")

    background_path_cali_weight = f"/eos/home-y/yulou/Fnal-hmm/root_io/tuples/BDT_score_cali_weight/{category}/BFull_SNottH/data_Combined.root"
    with ur.open(background_path_cali_weight + ":tree_output") as file:
        background_branches_cali_weight = file.arrays([variable, "weight_no_lumi"], library="np")
    signal_path_cali_weight = f"/eos/home-y/yulou/Fnal-hmm/root_io/tuples/BDT_score_cali_weight/{category}/BFull_SNottH/signal_2023BPix.root"
    with ur.open(signal_path_cali_weight + ":tree_output") as file:
        signal_branches_cali_weight = file.arrays([variable, "weight_no_lumi"], library="np")

    clean_null_values(signal_branches_no_error, [variable, "weight_no_lumi"], variables_type)
    clean_null_values(background_branches_no_error, [variable, "weight_no_lumi"], variables_type)
    clean_null_values(signal_branches_cali_weight, [variable, "weight_no_lumi"], variables_type)
    clean_null_values(background_branches_cali_weight, [variable, "weight_no_lumi"], variables_type)

    variable_bin = variable
    if variable + "_" + category in x_range:
        variable_bin += "_" + category

    bkg_histogram_no_error, bins = np.histogram(
        background_branches_no_error[variable],
        bins=n_bins[variable_bin],
        range=x_range[variable_bin],
    )
    signal_histogram_no_error, _ = np.histogram(
        signal_branches_no_error[variable],
        bins=n_bins[variable_bin],
        range=x_range[variable_bin],
        weights=signal_branches_no_error["weight_no_lumi"],
    )
    bkg_histogram_cali_weight, bins = np.histogram(
        background_branches_cali_weight[variable],
        bins=n_bins[variable_bin],
        range=x_range[variable_bin],
    )
    signal_histogram_cali_weight, _ = np.histogram(
        signal_branches_cali_weight[variable],
        bins=n_bins[variable_bin],
        range=x_range[variable_bin],
        weights=signal_branches_cali_weight["weight_no_lumi"],
    )

    fig, ax = get_canvas()

    hep.histplot(
        signal_histogram_no_error / np.sum(signal_histogram_no_error),
        bins,
        yerr=False,
        histtype="fill",
        label="signal_no_error",
        ax=ax,
        color="blue",
        alpha=0.4,
    )

    hep.histplot(
        signal_histogram_cali_weight / np.sum(signal_histogram_cali_weight),
        bins,
        yerr=False,
        ax=ax,
        label="signal_cali_weight",
        color="blue",
        linewidth=3,
    )

    hep.histplot(
        bkg_histogram_no_error / np.sum(bkg_histogram_no_error),
        bins,
        yerr=False,
        histtype="fill",
        label="data_no_error",
        ax=ax,
        color="red",
        alpha=0.4,
    )

    hep.histplot(
        bkg_histogram_cali_weight / np.sum(bkg_histogram_cali_weight),
        bins,
        yerr=False,
        label="data_cali_weight",
        ax=ax,
        color="red",
        linewidth=3,
    )
    hep.cms.label(data="True", label="", year=era, com="13.6", ax=ax)


    ax.set_ylabel("Events / Total events")
    #ax.set_xlabel(x_labels[variable] +" of "+ type_error)
    ax.set_xlabel(x_labels[variable] +" of "+ category)

    ymax = max(np.max(bkg_histogram_no_error / np.sum(bkg_histogram_no_error)),
               np.max(signal_histogram_no_error / np.sum(signal_histogram_no_error)))

    print("variable:", variable)
    
    ax.set_ylim(0.0, 1.3 * ymax)
    ax.set_xlim(bins[0], bins[-1])
    ax.legend(frameon=False, loc="upper right", ncols=1)

    output_directory = "../plots/sig_vs_bkg/" + category + "/" + "B" + bsubset + "_S" + ssubset + "/" + era + "/"
    #output_directory = get_output_directory(variable, output_directory, variables_type)

    save_figure(fig, output_directory, variable + "_" + era + "_sig_vs_bkg_both_errors")
    print("Saved plot of " + variable + " in " + output_directory)

    plt.close()




eras = ["Combined"]
background_subset = ["Full"]
# background_subset = ["NoDY50"]
# signal_subset = ["Full", "NottH", "VBF"]
signal_subset = ["NottH"]
# signal_subset = ["VBF"]


for channel_US in ["ggH", "VBF"]:
    variables = [
    ## DiMuon variables
    "BDT_ggH",]

    if channel_US == "VBF":
        variables = [
            "BDT_VBF"
        ]
    for bsubset in background_subset:
        for ssubset in signal_subset:
            for era in eras:
                for variable in variables:
                    draw_sig_and_bg_from_tuple(variable, era, channel_US,
                                            bsubset, ssubset)

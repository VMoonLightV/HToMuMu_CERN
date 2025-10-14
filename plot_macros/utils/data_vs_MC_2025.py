import uproot as ur
import mplhep as hep
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import csv

from .labels import (
    x_labels,
    background_labels,
    luminosity,
    x_range,
    n_bins,
    variables_type,
)  # , y_labels
from .helper import (
    get_canvas,
    save_figure,
    get_histograms_ratio,
    get_output_directory,
    clean_null_values,
)

signal_colors = {"ggH": "red", "VBF": "blue", "ttH": "lime"}

y_axis_max_range = {
    "mu1_pt_mass_ratio": 10e6,
    "mu2_pt_mass_ratio": 10e6,
    "mu1_bsConstrainedPt_mass_ratio": 10e6,
    "mu2_bsConstrainedPt_mass_ratio": 10e6,
    "mu1_eta": 10e6,
    "mu2_eta": 10e6,
    "phi_CS": 10e6,
    "cos_theta_CS": 10e6,
    "mu1_pt": 10e8,
    "mu2_pt": 10e8,
    "mu1_ptErr": 10e8,
    "mu2_ptErr": 10e8,
    "mu1_bsConstrainedPt": 10e8,
    "mu2_bsConstrainedPt": 10e8,
    "mu1_bsConstrainedPtErr": 10e8,
    "mu2_bsConstrainedPtErr": 10e8,
    "diMuon_mass": 10e6,
    "diMuon_bsConstrainedMass": 10e6,
    "diMuon_rapidity": 10e6,
    "diMuon_mass_full_range": 10e8,
    "diMuon_bsConstrainedMass_full_range": 10e8,
    "diMuon_bsConstrainedPt": 10e8,
    "diMuon_pt": 10e8,
    "diMuon_phi": 10e8,
    "diMuon_eta": 10e8,
    "relative_diMuon_mass_error": 10e6,
    "relative_diMuon_bsConstrainedMass_error": 10e6,
    "n_jet": 10e8,
    "jet_pt": 10e8,
    "jet_eta": 10e8,
    "jet_phi": 10e8,
    "jet_mass": 10e8,
    "diJet_pt": 10e8,
    "diJet_eta": 10e8,
    "diJet_phi": 10e8,
    "diJet_mass": 10e8,
    "diJet_mass_mo": 10e8,
    "diJet_DeltaEta": 10e8,
    "pt_balance": 10e8,
    "pt_centrality": 10e8,
    "n_SoftJet_pt2": 10e8,
    "n_SoftJet_pt5": 10e8,
    "n_SoftJet_pt10": 10e8,
    "HT": 10e8,
    "HT_pt2": 10e8,
    "HT_pt5": 10e8,
    "HT_pt10": 10e8,
}


def get_color_list(number_of_histograms):
    colors = [
        "#3f90da",
        "#ffa90e",
        "#bd1f01",
        "#94a4a2",
        "#832db6",
        "#a96b59",
        "#e76300",
        "#b9ac70",
        "#717581",
        "#92dadd",
    ]

    color_list = []
    for i in range(number_of_histograms):
        color_list.append(colors[i])

    return color_list


def get_background_label_list(background_sources):
    labels_list = []
    for source in background_sources:
        labels_list.append(background_labels[source])
    return labels_list


def get_histograms_from_tuple(
    input_dir,
    sources,
    era,
    variables,
    is_background,
    use_puweight,
    use_ggH_category,
    use_VBF_category,
    njet,
    region,
    lumi_rescale=False,
    isZRange=False,
):
    #if not use_puweight:
    variables.append("pileup_weight")
    variables.append("pileup_weight_up")
    variables.append("pileup_weight_down")

    #variables.append("diMuon_bsConstrainedMass")

    histograms_list = []
    bins_list = []
    DY_count = 0
    TT_count = 0

    # For 2024 data there is not simulations yet!!!
    # so in the case we re escale the luminosity
    era_reweight = 1

    #if lumi_rescale:
        # era_reweight = 106.45/9.45

    variable_bin = variables[0]
    print("era: " + era)
    variables.append("diMuon_bsConstrainedMass")

    for source in sources:
        with ur.open(input_dir + source + "_" + era + "_tuples.root:tree_output") as file:
            branches = file.arrays(variables, library="np")

            if (
                    variables[0] != "diMuon_bsConstrainedMass"
                    and ("bsConstrained" in variables[0])
                    and is_background
                ):
                    bool_list = (branches["diMuon_bsConstrainedMass"] > 130) | (
                        branches["diMuon_bsConstrainedMass"] < 120
                    )

            elif (
                    variables[0] != "diMuon_mass"
                    and variables[0] != "diMuon_bsConstrainedMass"
                    and is_background
                ):
                    bool_list = (branches["diMuon_mass"] > 130) | (
                        branches["diMuon_mass"] < 120
                    )
                    
            bool_list = (branches["diMuon_bsConstrainedMass"] > 70) | (
                branches["diMuon_bsConstrainedMass"] < 110
            )
            
            for variable in variables:
                        branches[variable] = branches[variable][bool_list]

            clean_null_values(branches, variables, variables_type)

            # print(variables)
            if "delta_phi" in variables[0]:
                branches[variables[0]] = np.absolute(branches[variables[0]])

            if isZRange:
                variable_bin = "diMuon_mass_Z"
            elif variables[0] == "calibrated_diMuon_bsConstrainedMass_error":
                variable_bin = "relative_diMuon_bsConstrainedMass_error"

            base_bins = np.linspace(
                x_range[variable_bin][0],
                x_range[variable_bin][1],
                n_bins[variable_bin] + 1,
            )

            print("use_puweight:", use_puweight)
            
            # count pileup_weight issues
            total_events = len(branches["pileup_weight"])
            zero_pileup_events = np.sum(branches["pileup_weight"] == 0)
            nan_pileup_events = np.sum(np.isnan(branches["pileup_weight"]))
            negative_pileup_events = np.sum(branches["pileup_weight"] < 0)
            print("-" * 50)
            print(f"Source: {source}")
            print(f"Total events: {total_events}")
            print(f"Events with pileup_weight = 0: {zero_pileup_events} ({100*zero_pileup_events/total_events:.2f}%)")
            print(f"Events with pileup_weight = NaN: {nan_pileup_events} ({100*nan_pileup_events/total_events:.2f}%)")
            print(f"Events with pileup_weight < 0: {negative_pileup_events} ({100*negative_pileup_events/total_events:.2f}%)")
            print(f"Min pileup_weight: {np.min(branches['pileup_weight']):.6f}")
            print(f"Max pileup_weight: {np.max(branches['pileup_weight']):.6f}")
            

            histogram, bins = np.histogram(
                branches[variables[0]],
                bins=base_bins,
                # weights=branches["weight"],
                weights=(
                    branches["weight"] * era_reweight * np.where(
                        branches["pileup_weight"] != 0,
                        branches["pileup_weight_up"] / branches["pileup_weight"],
                        1.0
                    )
                    if use_puweight
                    else branches["weight"] * np.where(
                        branches["pileup_weight"] != 0, 
                        1.0 / branches["pileup_weight"], 
                        1.0
                    )
                ),
            ) 

            histograms_list.append(histogram)
            bins_list.append(bins)
            # histograms_list[source] = histogram
            # bins_list[source] = bins
            if source == "DY":
                DY_count = histogram.sum()
                print("DY in bkg list", DY_count)
            
            if source == "TT":
                TT_count = histogram.sum()
                print("TT in bkg list", TT_count)

    return histograms_list, bins_list, DY_count+TT_count



def draw_data_and_simul_and_ratio(
    input_dir,
    variable,
    era,
    background_sources,
    signal_sources,
    njet,
    region,
    use_puweight=True,
    use_ggH_category=False,
    use_VBF_category=False,
):
    plt.style.use(hep.style.CMS)

    print("*" * len("****** PLOTTING " + variable + " *****"))
    print("****** PLOTTING " + variable + " *****")
    print("*" * len("****** PLOTTING " + variable + " *****"))

    isZRange = False
    if variable == "diMuon_mass_Z":
        variable = "diMuon_mass"
        isZRange = True

    elif variable == "diMuon_bsConstrainedMass_Z":
        variable = "diMuon_bsConstrainedMass"
        isZRange = True

    variables = [
        variable,
        "weight",
        "diMuon_bsConstrainedMass"
    ]
    if ("bsConstrained" in variable) and variable != "diMuon_bsConstrainedMass":
        variables.append("diMuon_bsConstrainedMass")
    elif variable != "diMuon_mass" and variable != "diMuon_bsConstrainedMass":
        variables.append("diMuon_mass")
    if use_ggH_category:
        variables.append("is_ggH_category")
    elif use_VBF_category:
        variables.append("is_VBF_category")

    if isZRange:
        variable_bin = "diMuon_mass_Z"
    elif variable == "calibrated_diMuon_bsConstrainedMass_error":
        variable_bin = "relative_diMuon_bsConstrainedMass_error"
    else:
        variable_bin = variable

    if use_ggH_category and (variable + "_ggH" in x_range):
        variable_bin += "_ggH"
    if use_VBF_category and (variable + "_VBF" in x_range):
        variable_bin += "_VBF"

    with ur.open(input_dir + "Data_" + era + "_tuples.root:tree_output") as data_file:
        branches = data_file.arrays(variables, library="np")
        if "bsConstrained" in variable:
            bool_list = (branches["diMuon_bsConstrainedMass"] > 130) | (
                branches["diMuon_bsConstrainedMass"] < 120
            )
        else:
            bool_list = (branches["diMuon_mass"] > 130) | (
               branches["diMuon_mass"] < 120
            )
            
        bool_list = (branches["diMuon_bsConstrainedMass"] > 70) | (
                branches["diMuon_bsConstrainedMass"] < 110
            )

        for var in variables:
            branches[var] = branches[var][bool_list]
        # branches[variable] = branches[variable][

        if "delta_phi" in variable:
            branches[variable] = np.absolute(branches[variable])

        print(x_range[variable_bin], n_bins[variable_bin])
        base_bins = np.linspace(
            x_range[variable_bin][0], x_range[variable_bin][1], n_bins[variable_bin] + 1
        )

        data_histogram, data_bins = np.histogram(branches[variable], bins=base_bins)

    if variable == "diMuon_mass" or variable == "diMuon_bsConstrainedMass":
        data_histogram[data_histogram == 0] = -100.0
        print("Era: " + era + " | Events: " + str(len(branches[variable])))
    data_count = data_histogram.sum()
    print("Data in " + variable + ":", data_count)

    simulation_era = era
    #if era == "2024":
     #   simulation_era = "2023BPix"

    print(variables)
    DY_TT_count = 0
    bkg_histograms_list, bkg_bins_list, DY_TT_count = get_histograms_from_tuple(
        input_dir,
        background_sources,
        simulation_era,
        variables,
        True,
        use_puweight,
        use_ggH_category,
        use_VBF_category,
        njet,
        region,
        era == "2024",
        isZRange,
    )
    
    MC_normalization_factor = data_count / DY_TT_count
    print("MC normalization factor:", MC_normalization_factor)
    for i in range(len(bkg_histograms_list)):
        bkg_histograms_list[i] = bkg_histograms_list[i] * MC_normalization_factor
    '''
    signal_histograms_list, signal_bins_list, no_meaning_value = (
        get_histograms_from_tuple(
            input_dir,
            signal_sources,
            "2023BPix",
            variables,
            False,
            use_puweight,
            use_ggH_category,
            use_VBF_category,
            njet,
            region,
            era == "2024",
            isZRange,
        )
    )
    '''

    fig, axs = get_canvas(True)

    hep.histplot(
        bkg_histograms_list,
        bkg_bins_list[0],
        yerr=True,
        histtype="fill",
        label=get_background_label_list(background_sources),
        ax=axs[0],
        stack=True,
        color=get_color_list(len(background_sources)),
    )

    hep.histplot(
        data_histogram,
        data_bins,
        yerr=True,
        histtype="errorbar",
        label="data",
        color="black",
        ax=axs[0],
    )

    signal_scale_factor = 100
    '''
    for source, histogram in zip(signal_sources, signal_histograms_list):
        if source == "ttH":
            signal_scale_factor *= 10
        hep.histplot(
            histogram * signal_scale_factor,
            signal_bins_list[0],
            yerr=False,
            # yerr=True,
            label=source + " (x" + str(signal_scale_factor) + ")",
            color=signal_colors[source],
            ax=axs[0],
        )
    '''

    hep.cms.label(
        data="True",
        label="" if use_puweight else "No pu weight",
        year=era,
        com="13.6",
        lumi=luminosity[era],
        ax=axs[0],
    )

    axs[0].set_ylabel(r"Events")
    # axs[0].set_ylim(-10000, y_axis_max_range[variable])
    # axs[0].set_ylim(0.1, y_axis_max_range[variable])
    #axs[0].set_ylim(0.1, 1000 * np.max(data_histogram))
    axs[0].set_ylim(0.1, 1.4 * np.max(data_histogram))
    axs[0].set_xlim(data_bins[0], data_bins[-1])

    #axs[0].set_yscale("log")
    axs[0].legend(frameon=False, loc="upper right", ncols=2)
    axs[0].tick_params(axis="x", which="both", bottom=True, top=True, labelbottom=False)

    plt.axhline(y=1, color="grey", linestyle="--", alpha=0.5)

    tot_bg_numpy_hist = np.array([])
    for i, bg_hist in enumerate(bkg_histograms_list):
        if i == 0:
            tot_bg_numpy_hist = bg_hist
        else:
            tot_bg_numpy_hist = tot_bg_numpy_hist + bg_hist

    ratio_hist, ratio_error = get_histograms_ratio(data_histogram, tot_bg_numpy_hist)

    # print(tot_bg_numpy_hist)
    sum_MC = sum([hist.sum() for hist in tot_bg_numpy_hist])

    print(sum_MC)

    
    hep.histplot(
        ratio_hist,
        data_bins,
        yerr=ratio_error,
        histtype="errorbar",
        label="data",
        color="black",
        ax=axs[1],
    )

    #if era == "2024":
       # axs[1].set_ylabel("Data/MC(2023BPix)", loc="center")
    #else:
    axs[1].set_ylabel("Data/MC", loc="center")
    axs[1].set_ylim(0.5, 1.5)
    axs[1].set_xlim(data_bins[0], data_bins[-1])
    #axs[1].set_xlabel(f"{njet}jet {region} " + x_labels[variable_bin])
    axs[1].set_xlabel(x_labels[variable_bin])



    output_directory = f"../plots-2024/ratio/" + era + "/"
    if not use_puweight:
        output_directory = "../plots-2024/ratio/" + era + "/no_puWeight/"
    output_directory = get_output_directory(variable, output_directory, variables_type)

    if isZRange:
        save_figure(fig, output_directory, variable + "_Z_" + era + "_MCData_ratio_up_linear")
    else:
        save_figure(fig, output_directory, variable + "_" + era + "_MCData_ratio_up_linear")
    plt.close()

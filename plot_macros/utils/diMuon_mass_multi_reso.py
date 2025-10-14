import uproot as ur
import mplhep as hep
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import csv

merge_low_pt_eta = True

plot_version = "EVE_resolution_voigtian_merge_lowPt"


muon1_pt_cuts = [26.0, 45.0, 52.0, 62.0, 200.0]

eta_cuts = {"B": [0.0, 0.9], "O": [0.9, 1.8], "E": [1.8, 2.4]}

csv_label = {
    "relative_diMuon_bsConstrainedMass_error": "rela_reso",
    "calibrated_diMuon_bsConstrainedMass_error": "cali_reso",
    "relative_diMuon_bsConstrainedMass_sigma": "rela_sigma",
    "calibrated_diMuon_bsConstrainedMass_sigma": "cali_sigma",
}


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

region_colors = {
    "BB": "#1f77b4",
    "BO": "#ff7f0e",
    "BE": "#2ca02c",
    "OB": "#d62728",
    "OO": "#9467bd",
    "OE": "#8c564b",
    "EB": "#e377c2",
    "EO": "#7f7f7f",
    "EE": "#bcbd22",
    "B+O+E_B": "#1f77b4",
    "B+O+E_O": "#ff7f0e",
    "B+O+E_E": "#2ca02c",
}


def get_weighted_median(data, weights):

    # calculate data medium
    valid_indices = weights > 0
    data = data[valid_indices]
    weights = weights[valid_indices]

    if len(data) == 0:
        return np.nan

    # sort the data by value
    sorted_indices = np.argsort(data)
    data_sorted = data[sorted_indices]
    weights_sorted = weights[sorted_indices]

    # calculate total weight
    cumulative_weights = np.cumsum(weights_sorted)
    total_weight = cumulative_weights[-1]

    # find medium value
    median_weight = total_weight / 2.0
    median_index = np.searchsorted(cumulative_weights, median_weight, side="right")

    if median_index < len(data_sorted):
        return data_sorted[median_index]
    else:
        return data_sorted[-1]


def get_histograms_from_tuple(
    era,
    channel,
    variables,
    is_background,
    use_puweight,
    muon1_region,
    draw_cali_root,
    root_dir,
    lumi_rescale=False,
):
    if not use_puweight:
        variables.append("pileup_weight")

    isZRange = False

    histograms_list = []
    bins_list = []
    eta_names = []
    median_values = []

    # For 2024 data there is not simulations yet!!!
    # so in the case we rescale the luminosity
    era_reweight = 1

    # if lumi_rescale:
    # era_reweight = 106.45/9.45
    # if use_ggH_category:
    #    era_reweight = 50112710 / 5438017
    # elif use_VBF_category:
    #    era_reweight = 127867 / 28980
    # era = "2023BPix"

    variable_bin = variables[0]

    if merge_low_pt_eta == True and muon1_region == 0:
        if draw_cali_root == False:
            for region_2, eta_range_2 in eta_cuts.items():

                all_data_for_current_group = []
                all_weights_for_current_group = []

                for region_1, eta_range_1 in eta_cuts.items():
                    category_name = f"{region_1}{region_2}_mu1_pt_{muon1_pt_cuts[0]}_{muon1_pt_cuts[1]}"
                    tree_name = f"tree_EVE_{category_name}"
                    with ur.open(
                        root_dir + channel + "_" + era + "_skim.root:" + tree_name
                    ) as data_file:
                        branches = data_file.arrays(library="np")
                        clean_null_values(branches, variables, variables_type)

                        data_array_small = branches[variables[0]]

                        if "data" in channel.lower():
                            weights_array_small = np.ones_like(data_array_small)
                        else:
                            weights_array_small = (
                                branches["weight"] * era_reweight
                                if use_puweight
                                else branches["weight"] / branches["pileup_weight"]
                            )
                        all_data_for_current_group.append(data_array_small)
                        all_weights_for_current_group.append(weights_array_small)

                combined_data = np.concatenate(all_data_for_current_group)
                combined_weights = np.concatenate(all_weights_for_current_group)

                eta_region = f"B+O+E_{region_2}"

                median_value = get_weighted_median(combined_data, combined_weights)
                print(
                    f"For combined eta_region {eta_region} Median: {median_value:.4f}"
                )

                if "error" in variables[0]:
                    base_bins = np.linspace(0, 0.1, 101)
                else:
                    base_bins = np.linspace(0, 5, 101)

                histogram, bins = np.histogram(
                    combined_data, bins=base_bins, weights=combined_weights
                )

                histograms_list.append(histogram)
                bins_list.append(bins)
                eta_names.append(eta_region)
                median_values.append(median_value)
        else:
            for region_2, eta_range_2 in eta_cuts.items():
                eta_region = f"B+O+E_{region_2}"

                with ur.open(
                    f"{root_dir}/{channel}_" + era + "_skim.root:tree_output"
                ) as data_file:

                    branches = data_file.arrays(library="np")
                    clean_null_values(branches, variables, variables_type)

                    ###################
                    # only for calibration

                    bool_list = (
                        (branches["mu1_bsConstrainedPt"] > muon1_pt_cuts[0])
                        & (branches["mu1_bsConstrainedPt"] < muon1_pt_cuts[1])
                        & (abs(branches["mu1_eta"]) > 0.0)
                        & (abs(branches["mu1_eta"]) < 2.4)
                        & (abs(branches["mu2_eta"]) > eta_cuts[region_2][0])
                        & (abs(branches["mu2_eta"]) < eta_cuts[region_2][1])
                    )

                    for variable in variables:
                        branches[variable] = branches[variable][bool_list]

                    branches["weight"] = branches["weight"][bool_list]
                    ###################

                    data_array = branches[variables[0]]

                    if "data" in channel.lower():
                        weights_array = np.ones_like(data_array)
                    else:
                        weights_array = (
                            branches["weight"] * era_reweight
                            if use_puweight
                            else branches["weight"] / branches["pileup_weight"]
                        )

                    median_value = get_weighted_median(data_array, weights_array)
                    print(f"For eta_region {eta_region} Median: {median_value:.4f}")

                    if "error" in variables[0]:
                        base_bins = np.linspace(0, 0.1, 101)
                    else:
                        base_bins = np.linspace(0, 5, 101)

                    histogram, bins = np.histogram(
                        data_array, bins=base_bins, weights=weights_array
                    )

                    histograms_list.append(histogram)
                    bins_list.append(bins)
                    eta_names.append(eta_region)
                    median_values.append(median_value)

    else:
        i = muon1_region
        for region_1, eta_range_1 in eta_cuts.items():
            for region_2, eta_range_2 in eta_cuts.items():
                muon1_cut1, muon1_cut2 = muon1_pt_cuts[i], muon1_pt_cuts[i + 1]
                eta_region = f"{region_1}{region_2}"

                category_name = f"{region_1}{region_2}_mu1_pt_{muon1_pt_cuts[i]}_{muon1_pt_cuts[i+1]}"
                tree_name = f"tree_EVE_{category_name}"

                if draw_cali_root == True:
                    with ur.open(
                        f"{root_dir}/{channel}_" + era + "_skim.root:tree_output"
                    ) as data_file:

                        branches = data_file.arrays(library="np")
                        clean_null_values(branches, variables, variables_type)

                        ###################
                        # only for calibration

                        bool_list = (
                            (branches["mu1_bsConstrainedPt"] > muon1_pt_cuts[i])
                            & (branches["mu1_bsConstrainedPt"] < muon1_pt_cuts[i + 1])
                            & (abs(branches["mu1_eta"]) > eta_cuts[region_1][0])
                            & (abs(branches["mu1_eta"]) < eta_cuts[region_1][1])
                            & (abs(branches["mu2_eta"]) > eta_cuts[region_2][0])
                            & (abs(branches["mu2_eta"]) < eta_cuts[region_2][1])
                        )

                        for variable in variables:
                            branches[variable] = branches[variable][bool_list]

                        branches["weight"] = branches["weight"][bool_list]
                        ###################

                        data_array = branches[variables[0]]

                        if "data" in channel.lower():
                            weights_array = np.ones_like(data_array)
                        else:
                            weights_array = (
                                branches["weight"] * era_reweight
                                if use_puweight
                                else branches["weight"] / branches["pileup_weight"]
                            )

                        median_value = get_weighted_median(data_array, weights_array)
                        print(f"For eta_region {eta_region} Median: {median_value:.4f}")

                        if "error" in variables[0]:
                            base_bins = np.linspace(0, 0.1, 101)
                        else:
                            base_bins = np.linspace(0, 5, 101)

                        histogram, bins = np.histogram(
                            data_array, bins=base_bins, weights=weights_array
                        )

                        histograms_list.append(histogram)
                        bins_list.append(bins)
                        eta_names.append(eta_region)
                        median_values.append(median_value)
                else:

                    category_name = f"{region_1}{region_2}_mu1_pt_{muon1_pt_cuts[i]}_{muon1_pt_cuts[i+1]}"
                    tree_name = f"tree_EVE_{category_name}"
                    with ur.open(
                        f"{root_dir}/{channel}_" + era + "_skim.root:" + tree_name
                    ) as data_file:
                        branches = data_file.arrays(library="np")
                        clean_null_values(branches, variables, variables_type)

                        data_array = branches[variables[0]]

                        if "data" in channel.lower():
                            weights_array = np.ones_like(data_array)
                        else:
                            weights_array = (
                                branches["weight"] * era_reweight
                                if use_puweight
                                else branches["weight"] / branches["pileup_weight"]
                            )

                        median_value = get_weighted_median(data_array, weights_array)
                        print(f"For eta_region {eta_region} Median: {median_value:.4f}")

                        if "error" in variables[0]:
                            base_bins = np.linspace(0, 0.1, 101)
                        else:
                            base_bins = np.linspace(0, 5, 101)

                        histogram, bins = np.histogram(
                            data_array, bins=base_bins, weights=weights_array
                        )

                    histograms_list.append(histogram)
                    bins_list.append(bins)
                    eta_names.append(eta_region)
                    median_values.append(median_value)

    return histograms_list, bins_list, eta_names, median_values


def draw_diMuon_mass_multi_reso(
    variables,
    era,
    channel,
    muon1_region,
    draw_cali_root,
    root_dir,
    use_puweight=True,
):
    plt.style.use(hep.style.CMS)

    print("****** PLOTTING *****")

    simulation_era = era
    signal_histograms_list, signal_bins_list, eta_names, median_values = (
        get_histograms_from_tuple(
            simulation_era,
            channel,
            variables,
            False,
            use_puweight,
            muon1_region,
            draw_cali_root,
            root_dir,
            era == "2024",
        )
    )

    fig, ax = plt.subplots()

    for eta_name, histogram in zip(eta_names, signal_histograms_list):
        print(f"{eta_name}_count: {histogram.sum()}")
        hep.histplot(
            histogram,
            signal_bins_list[0],
            yerr=False,
            label=eta_name,
            color=region_colors[eta_name],
            ax=ax,
        )

    hep.cms.label(
        data="True",
        label="" if use_puweight else "No pu weight",
        year=era,
        com="13.6",
        lumi=luminosity[era],
        ax=ax,
    )

    ax.set_ylabel(r"Events")
    ax.set_ylim(1, 10 * np.max(signal_histograms_list))
    ax.set_xlim(0, 0.1)
    if "error" in variables[0]:
        ax.set_xlim(0, 0.1)
    else:
        ax.set_xlim(0, 5)

    ax.set_yscale("log")
    ax.legend(frameon=False, loc="upper right", ncols=2)
    ax.set_xlabel(r"relative diMuon BCSmass reso")

    output_directory = f"../plots/{plot_version}/{channel}/{era}/"
    if not use_puweight:
        output_directory = f"../plots/{plot_version}_no_puWeight/{channel}/{era}/"

    pt_range_string = f"{muon1_pt_cuts[muon1_region]}_{muon1_pt_cuts[muon1_region+1]}"

    save_figure(
        fig,
        output_directory,
        f"BSC_Z_multi_{csv_label[variables[0]]}_mu1pt_" + pt_range_string,
    )
    plt.close()

    data_to_save = {
        "pt_range": [pt_range_string] * len(eta_names),
        "eta_category": eta_names,
        f"median_value_{csv_label[variables[0]]}": median_values,
    }

    df = pd.DataFrame(data_to_save)
    output_filename = (
        f"{output_directory}BCS_Z_mass_multi_median_{csv_label[variables[0]]}.csv"
    )
    file_exists = os.path.exists(output_filename)
    if muon1_region == 0:
        file_exists = False
        df.to_csv(output_filename, index=False, mode="w", header=not file_exists)
    else:
        df.to_csv(output_filename, index=False, mode="a", header=not file_exists)

    if not file_exists:
        print(f"File {output_filename} created and data saved.")
    else:
        print(f"Data appended to {output_filename}.")

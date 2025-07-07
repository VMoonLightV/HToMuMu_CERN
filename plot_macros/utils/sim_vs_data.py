import uproot as ur
import mplhep as hep
import numpy as np
import matplotlib.pyplot as plt

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
from .colors import(
    signal_colors,
    get_color_list,
)

def get_background_label_list(background_sources):
    labels_list = []
    for source in background_sources:
        labels_list.append(background_labels[source])
    return labels_list


def get_histograms_from_tuple(
    sources,
    era,
    variables,
    is_background,
    use_puweight,
    production_channel,
    bdt_cuts=[],
    bdt_subset="",
    lumi_rescale=False,
    Z_study=False,
):
    
    if not use_puweight:
        variables.append("pileup_weight")
    # variables.append("pileup_weight")
    # variables.append("pileup_weight_down")


    histograms_list = []
    bins_list = []

    # For 2024 data there is not simulations yet!!!
    # so in the case we re escale the luminosity
    era_reweight = 1
    if lumi_rescale:
        print("Re scaling lumi")
        era_reweight = 109.08 / 9.45
        era = "2023BPix"

    variable_bin = variables[0]

    if variable_bin + "_" + production_channel in x_range:
        variable_bin += "_" + production_channel

    tuple_path = "../root_io/tuples/"
    if bdt_subset != "" and len(bdt_cuts) != 0:
        tuple_path += "BDT_score/" + production_channel + "/" + bdt_subset + "/"

    for source in sources:
        file_name = source + "_" + era + "_tuples.root:tree_output"
        if bdt_subset != "" and len(bdt_cuts) != 0:
            file_name = source + "_" + era + "_" + bdt_subset + ".root:tree_output"

        with ur.open(tuple_path + file_name) as file:
            branches = file.arrays(variables, library="np")

            bool_list = np.ones(len(branches[variables[0]]), dtype=bool)

            if variables[0] != "diMuon_bsConstrainedMass" and ("bsConstrained" in variables[0]) and is_background:
                bool_list = (bool_list) & (branches["diMuon_bsConstrainedMass"] > 130) | (
                    branches["diMuon_bsConstrainedMass"] < 120
                )
                if not Z_study:
                    bool_list = (bool_list) & (branches["diMuon_bsConstrainedMass"] > 110) & (
                        branches["diMuon_bsConstrainedMass"] < 150
                    )


            elif variables[0] != "diMuon_mass" and ("bsConstrained" not in variables[0]) and is_background:
                bool_list = (bool_list) & (
                    ((branches["diMuon_mass"] > 130) | (branches["diMuon_mass"] < 120))
                )
                if not Z_study:
                    bool_list = (bool_list) & (branches["diMuon_mass"] > 110) & (
                        branches["diMuon_mass"] < 150
                    )

            if production_channel != "":
                bool_list = (bool_list) & (
                    branches["is_" + production_channel + "_category"] == 1
                )

            if len(bdt_cuts) > 1:
                bdt_bool = (branches["BDT_" + production_channel] > bdt_cuts[0]) & (
                    branches["BDT_" + production_channel] < bdt_cuts[1]
                )
                bool_list = (bool_list) & (bdt_bool)

            for var in variables:
                branches[var] = branches[var][bool_list]

            clean_null_values(branches, variables, variables_type)

            if "delta_phi" in variables[0]:
                branches[variables[0]] = np.absolute(branches[variables[0]])

            if ((variables[0] == "diMuon_mass") | (variables[0] == "diMuon_bsConstrainedMass")) and Z_study:
                number_of_bins = 80; 
                x_range_histos = (85,100)
            else:
                number_of_bins = n_bins[variable_bin]
                x_range_histos = x_range[variable_bin]

            histogram, bins = np.histogram(
                branches[variables[0]],
                bins=number_of_bins,
                range=x_range_histos,
                weights=(
                    branches["weight"] * era_reweight
                    # branches["weight"] * (branches["pileup_weight_down"] / branches["pileup_weight"])
                    if use_puweight
                    else branches["weight"] / branches["pileup_weight"]
                ),
            )
            histograms_list.append(histogram)
            bins_list.append(bins)
    return histograms_list, bins_list


def get_data_histograms_from_tuple(
    era,
    variables,
    production_channel,
    bdt_cuts,
    bdt_subset="",
    Z_study=False
):
    tuple_path = "../root_io/tuples/"
    file_name = "Data_" + era + "_tuples.root:tree_output"
    if bdt_subset != "" and len(bdt_cuts) != 0:
        tuple_path += "BDT_score/" + production_channel + "/" + bdt_subset + "/"
        file_name = "Data_" + era + "_" + bdt_subset + ".root:tree_output"

    with ur.open(tuple_path + file_name) as data_file:
        branches = data_file.arrays(variables, library="np")

        variable_bin = variables[0]
        if variable_bin + "_" + production_channel in x_range:
            variable_bin += "_" + production_channel


        if "bsConstrained" in variables[0]:
            bool_list = ((branches["diMuon_bsConstrainedMass"] > 130) | (branches["diMuon_bsConstrainedMass"] < 120))
            if not Z_study:
                bool_list = (bool_list) & (branches["diMuon_bsConstrainedMass"] > 110) & (
                    branches["diMuon_bsConstrainedMass"] < 150
                )
        else:
            bool_list = ((branches["diMuon_mass"] > 130) | (branches["diMuon_mass"] < 120))
            if not Z_study:
                bool_list = (bool_list) & (branches["diMuon_mass"] > 110) & (
                    branches["diMuon_mass"] < 150
                )
        
        if production_channel != "":
            bool_list = (bool_list) & (
                branches["is_" + production_channel + "_category"] == 1
            )

        if len(bdt_cuts) > 1:
            bdt_bool = (branches["BDT_" + production_channel] > bdt_cuts[0]) & (
                branches["BDT_" + production_channel] < bdt_cuts[1]
            )
            bool_list = (bool_list) & (bdt_bool)

        for var in variables:
            branches[var] = branches[var][bool_list]

        clean_null_values(branches, variables, variables_type)

        if "delta_phi" in variables[0]:
            branches[variables[0]] = np.absolute(branches[variables[0]])

        if (( variables[0] == "diMuon_mass") | (variables[0] == "diMuon_bsConstrainedMass")) and Z_study:
            number_of_bins = 80; 
            x_range_histos = (85,100)
        else:
            number_of_bins = n_bins[variable_bin]
            x_range_histos = x_range[variable_bin]
        
        data_histogram, data_bins = np.histogram(
            branches[variables[0]],
            bins=number_of_bins,
            range=x_range_histos,
        )

    return data_histogram, data_bins


def draw_data_and_simul_and_ratio(
    variable,
    era,
    background_sources,
    signal_sources,
    use_puweight=True,
    production_channel="",
    bdt_cuts=[],
    bdt_subset="",
    Z_study=False,
):
    plt.style.use(hep.style.CMS)

    print("*" * len("****** PLOTTING " + variable + " *****"))
    print("****** PLOTTING " + variable + " ERA " + era + " *****")
    print("*" * len("****** PLOTTING " + variable + " *****"))

    variables = [variable, "weight"] 
    if (("bsConstrained" in variable) and variable != "diMuon_bsConstrainedMass"):
        variables.append("diMuon_bsConstrainedMass")
    elif (variable != "diMuon_mass" and ("bsConstrained" not in variable)):
        variables.append("diMuon_mass")
    # if variable != "diMuon_mass":
    if production_channel != "":
        variables.append("is_" + production_channel + "_category")
    if len(bdt_cuts) != 0:
        variables.append("BDT_" + production_channel)

    data_histogram, data_bins = get_data_histograms_from_tuple(
        era,
        variables,
        production_channel,
        bdt_cuts,
        bdt_subset,
        Z_study=Z_study,
    )

    if variable == "diMuon_mass" or variable == "diMuon_bsConstrainedMass":
        data_histogram[data_histogram == 0] = -100.0

    bkg_histograms_list, bkg_bins_list = get_histograms_from_tuple(
        background_sources,
        era,
        variables,
        True,
        use_puweight,
        production_channel,
        bdt_cuts,
        bdt_subset,
        era == "2024",
        Z_study=Z_study
    )

    signal_histograms_list, signal_bins_list = get_histograms_from_tuple(
        signal_sources,
        era,
        variables,
        False,
        use_puweight,
        production_channel,
        bdt_cuts,
        bdt_subset,
        era == "2024",
        Z_study=Z_study
    )

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

    signal_scale_factor = 10
    for source, histogram in zip(signal_sources, signal_histograms_list):
        hep.histplot(
            histogram * signal_scale_factor,
            signal_bins_list[0],
            yerr=False,
            # yerr=True,
            label=source + " (x" + str(signal_scale_factor) + ")",
            color=signal_colors[source],
            ax=axs[0],
        )

    label = ""
    if not use_puweight:
        label = "No PU weight"
    if len(bdt_cuts) > 1:
        label = "Cat" + str(len(bdt_cuts) - 1)
    hep.cms.label(
        data="True",
        label=label,
        year=era,
        com="13.6",
        lumi=luminosity[era],
        ax=axs[0],
    )

    axs[0].set_ylabel(r"Events")
    axs[0].set_ylim(0.1, 1000 * np.max(data_histogram))
    axs[0].set_xlim(data_bins[0], data_bins[-1])
    axs[0].set_yscale("log")
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

    hep.histplot(
        ratio_hist,
        data_bins,
        yerr=ratio_error,
        histtype="errorbar",
        label="data",
        color="black",
        ax=axs[1],
    )

    if(era == "2024"):
        axs[1].set_ylabel("Data/MC(2023BPix)", loc="center")
    else:
        axs[1].set_ylabel("Data/MC", loc="center")
    axs[1].set_ylim(0.5, 1.5)
    axs[1].set_xlim(data_bins[0], data_bins[-1])
    axs[1].set_xlabel(x_labels[variable])

    output_directory = "../plots/ratio/" + era + "/"
    output_name = variable + "_" + era + "_MCData_ratio"
    if Z_study:
        output_name = variable + "_Z_included_" + era + "_MCData_ratio"

    if not use_puweight:
        output_directory = "../plots/ratio/" + era + "/no_puWeight/"
    if production_channel != "":
        output_directory = (
            "../plots/ratio/" + production_channel + "_category/" + era + "/"
        )
        output_directory = "../plots/ratio/" + production_channel + "_category/bdt_selections/" + era + "/"
    if len(bdt_cuts) > 1:
        output_name += label

    output_directory = get_output_directory(variable, output_directory, variables_type)

    save_figure(fig, output_directory, output_name)

    plt.close()

    if len(bdt_cuts) > 2:
        draw_data_and_simul_and_ratio(
            variable,
            era,
            background_sources,
            signal_sources,
            use_puweight=use_puweight,
            production_channel=production_channel,
            bdt_cuts=bdt_cuts[1:],
            bdt_subset=bdt_subset,
            Z_study=Z_study,
        )

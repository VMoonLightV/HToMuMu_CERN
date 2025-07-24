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

# polynominal fit for ZCR_normalization
order = 8

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
    sources, era, variables, is_background, use_puweight,
    use_ggH_category, use_VBF_category, njet, region, lumi_rescale=False, isZRange=False,
):
    if not use_puweight:
        variables.append("pileup_weight")

    histograms_list = []
    bins_list = []

    # For 2024 data there is not simulations yet!!!
    # so in the case we re escale the luminosity
    era_reweight = 1
    
    if lumi_rescale:
        #era_reweight = 106.45/9.45
        if(use_ggH_category):
            era_reweight = 50112710/5438017
        elif(use_VBF_category):
            era_reweight = 127867/28980
        era = "2023BPix"

    variable_bin = variables[0]
    if use_ggH_category and (variable_bin + "_ggH" in x_range):
        variable_bin += "_ggH"
    if use_VBF_category and (variable_bin + "_VBF" in x_range):
        variable_bin += "_VBF"

    for source in sources:
        with ur.open(
            f"/eos/home-y/yulou/Fnal-hmm/hmm-tuples/njet/{njet}jet/{region}/" + source + "_" + era + "_skim.root:tree_output"
        ) as file:
            branches = file.arrays(variables, library="np")
            if variables[0] != "diMuon_bsConstrainedMass" and ("bsConstrained" in variables[0]) and is_background:
                bool_list = (branches["diMuon_bsConstrainedMass"] > 130) | (
                    branches["diMuon_bsConstrainedMass"] < 120
                )
                for variable in variables:
                    branches[variable] = branches[variable][bool_list]

            elif (variables[0] != "diMuon_mass" and variables[0] != "diMuon_bsConstrainedMass" and is_background):
                bool_list = (branches["diMuon_mass"] > 130) | (
                    branches["diMuon_mass"] < 120
                )
                for variable in variables:
                    branches[variable] = branches[variable][bool_list]

            clean_null_values(branches, variables, variables_type)

            if use_ggH_category:
                bool_list = branches["is_ggH_category"] == 1
                for variable in variables:
                    branches[variable] = branches[variable][bool_list]
            elif use_VBF_category:
                bool_list = branches["is_VBF_category"] == 1
                for variable in variables:
                    branches[variable] = branches[variable][bool_list]

            #print(variables)
            if "delta_phi" in variables[0]:
                branches[variables[0]] = np.absolute(branches[variables[0]])

            if(isZRange):
                variable_bin = "diMuon_mass_Z"

            histogram, bins = np.histogram(
                branches[variables[0]],
                bins=n_bins[variable_bin],
                range=x_range[variable_bin],
                # weights=branches["weight"],
                weights=(
                    branches["weight"]*era_reweight
                    if use_puweight
                    else branches["weight"]/ branches["pileup_weight"]
                ),
            )
            histograms_list.append(histogram)
            bins_list.append(bins)
            # histograms_list[source] = histogram
            # bins_list[source] = bins

    return histograms_list, bins_list



def polyfit(df, output_name):

    x = df['BinCenter'].values
    y = df['RatioValue'].values

    coefficients = np.polyfit(x, y, order)

    poly_function = np.poly1d(coefficients)

    coeff_df = pd.DataFrame({
        'power': range(order, -1, -1),
        'coefficient': coefficients
    })
    coeff_df.to_csv(output_name, index=False)

    print(f"\nploynominal in {output_name}: ")
    print(poly_function)
    
    return coeff_df

def draw_data_and_simul_and_ratio(
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
    if(variable == "diMuon_mass_Z"):
        variable = "diMuon_mass"
        isZRange = True

    elif(variable == "diMuon_bsConstrainedMass_Z"):
        variable = "diMuon_bsConstrainedMass"
        isZRange = True

    variables = [variable, "weight"]
    if (("bsConstrained" in variable) and variable != "diMuon_bsConstrainedMass"):
        variables.append("diMuon_bsConstrainedMass")
    elif (variable != "diMuon_mass" and variable != "diMuon_bsConstrainedMass"):
        variables.append("diMuon_mass")
    if use_ggH_category:
        variables.append("is_ggH_category")
    elif use_VBF_category:
        variables.append("is_VBF_category")

    if(isZRange):
        variable_bin = "diMuon_mass_Z"
    else: 
        variable_bin = variable

    if use_ggH_category and (variable + "_ggH" in x_range):
        variable_bin += "_ggH"
    if use_VBF_category and (variable + "_VBF" in x_range):
        variable_bin += "_VBF"

    with ur.open(
        f"/eos/home-y/yulou/Fnal-hmm/hmm-tuples/njet/{njet}jet/{region}/Data_" + era + "_skim.root:tree_output"
    ) as data_file:
        branches = data_file.arrays(variables, library="np")
        if "bsConstrained" in variable:
            bool_list = (branches["diMuon_bsConstrainedMass"] > 130) | (branches["diMuon_bsConstrainedMass"] < 120)
        else:
            bool_list = (branches["diMuon_mass"] > 130) | (branches["diMuon_mass"] < 120)

        for var in variables:
            branches[var] = branches[var][bool_list]
        # branches[variable] = branches[variable][

        if "delta_phi" in variable:
            branches[variable] = np.absolute(branches[variable])

        if use_ggH_category:
            bool_list = branches["is_ggH_category"] == 1
            for var in variables:
                branches[var] = branches[var][bool_list]
        elif use_VBF_category:
            bool_list = branches["is_VBF_category"] == 1
            for var in variables:
                branches[var] = branches[var][bool_list]

        data_histogram, data_bins = np.histogram(
            branches[variable],
            bins=n_bins[variable_bin],
            range=x_range[variable_bin],
        )
        
        sum_data = len(branches[variable])

    if variable == "diMuon_mass" or variable == "diMuon_bsConstrainedMass":
        data_histogram[data_histogram == 0] = -100.0
        print("Era: " + era + " | Events: " + str(len(branches[variable])))

    simulation_era = era
    #if era == "2024":
        #simulation_era = "2023BPix"
    
    num_jet=njet

    print(variables)
    bkg_histograms_list, bkg_bins_list = get_histograms_from_tuple(
        background_sources, simulation_era, variables, True, use_puweight,
        use_ggH_category, use_VBF_category, njet, region, era == "2024", isZRange, 
    )
    signal_histograms_list, signal_bins_list = get_histograms_from_tuple(
        signal_sources, simulation_era, variables, False, use_puweight,
        use_ggH_category, use_VBF_category, njet, region, era == "2024", isZRange, 
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

    signal_scale_factor = 100
    for source, histogram in zip(signal_sources, signal_histograms_list):
        if(source == "ttH"):
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
    sum_MC = sum([hist.sum() for hist in tot_bg_numpy_hist])
    
    if "R" in region:
        print(f"{era} {njet}jet {region} data/MC num_events ({variable}): {sum_data} / {sum_MC}") #= {sum_data/sum_MC}")
        #if  variable != "n_jet":
        #    with open(f"/afs/cern.ch/user/y/yulou/CMSSW_14_0_14/src/HToMuMu/scripts/event_counts_{region}.txt", "a") as f:
        #      f.write(f"{era} {njet}jet ZCR data/MC num_events ({variable}): {sum_data} / {sum_MC} = {sum_data/sum_MC}" + "\n")
        
        csv_path = f"/afs/cern.ch/user/y/yulou/CMSSW_14_0_14/src/HToMuMu/scripts/event_counts_{region}.csv"
        write_header = not os.path.exists(csv_path)
        with open(csv_path, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            if write_header:
                csv_writer.writerow(["Era", "Njet", "Variable", "Region", "Data_Events", "MC_Events", "Ratio"])
            
            csv_writer.writerow([era, njet, variable, region, sum_data, sum_MC, sum_data/sum_MC])

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
    axs[1].set_xlabel(f"{njet}jet {region} "+x_labels[variable])
    
    if ("ZCR_normalization" in region) & (variable == "diMuon_pt"):
      axs[1].set_ylim(0.0, 2.0)
      
      iter_dir = f"../plots/ratio/njet/{njet}jet_ratio_table_dimuon_pt_{region}/" 
      os.makedirs(iter_dir, exist_ok=True)
            
      num_bins = len(ratio_hist)
      min_val, max_val= x_range[variable]
      range_val = max_val - min_val
      bin_width = range_val/num_bins
      bin_edges = np.linspace(0, range_val, num_bins + 1)
      bin_centers = bin_edges[:-1] + bin_width / 2
            
      df = pd.DataFrame({
                'BinCenter': bin_centers,
                'RatioValue': ratio_hist,
                'RatioError': ratio_error  
                })
                
      df.to_csv(f'{iter_dir}/{era}_ratio_table.csv', index=False)
      
      # draw fit curve
      output_file= f"{iter_dir}/polynomial_{era}_coefficients.csv"
            
      coeff_df = polyfit(df, output_file)
      coefficients = coeff_df['coefficient'].values
      x_fit = np.linspace(data_bins[0], data_bins[-1], 500)
      y_fit = np.polyval(coefficients, x_fit)
  
      axs[1].plot(x_fit, y_fit, 
              color='blue', 
              linewidth=2,
              linestyle='-',
              label=f'{order}-th Polynomial Fit')
  
      axs[1].legend(loc='best')
  

    output_directory = f"../plots/ratio/njet/{njet}jet_{region}/" + era + "/"
    if not use_puweight:
        output_directory = "../plots/ratio/" + era + "/no_puWeight/"
    if use_ggH_category:
        output_directory = "../plots/ratio/ggH_category/" + era + "/"
    elif use_VBF_category:
        output_directory = "../plots/ratio/VBF_category/" + era + "/"

    output_directory = get_output_directory(variable, output_directory, variables_type)

    if(isZRange):
        save_figure(fig, output_directory, variable + "_Z_" + era + "_MCData_ratio")
    else:
        save_figure(fig, output_directory, variable + "_" + era + "_MCData_ratio")
    plt.close()

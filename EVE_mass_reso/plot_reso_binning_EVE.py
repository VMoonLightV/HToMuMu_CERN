import uproot as ur
import mplhep as hep
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import csv
from scipy.optimize import curve_fit
from scipy.special import voigt_profile

plot_version = "EVE_resolution_voigtian_merge_lowPt"
root_dir = "ZCR_75-105_calibrated_all_channel"
mass_sigma_bin_old = [
    0.0,
    1.0,
    1.2,
    1.4,
    1.6,
    1.8,
    2.0,
    2.2,
    2.4,
    2.6,
    2.8,
    3.0,
    3.5,
    4.0,
    5.0,
]

mass_sigma_bin = [
    0.0,
    0.8,
    0.9,
    1.0,
    1.1,
    1.2,
    1.3,
    1.4,
    1.5,
    1.6,
    1.7,
    1.8,
    1.9,
    2.0,
    2.2,
    2.6,
    3.0,
]

muon1_pt_cuts = [26.0, 45.0, 52.0, 62.0, 200.0]

eta_cuts = {"B": [0.0, 0.9], "O": [0.9, 1.8], "E": [1.8, 2.4]}

csv_label = {
    "relative_diMuon_bsConstrainedMass_error": "rela_reso",
    "calibrated_diMuon_bsConstrainedMass_error": "cali_reso",
    "relative_diMuon_bsConstrainedMass_sigma": "rela_sigma",
    "calibrated_diMuon_bsConstrainedMass_sigma": "cali_sigma",
}

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


variables = ["diMuon_mass", "diMuon_bsConstrainedMass"]
Z_range = [80, 100]
H_range = [115, 135]
Z_fit_range = [89, 93]  ## make sense? used to be [89,93], or I can use [peak-2, peak+2]
Z_fit_width = 4  ## max width is 10GeV
H_fit_range = [122.5, 127.5]
Z_mass = 91
H_mass = 125
masses = {"Z": 91, "H": 125}


def gaussian(x, A, mean, std):
    return A * np.exp(-(((x - mean) / std) ** 2) / 2)


def voigtian(m, A, mZ, sigma_res, gamma_bw):
    return A * voigt_profile(m - mZ, sigma_res, gamma_bw)


def get_dynamic_fit_range(hist, search_range, fit_width):
    y_values, x_edges = hist
    x_centers = (x_edges[:-1] + x_edges[1:]) / 2.0

    search_mask = (x_centers >= search_range[0]) & (x_centers <= search_range[1])
    if not np.any(search_mask):
        print(f"warning: no data in  {search_range} GeV")
        return None, None

    peak_y_index_in_search = np.argmax(y_values[search_mask])
    peak_y_global_index = np.where(search_mask)[0][peak_y_index_in_search]

    peak_x_approx = x_centers[peak_y_global_index]

    fit_range_min = peak_x_approx - fit_width / 2.0
    fit_range_max = peak_x_approx + fit_width / 2.0

    minBin = np.where(x_centers >= fit_range_min)[0][0]
    maxBin = np.where(x_centers <= fit_range_max)[0][-1] + 1

    return minBin, maxBin, peak_x_approx


def calculate_effective_sigma_from_voigt(popt):

    sigma_res = popt[2]
    gamma_bw = popt[3]

    fwhm_g = sigma_res * 2.0 * np.sqrt(2.0 * np.log(2.0))
    fwhm_l = 2.0 * gamma_bw

    fwhm_v = 0.5346 * fwhm_l + np.sqrt(0.2166 * fwhm_l**2 + fwhm_g**2)
    sigma_eff = fwhm_v / (2.0 * np.sqrt(2.0 * np.log(2.0)))

    return sigma_eff


def plot_diMuon_comp_and_fit(
    fit_range, mass_range, noBSC_hist, BSC_hist, particle, era, channel
):

    # minBin = np.where(noBSC_hist[1] >= fit_range[0])[0][0]
    # maxBin = np.where(noBSC_hist[1] <= fit_range[1])[0][-1] + 1
    minBin, maxBin, masses[particle] = get_dynamic_fit_range(
        BSC_hist, search_range=Z_fit_range, fit_width=Z_fit_width
    )
    # print(
    #    f"For {region_1}{region_2}_mu1_pt_{muon1_cut1}_{muon1_cut2} set approximate peak {masses[particle]:.2f} GeV in fitting x-range: [{noBSC_hist[1][minBin]:.2f}, {noBSC_hist[1][maxBin]:.2f}] GeV"
    # )

    Z_GAMMA_BW = 2.4955 / 2

    voigtian_fixed_gamma = lambda m, A, mZ, sigma_res: voigtian(
        m, A, mZ, sigma_res, Z_GAMMA_BW
    )
    for width in range(Z_fit_width, 10):
        minBin, maxBin, masses[particle] = get_dynamic_fit_range(
            BSC_hist, search_range=Z_fit_range, fit_width=width
        )
        p0_voigt = [np.max(noBSC_hist[0][minBin:maxBin]), masses[particle], 2]
        p0_voigt_BSC = [np.max(BSC_hist[0][minBin:maxBin]), masses[particle], 2]

        try:
            popt, pcov = curve_fit(
                voigtian_fixed_gamma,
                noBSC_hist[1][minBin:maxBin],
                noBSC_hist[0][minBin:maxBin],
                p0=p0_voigt,
                maxfev=5000,
            )
            popt = np.insert(popt, 3, Z_GAMMA_BW)
            pcov_temp = np.insert(pcov, 3, 0, axis=1)
            pcov = np.insert(pcov_temp, 3, 0, axis=0)

            poptBSC, pcovBSC = curve_fit(
                voigtian_fixed_gamma,
                BSC_hist[1][minBin:maxBin],
                BSC_hist[0][minBin:maxBin],
                p0=p0_voigt_BSC,
                maxfev=5000,
            )
            poptBSC = np.insert(poptBSC, 3, Z_GAMMA_BW)
            pcov_tempBSC = np.insert(pcovBSC, 3, 0, axis=1)
            pcovBSC = np.insert(pcov_tempBSC, 3, 0, axis=0)

            print(f"Fit Voigtian successfully with width = {width} GeV.")
            final_fitting_width = width
            break

        except RuntimeError:
            print(f"Fit failed for width = {width} GeV. Trying next width...")
            continue

    perr = np.sqrt(np.diag(pcov))
    perrBSC = np.sqrt(np.diag(pcovBSC))

    noBSC_sigma = calculate_effective_sigma_from_voigt(popt)
    noBSC_res = noBSC_sigma / popt[1]
    noBSC_res_err = noBSC_res * np.sqrt(
        (perr[1] / popt[1]) ** 2 + (perr[2] / popt[2]) ** 2
    )  ### not right!
    BSC_sigma = calculate_effective_sigma_from_voigt(poptBSC)
    BSC_res = BSC_sigma / poptBSC[1]
    BSC_res_err = BSC_res * np.sqrt(
        (perrBSC[1] / poptBSC[1]) ** 2 + (perrBSC[2] / poptBSC[2]) ** 2
    )
    return (
        BSC_sigma,
        poptBSC[1],
        poptBSC[2],
        poptBSC[3],
        BSC_res,
        BSC_res_err,
        final_fitting_width,
    )


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
    use_puweight,
    lumi_rescale=False,
):
    if not use_puweight:
        variables.append("pileup_weight")

    mass_sigma_bin_L = []
    mass_sigma_bin_R = []
    measure_sigmas = []
    median_values = []

    print(f"start calculating {era} {channel} {csv_label[variables[0]]}!")

    # For 2024 data there is not simulations yet!!!
    # so in the case we re escale the luminosity
    era_reweight = 1

    for i in range(len(mass_sigma_bin) - 1):

        with ur.open(
            f"/eos/home-y/yulou/Fnal-hmm/hmm-tuples/EVE_pt_eta/{root_dir}/{channel}_"
            + era
            + "_skim.root:tree_output"
        ) as data_file:

            branches = data_file.arrays(library="np")

            ###################

            bool_list = (
                (branches[variables[0]] > mass_sigma_bin[i])
                & (branches[variables[0]] < mass_sigma_bin[i + 1])
                & (branches["diMuon_mass"] > 75)
                & (branches["diMuon_mass"] < 105)
            )

            for variable in [variables[0], "diMuon_mass", "diMuon_bsConstrainedMass"]:
                branches[variable] = branches[variable][bool_list]

            branches["weight"] = branches["weight"][bool_list]

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

            ############## for measured fitting
            histograms_list = []
            for var in ["diMuon_mass", "diMuon_bsConstrainedMass"]:
                histogram, bins = np.histogram(
                    branches[var],
                    bins=160,
                    range=Z_range,
                )

                histograms_list.append([histogram, bins])
                # labels.append(particle + "_" + var + "_" + era)
            (
                BSC_mass_sigma,
                BSC_mass_mu,
                BSC_voi_sigma,
                BSC_voi_gamma,
                BSC_res,
                BSC_res_err,
                final_fitting_width,
            ) = plot_diMuon_comp_and_fit(
                Z_fit_range,
                Z_range,
                histograms_list[0],
                histograms_list[1],
                "Z",
                era,
                channel,
            )
            print(
                f"For mass_sigma_region {mass_sigma_bin[i]} - {mass_sigma_bin[i+1]} Measured: {BSC_voi_sigma:.4f}"
            )

            print(
                f"For mass_sigma_region {mass_sigma_bin[i]} - {mass_sigma_bin[i+1]} Median: {median_value:.4f}"
            )

            ##############

            mass_sigma_bin_L.append(mass_sigma_bin[i])
            mass_sigma_bin_R.append(mass_sigma_bin[i + 1])
            median_values.append(median_value)
            measure_sigmas.append(BSC_voi_sigma)

    return mass_sigma_bin_L, mass_sigma_bin_R, median_values, measure_sigmas


def draw_diMuon_mass_multi_reso(
    variables,
    era,
    channel,
    use_puweight=True,
):
    plt.style.use(hep.style.CMS)

    print("****** PLOTTING *****")

    mass_sigma_bin_L, mass_sigma_bin_R, median_values, measure_sigmas = (
        get_histograms_from_tuple(era, channel, variables, use_puweight)
    )

    data_to_save = {
        "mass_sigma_bin_L": mass_sigma_bin_L,
        "mass_sigma_bin_R": mass_sigma_bin_R,
        f"median_value_{csv_label[variables[0]]}": median_values,
        "measure_sigmas": measure_sigmas,
    }

    output_directory = f"../plots_ole/{plot_version}/{channel}/{era}"
    df = pd.DataFrame(data_to_save)
    output_filename = f"{output_directory}binned_BCS_Z_mass_multi_median_{csv_label[variables[0]]}_0-3.csv"

    df.to_csv(output_filename, index=False, mode="w")

    return df


eras = ["2025"]
# eras = ["2022", "2022EE", "2023", "2023BPix"]
variableset = [
    # ["relative_diMuon_bsConstrainedMass_error"],
    # ["calibrated_diMuon_bsConstrainedMass_error"],
    ["calibrated_diMuon_bsConstrainedMass_sigma"],
    ["relative_diMuon_bsConstrainedMass_sigma"],
]


for era in eras:
    for variables in variableset:

        df_data = draw_diMuon_mass_multi_reso(
            variables,
            era,
            "Data",
            use_puweight=True,
        )
        '''
        df_DY = draw_diMuon_mass_multi_reso(
            variables,
            era,
            "DY",
            use_puweight=True,
        )
        '''
        
        x_label = f"median_value_{csv_label[variables[0]]}"
        y_measure_label = "measure_sigmas"
        min_val, max_val = mass_sigma_bin[0], mass_sigma_bin[-1]

        fig, ax = plt.subplots(figsize=(10, 10))

        ax.scatter(
            df_data[x_label],
            df_data[y_measure_label],
            color="blue",
            label="Data",
            s=20,
            zorder=5,
        )
        '''
        ax.scatter(
            df_DY[x_label],
            df_DY[y_measure_label],
            color="red",
            label="DY",
            s=20,
            zorder=5,
        )
        '''

        line_x = np.linspace(min_val, max_val, 101)

        ax.plot(line_x, line_x, color="black", linestyle="-", label="y = x")
        ax.plot(
            line_x, 1.1 * line_x, color="gray", linestyle="--", label="y = 1.1x / 0.9x"
        )
        ax.plot(line_x, 0.9 * line_x, color="gray", linestyle="--")

        ax.set_xlabel(
            f"Predicted Resolution (median_value_{csv_label[variables[0]]})",
            fontsize=14,
        )
        ax.set_ylabel("Measured Resolution (BSC_voi_sigma)", fontsize=14)
        ax.set_title(
            f"Measured vs. Predicted {csv_label[variables[0]]} - {era}", fontsize=16
        )
        ax.legend(fontsize=12)
        ax.grid(True, which="both", linestyle=":", linewidth=0.6)

        ax.set_xlim(min_val, max_val)
        ax.set_ylim(min_val, max_val)

        plot_name = f"../plots_ole/{plot_version}/{era}_reso_binned_predicted_measured_{csv_label[variables[0]]}_0-3.png"
        plt.savefig(plot_name, dpi=300, bbox_inches="tight")
        plt.close(fig)

        print(f"Plot saved to: {plot_name}\n")

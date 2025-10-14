import uproot as ur
import mplhep as hep
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.special import voigt_profile

merge_low_pt_eta = True
muon1_pt_cuts = [26.0, 45.0, 52.0, 62.0, 200.0]

eta_cuts = {"B": [0.0, 0.9], "O": [0.9, 1.8], "E": [1.8, 2.4]}


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

y_axis_max_range = {
    "diMuon_mass_full_range": 10e8,
}

signal_sources = [
    "ggH",
    "VBF",
    "ttH",
]

signal_colors = {"ggH": "red", "VBF": "blue", "ttH": "lime"}


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


variables = ["diMuon_mass", "diMuon_bsConstrainedMass"]
Z_range = [80, 100]
H_range = [115, 135]
Z_fit_range = [89, 93]  ## make sense? use [peak-2, peak+2]
Z_fit_width = 4  ## max width is 10GeV
H_fit_range = [122.5, 127.5]
Z_mass = 91
H_mass = 125
masses = {"Z": 91, "H": 125}


def gaussian(x, A, mean, std):
    return A * np.exp(-(((x - mean) / std) ** 2) / 2)


def voigtian(m, A, mZ, sigma_res, gamma_bw):
    # mZ = Z_mass + mu
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
    fit_range,
    mass_range,
    noBSC_hist,
    BSC_hist,
    particle,
    era,
    channel,
    region_1,
    region_2,
    muon1_cut1,
    muon1_cut2,
    plot_version,
    signal=None,
):
    if particle == "H" and signal == None:
        print("Must provide a signal to plot")

    # minBin = np.where(noBSC_hist[1] >= fit_range[0])[0][0]
    # maxBin = np.where(noBSC_hist[1] <= fit_range[1])[0][-1] + 1
    minBin, maxBin, masses[particle] = get_dynamic_fit_range(
        BSC_hist, search_range=Z_fit_range, fit_width=Z_fit_width
    )
    print(
        f"For {region_1}{region_2}_mu1_pt_{muon1_cut1}_{muon1_cut2} set approximate peak {masses[particle]:.2f} GeV in fitting x-range: [{noBSC_hist[1][minBin]:.2f}, {noBSC_hist[1][maxBin]:.2f}] GeV"
    )

    ### Voigtian fitting

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

    fig, axs = get_canvas(True)
    if particle == "Z":
        ifMCorData = "Data"
    else:
        ifMCorData = signal + " MC"

    hep.histplot(
        noBSC_hist[0],
        noBSC_hist[1],
        label=ifMCorData
        + " no BSC "
        + "sigma: {:.6f}, mu: {:.6f}".format(noBSC_sigma, popt[1]),
        ax=axs[0],
    )
    hep.histplot(
        BSC_hist[0],
        BSC_hist[1],
        label=ifMCorData
        + " BSC "
        + "sigma: {:.6f}, mu: {:.6f}".format(BSC_sigma, poptBSC[1]),
        ax=axs[0],
    )

    hep.cms.label(
        data="True",
        label="",  # if use_puweight else "No pu weight",
        year=era,
        com="13.6",
        lumi=luminosity[era],
        ax=axs[0],
    )

    axs[0].plot(
        noBSC_hist[1][minBin:maxBin],
        voigtian(noBSC_hist[1][minBin:maxBin], popt[0], popt[1], popt[2], popt[3]),
        label="noBSC $\sigma / \mu $: {:.6f} $\pm$ {:.6f}".format(
            noBSC_res, noBSC_res_err
        ),
    )
    axs[0].plot(
        noBSC_hist[1][minBin:maxBin],
        voigtian(
            BSC_hist[1][minBin:maxBin],
            poptBSC[0],
            poptBSC[1],
            poptBSC[2],
            poptBSC[3],
        ),
        label="BSC $\sigma / \mu $: {:.6f} $\pm$ {:.6f}".format(BSC_res, BSC_res_err),
    )

    axs[0].set_ylabel("Events")
    axs[0].set_ylim(0, 1.6 * np.max(noBSC_hist[0]))
    axs[0].set_xlim(mass_range[0], mass_range[1])
    axs[0].legend(frameon=False, loc="upper right", ncols=1)
    axs[0].tick_params(axis="x", which="both", bottom=True, top=True, labelbottom=False)

    axs[1].set_ylabel("BSC/noBSC", loc="center")
    axs[1].set_ylim(0.5, 1.5)
    axs[1].set_xlim(mass_range[0], mass_range[1])
    axs[1].set_xlabel(
        f"{region_1}{region_2}_mu1_pt_{muon1_cut1}_{muon1_cut2}  "
        + "m$_{\mu\mu}$ [GeV]"
    )

    ratio_hist, ratio_error = get_histograms_ratio(BSC_hist[0], noBSC_hist[0])
    hep.histplot(
        ratio_hist,
        noBSC_hist[1],
        yerr=ratio_error * 0,
        histtype="errorbar",
        # label="data",
        color="black",
        ax=axs[1],
    )

    output_directory = f"../plots/{plot_version}/{channel}/{era}/"

    if particle == "H":
        save_figure(
            fig, output_directory, particle + "_" + signal + "_" + era + "_reso"
        )
    else:
        save_figure(
            fig,
            output_directory,
            particle
            + "_"
            + f"{region_1}{region_2}_mu1_pt_{muon1_cut1}_{muon1_cut2}"
            + "_reso",
        )
    plt.close()

    return (
        BSC_sigma,
        poptBSC[1],
        poptBSC[2],
        poptBSC[3],
        BSC_res,
        BSC_res_err,
        final_fitting_width,
    )


def draw_diMuon_mass_peak_EVE(
    particle, era, channel, plot_version, root_dir, use_puweight=True
):
    plt.style.use(hep.style.CMS)

    print("*" * len("****** PLOTTING " + particle + " peak for " + era + " *****"))
    print("****** PLOTTING " + particle + " peak for " + era + " *****")
    print("*" * len("****** PLOTTING " + particle + " peak for " + era + " *****"))

    if particle == "Z":
        mass_range = Z_range
        fit_range = Z_fit_range
        histograms_list = []
        # labels = []

        results_data = []

        if merge_low_pt_eta == True:
            for region_2, eta_range_2 in eta_cuts.items():
                histograms_list = []
                all_data_for_current_group = {var: [] for var in variables}
                for region_1, eta_range_1 in eta_cuts.items():
                    category_name = f"{region_1}{region_2}_mu1_pt_{muon1_pt_cuts[0]}_{muon1_pt_cuts[1]}"
                    tree_name = f"tree_EVE_{category_name}"
                    with ur.open(
                        root_dir + channel + "_" + era + "_skim.root:" + tree_name
                    ) as data_file:
                        branches = data_file.arrays(variables, library="np")
                        for var in variables:
                            all_data_for_current_group[var].append(branches[var])

                for var in variables:
                    combined_data = np.concatenate(all_data_for_current_group[var])
                    histogram, bins = np.histogram(
                        combined_data,
                        bins=160,
                        range=Z_range,
                    )

                    histograms_list.append([histogram, bins])
                (
                    BSC_mass_sigma,
                    BSC_mass_mu,
                    BSC_voi_sigma,
                    BSC_voi_gamma,
                    BSC_res,
                    BSC_res_err,
                    final_fitting_width,
                ) = plot_diMuon_comp_and_fit(
                    fit_range,
                    mass_range,
                    histograms_list[0],
                    histograms_list[1],
                    particle,
                    era,
                    channel,
                    "B+O+E_",
                    region_2,
                    muon1_pt_cuts[0],
                    muon1_pt_cuts[1],
                    plot_version,
                )
                result_row = {
                    "muon1_pt_cut_low": muon1_pt_cuts[0],
                    "muon1_pt_cut_high": muon1_pt_cuts[1],
                    "region_1": "B+O+E",
                    "region_2": region_2,
                    "BSC_mass_mu": BSC_mass_mu,
                    "BSC_mass_sigma": BSC_mass_sigma,
                    "BSC_voi_sigma": BSC_voi_sigma,
                    "BSC_voi_gamma": BSC_voi_gamma,
                    "BSC_res": BSC_res,
                    "BSC_res_err": BSC_res_err,
                    "fitting_width": final_fitting_width,
                }
                results_data.append(result_row)

            start_muon_pt = 1  # where muon pt range for different eta combination start
        else:
            start_muon_pt = 0

        for i in range(start_muon_pt, len(muon1_pt_cuts) - 1):
            for region_1, eta_range_1 in eta_cuts.items():
                for region_2, eta_range_2 in eta_cuts.items():

                    histograms_list = []
                    muon1_cut1, muon1_cut2 = muon1_pt_cuts[i], muon1_pt_cuts[i + 1]

                    category_name = f"{region_1}{region_2}_mu1_pt_{muon1_pt_cuts[i]}_{muon1_pt_cuts[i+1]}"
                    tree_name = f"tree_EVE_{category_name}"
                    with ur.open(
                        root_dir + channel + "_" + era + "_skim.root:" + tree_name
                    ) as data_file:
                        branches = data_file.arrays(variables, library="np")
                        for var in variables:
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
                        fit_range,
                        mass_range,
                        histograms_list[0],
                        histograms_list[1],
                        particle,
                        era,
                        channel,
                        region_1,
                        region_2,
                        muon1_cut1,
                        muon1_cut2,
                        plot_version,
                    )

                    result_row = {
                        "muon1_pt_cut_low": muon1_cut1,
                        "muon1_pt_cut_high": muon1_cut2,
                        "region_1": region_1,
                        "region_2": region_2,
                        "BSC_mass_mu": BSC_mass_mu,
                        "BSC_mass_sigma": BSC_mass_sigma,
                        "BSC_voi_sigma": BSC_voi_sigma,
                        "BSC_voi_gamma": BSC_voi_gamma,
                        "BSC_res": BSC_res,
                        "BSC_res_err": BSC_res_err,
                        "fitting_width": final_fitting_width,
                    }
                    results_data.append(result_row)

        df = pd.DataFrame(results_data)

        filename = (
            f"../plots/{plot_version}/{channel}/{era}/BSC_Z_mass_reso_results.csv"
        )

        df.to_csv(filename, index=False)

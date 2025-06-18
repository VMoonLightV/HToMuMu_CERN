import uproot as ur
import mplhep as hep
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
#from scipy.stats import norm


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

signal_sources = [
    "ggH",
    "VBF",
    "ttH",
]

# signal_colors = {"ggH": "red", "VBF": "blue", "ttH": "lime"}

# def get_color_list(number_of_histograms):
    # colors = [
        # "#3f90da",
        # "#ffa90e",
        # "#bd1f01",
        # "#94a4a2",
        # "#832db6",
        # "#a96b59",
        # "#e76300",
        # "#b9ac70",
        # "#717581",
        # "#92dadd",
    # ]

    # color_list = []
    # for i in range(number_of_histograms):
        # color_list.append(colors[i])

    # return color_list

variables = ["diMuon_mass_full_range", "diMuon_bsConstrainedMass_full_range"]
Z_range = [80,100]
H_range = [115,135]
Z_fit_range = [89,93]
H_fit_range = [122.5,127.5]
Z_mass = 91
H_mass = 125
masses = {
    "Z":91,
    "H":125
}

def gaussian(x, A, mean, std):
        return A * np.exp(-((x - mean) / std)**2 / 2)

def plot_diMuon_comp_and_fit(fit_range, mass_range, noBSC_hist, BSC_hist, particle, era, signal=None):
    if (particle == "H" and signal==None):
        print("Must provide a signal to plot")

    bin_centers = (noBSC_hist[1][:-1] + noBSC_hist[1][1:]) / 2
    minBin = np.where(noBSC_hist[1] == fit_range[0])[0][0]
    maxBin = np.where(noBSC_hist[1] == fit_range[1])[0][0] + 1

    popt, pcov = curve_fit(gaussian, bin_centers[minBin:maxBin], noBSC_hist[0][minBin:maxBin], p0=[np.max(noBSC_hist[0][minBin:maxBin]), masses[particle], 1])
    poptBSC, pcovBSC = curve_fit(gaussian, bin_centers[minBin:maxBin], BSC_hist[0][minBin:maxBin], p0=[np.max(BSC_hist[0][minBin:maxBin]), masses[particle], 1])


    perr = np.sqrt(np.diag(pcov))
    perrBSC = np.sqrt(np.diag(pcovBSC))

    noBSC_res = popt[2]/popt[1]
    noBSC_res_err = noBSC_res*np.sqrt((perr[1]/popt[1])**2 + (perr[2]/popt[2])**2)
    BSC_res = poptBSC[2]/poptBSC[1]
    BSC_res_err = BSC_res*np.sqrt((perrBSC[1]/poptBSC[1])**2 + (perrBSC[2]/poptBSC[2])**2)

    fig, axs = get_canvas(True)
    if (particle=="Z"): ifMCorData = "Data"
    else: ifMCorData = signal + " MC"
    hep.histplot(noBSC_hist, label = ifMCorData + " no BSC", ax=axs[0])
    hep.histplot(BSC_hist, label = ifMCorData + " BSC", ax=axs[0])

    hep.cms.label(
    data="True",
    label="", #if use_puweight else "No pu weight",
    year=era,
    com="13.6",
    lumi=luminosity[era],
    ax=axs[0],
    )

    #axs[0].plot(bin_centers[minBin:maxBin], gaussian(bin_centers[minBin:maxBin], popt[0], popt[1], popt[2]),
    #    label='noBSC $\mu$: {:.2f} $\sigma$: {:.2f} $\pm$ {:.2f}'.format(popt[1],popt[2], perr[2]))
    #axs[0].plot(bin_centers[minBin:maxBin], gaussian(bin_centers[minBin:maxBin], poptBSC[0], poptBSC[1], poptBSC[2]), 
    #    label='BSC $\mu$: {:.2f} $\sigma$: {:.2f} $\pm$ {:.2f}'.format(poptBSC[1],poptBSC[2], perrBSC[2]))

    axs[0].plot(bin_centers[minBin:maxBin], gaussian(bin_centers[minBin:maxBin], popt[0], popt[1], popt[2]),
        label='noBSC $\sigma / \mu $: {:.6f} $\pm$ {:.6f}'.format(noBSC_res, noBSC_res_err))
    axs[0].plot(bin_centers[minBin:maxBin], gaussian(bin_centers[minBin:maxBin], poptBSC[0], poptBSC[1], poptBSC[2]), 
        label='BSC $\sigma / \mu $: {:.6f} $\pm$ {:.6f}'.format(BSC_res, BSC_res_err))

    axs[0].set_ylabel("Events")
    axs[0].set_ylim(0, 1.6 * np.max(noBSC_hist[0]))
    axs[0].set_xlim(mass_range[0], mass_range[1])
    axs[0].legend(frameon=False, loc="upper right", ncols=1)
    axs[0].tick_params(axis="x", which="both", bottom=True, top=True, labelbottom=False)

    axs[1].set_ylabel("BSC/noBSC", loc="center")
    axs[1].set_ylim(0.5, 1.5)
    axs[1].set_xlim(mass_range[0], mass_range[1])
    axs[1].set_xlabel("m$_{\mu\mu}$ [GeV]")

    ratio_hist, ratio_error = get_histograms_ratio(BSC_hist[0], noBSC_hist[0])
    hep.histplot(
        ratio_hist,
        noBSC_hist[1],
        yerr=ratio_error*0,
        histtype="errorbar",
        #label="data",
        color="black",
        ax=axs[1],
    )

    output_directory = "../plots/resolution/" + era + "/"

    if(particle == "H"): 
        save_figure(fig, output_directory, particle + "_" + signal + "_" + era + "_reso")
    else: 
        save_figure(fig, output_directory, particle + "_" + era + "_reso")
    plt.close()


def draw_diMuon_mass_peak_comp(particle, era, use_puweight=True):
    plt.style.use(hep.style.CMS)

    print("*" * len("****** PLOTTING " + particle + " peak for " + era + " *****"))
    print("****** PLOTTING " + particle + " peak for " + era + " *****")
    print("*" * len("****** PLOTTING " + particle + " peak for " + era + " *****"))

    era_reweight = 1
    if era == "2024":
        era_reweight = 106.45/9.45

    if particle == "Z":
        mass_range = Z_range
        fit_range = Z_fit_range
        histograms_list = []
        #labels = []
        with ur.open("../root_io/histos/Data_" + era + "_histos.root") as data_file:
            for var in variables:
                histograms_list.append(data_file[var].to_numpy())
                #labels.append(particle + "_" + var + "_" + era)
        plot_diMuon_comp_and_fit(fit_range, mass_range, histograms_list[0], histograms_list[1], particle, era)

    if particle == "H":
        if era == "2024":
            print("There are no signal MC for 2024 yet")
            return
        mass_range = H_range
        fit_range = H_fit_range
        for signal in signal_sources:
            histograms_list = []
            #labels = []
            with ur.open("../root_io/histos/" + signal + "_" + era + "_histos.root") as data_file:
                for var in variables:
                    histograms_list.append(data_file[var].to_numpy())
                    #labels.append(particle + "_" + signal + "_" + var + "_" + era)
            plot_diMuon_comp_and_fit(fit_range, mass_range, histograms_list[0], histograms_list[1], particle, era, signal)

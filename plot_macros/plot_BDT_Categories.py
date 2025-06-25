import uproot as ur
import mplhep as hep
import numpy as np
import math
import matplotlib.pyplot as plt
import sys

from utils.labels import luminosity, x_range, n_bins, x_labels
from utils.helper import get_canvas, save_figure, get_histograms_ratio

if len(sys.argv) < 3:
    print("Arguments missing: Channel_under_study, era, background_subset, signal_subset")
    exit()
channel_US = sys.argv[1]
era_input = sys.argv[2]

if "--only" in sys.argv:
    sys.argv.remove("--only")
    eras = [era_input]
elif era_input == "2022":
    eras = ["2022", "2022EE", "2022Combined"]
elif era_input == "2023":
    eras = ["2023", "2023BPix", "2023Combined"]
elif era_input == "Combined":
    eras = ["2022Combined", "2023Combined", "Combined"]
elif era_input == "All":
    eras = ["2022", "2022EE", "2023","2023BPix","Combined"]
else:
    print("Set era to be one of the available sets:")
    print(" > 2022, 2023, Combined, All")
    exit()

if len(sys.argv) == 3:
    background_subset = "Full"
    signal_subset = "NottH"
    print("Using default subsets:", background_subset, signal_subset)
elif len(sys.argv) == 5:
    background_subset = sys.argv[3]
    signal_subset = sys.argv[4]
else:
    print("Include subset of background AND signal only.")
    exit()

print("Channel under study: ", channel_US)
print("Eras: ", eras)
print("Background subset: ", background_subset)
print("Signal subset: ", signal_subset)

subset_title = "B" + background_subset + "_S" + signal_subset
BDTvar = "BDT_" + channel_US
BDTscore_path = "../root_io/skim/" + channel_US + "/BDT_score/"
N_max_iterations = 1 if channel_US == "ggH" else 2

def find_bdt_categories(era, bdt_categories, bdf_cut_max=1, iteration=0):
    # print("BDF Max Cut: ", bdf_cut_max)
    plt.style.use(hep.style.CMS)
    with ur.open(
        BDTscore_path + "background_" + era + "_skim_" + subset_title + ".root:tree_output"
    ) as file:
        bkg_branches = file.arrays(
            [BDTvar, "weight_no_lumi", "diMuon_mass"], library="np"
        )
    with ur.open(
        BDTscore_path + "signal_" + era + "_skim_" + subset_title + ".root:tree_output"
    ) as file:
        signal_branches = file.arrays(
            [BDTvar, "weight_no_lumi", "diMuon_mass"], library="np"
        )

    signal = []
    bkg_sqrt = []
    significance = []
    bdf_cut_min = 0.0
    # bdf_cut_max = 1.0
    cut_step = bdf_cut_max / 60
    if iteration == 0:
        cut_step = bdf_cut_max / 130
    bins = []
    while bdf_cut_min < bdf_cut_max:
        bkg_bool_list = (
            (bkg_branches["diMuon_mass"] > 121)
            & (bkg_branches["diMuon_mass"] < 129)
            & (bkg_branches[BDTvar] > bdf_cut_min)
            & (bkg_branches[BDTvar] < bdf_cut_max)
        )
        signal_bool_list = (
            (signal_branches["diMuon_mass"] > 121)
            & (signal_branches["diMuon_mass"] < 129)
            & (signal_branches[BDTvar] > bdf_cut_min)
            & (signal_branches[BDTvar] < bdf_cut_max)
        )

        signal_events = np.sum(
            float(luminosity[era]) * signal_branches["weight_no_lumi"][signal_bool_list]
        )
        bkg_events = np.sum(
            float(luminosity[era]) * bkg_branches["weight_no_lumi"][bkg_bool_list]
        )
        # print("signal = ", signal_events)
        # print("bkg = ", bkg_events)
        # print("S/sqrt(bkg) = ", signal_events/ math.sqrt(bkg_events))
        # print("min cut= ", bdf_cut_min)
        # print("max cut= ", bdf_cut_max)
        signal.append(signal_events)
        bkg_sqrt.append(math.sqrt(bkg_events))
        if bkg_events <= 0:
            break
        bins.append(bdf_cut_min)
        significance.append(signal_events / math.sqrt(bkg_events))

        bdf_cut_min += cut_step

    fig, ax = get_canvas()

    ax.errorbar(
        bins,
        significance,
        # ey,
        marker="o",
        linestyle="",
        markerfacecolor="black",
        color="black",
        markersize=5,
        # label=labelList[j],
    )

    # hep.cms.label(
    # data="True", label="", year=era, com="13.6", lumi=luminosity[era], ax=ax
    # )
    hep.cms.label(data="True", ax=ax, com="13.6")

    max_height = max(significance)
    best_cut = bins[significance.index(max(significance))]
    print("MAX significance: ", max(significance))
    ax.axvline(
        x=best_cut,
        # ymin=0.0,
        # ymax=max_height,
        color="red",
        linestyle="--",
        alpha=0.5,
    )

    # print("BDT > ", best_cut)
    # ax.set_yscale("log")
    # ax.set_ylim(
    # 0.001,
    # 10 * max_height,
    # )
    ax.set_ylim(0.0, 1.3 * max_height)
    ax.set_xlim(bins[0], bins[-1])
    ax.set_ylabel(r"S/$\sqrt{B}$", loc="center")
    # ax.legend(frameon=False, loc="upper right")
    ax.set_xlabel("BTD Cut")

    output_directory = "../plots/" + channel_US + "_category/BDT_categories/cuts/"
    save_name = "BDT_cuts_" + era + "_Cat" + str(iteration) + "_" + subset_title
    save_figure(fig, output_directory, save_name)

    bdt_categories.append(round(best_cut, 3))
    # if max(significance) > 0.05:
    if iteration < N_max_iterations:
        find_bdt_categories(era, bdt_categories, best_cut, iteration + 1)


def draw_bdt_categories(era):
    plt.style.use(hep.style.CMS)
    bdt_categories = []
    find_bdt_categories(era, bdt_categories)
    bdt_categories.append(0.0)
    bdt_categories.reverse()
    bdt_categories.append(1.0)

    print("Era: ", era)
    print("Categories: ", bdt_categories)

    with ur.open(
        BDTscore_path + "background_" + era + "_skim_" + subset_title + ".root:tree_output"
    ) as file:
        bkg_branches = file.arrays(
            [BDTvar, "weight_no_lumi", "diMuon_mass"], library="np"
        )
        bkg_hist, bkg_bins = np.histogram(
            bkg_branches[BDTvar],
            bins=n_bins[BDTvar],
            range=x_range[BDTvar],
            weights=float(luminosity[era]) * bkg_branches["weight_no_lumi"],
        )

    with ur.open(
        BDTscore_path + "signal_" + era + "_skim_" + subset_title + ".root:tree_output"
    ) as file:
        signal_branches = file.arrays(
            [BDTvar, "weight_no_lumi", "diMuon_mass"], library="np"
        )
        signal_hist, signal_bins = np.histogram(
            signal_branches[BDTvar],
            bins=n_bins[BDTvar],
            range=x_range[BDTvar],
            weights=float(luminosity[era]) * signal_branches["weight_no_lumi"],
        )
    fig, axs = get_canvas(True)

    hep.histplot(
        bkg_hist / np.sum(bkg_hist),
        bkg_bins,
        label="Background",
        ax=axs[0],
        stack=True,
        linewidth=2,
        color="red",
    )

    hep.histplot(
        signal_hist / np.sum(signal_hist),
        signal_bins,
        label="Signal (" + channel_US + ")",
        color="blue",
        linewidth=2,
        ax=axs[0],
    )

    hep.cms.label(
        data="True",
        label="",
        # year=era,
        com="13.6",
        # lumi=luminosity[era],
        ax=axs[0],
    )

    # max_height = max(
    # np.max(signal_hist / np.sum(signal_hist)), np.max(bkg_hist / np.sum(bkg_hist))
    # )

    # axs[0].set_yscale("log")
    # axs[0].set_ylim(
    # 0.001,
    # 10 * max_height,
    # )
    axs[0].set_ylim(
        0.0,
        1.3
        * max(
            np.max(signal_hist / np.sum(signal_hist)),
            np.max(bkg_hist / np.sum(bkg_hist)),
        ),
    )
    axs[0].set_xlim(signal_bins[0], signal_bins[-1])
    axs[0].set_ylabel(r"Events/ Total events", loc="center")
    axs[0].legend(frameon=False, loc="upper right")

    signal = []
    bkg_sqrt = []

    for category in range(len(bdt_categories) - 1):
        if category != 0:
            axs[0].axvline(
                x=bdt_categories[category],
                # ymin=0.001,
                color="grey",
                linestyle="--",
                alpha=0.5,
            )
        bkg_bool_list = (
            (bkg_branches["diMuon_mass"] > 121)
            & (bkg_branches["diMuon_mass"] < 129)
            & (bkg_branches[BDTvar] > bdt_categories[category])
            & (bkg_branches[BDTvar] < bdt_categories[category + 1])
        )
        signal_bool_list = (
            (signal_branches["diMuon_mass"] > 121)
            & (signal_branches["diMuon_mass"] < 129)
            & (signal_branches[BDTvar] > bdt_categories[category])
            & (signal_branches[BDTvar] < bdt_categories[category + 1])
        )

        signal_events = np.sum(
            float(luminosity[era]) * signal_branches["weight_no_lumi"][signal_bool_list]
        )
        bkg_events = np.sum(
            float(luminosity[era]) * bkg_branches["weight_no_lumi"][bkg_bool_list]
        )
        signal.append(signal_events)
        bkg_sqrt.append(math.sqrt(bkg_events))

    ratio_hist, ratio_error = get_histograms_ratio(np.array(signal), np.array(bkg_sqrt))

    hep.histplot(
        ratio_hist,
        bdt_categories,
        yerr=ratio_error,
        xerr=True,
        histtype="errorbar",
        color="black",
        ax=axs[1],
    )

    print(ratio_hist)

    axs[1].set_ylabel(r"S/$\sqrt{B}$", loc="center")
    axs[1].set_ylim(0.0, 2.000)
    axs[1].set_xlim(signal_bins[0], signal_bins[-1])
    axs[1].set_xlabel(x_labels[BDTvar])

    output_directory = "../plots/" + channel_US + "_category/BDT_categories/"
    save_name = "BDT_output_" + era + "_" + subset_title
    save_figure(fig, output_directory, save_name)


for era in eras:
    draw_bdt_categories(era)
    # find_bdt_categories(era)

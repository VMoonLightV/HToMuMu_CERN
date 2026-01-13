import mplhep as hep
import numpy as np
import matplotlib.pyplot as plt
from utils.helper import get_canvas, save_figure
import sys

plt.style.use(hep.style.CMS)  # or ATLAS/LHCb2

if len(sys.argv) < 3:
    print("Arguments missing: Channel_under_study, era, background_subset, signal_subset")
    exit()
channel_US = sys.argv[1]
era_input = sys.argv[2]
comparation_input = sys.argv[3]


if len(sys.argv) == 4:
    background_subset = "Full"
    signal_subset = "NottH"
    print("Using default subsets:", background_subset, signal_subset)
elif len(sys.argv) == 6:
    background_subset = sys.argv[4]
    signal_subset = sys.argv[5]
else:
    print("Include subset of background AND signal only.")
    exit()

print("Channel under study: ", channel_US)
print("Eras: ", era_input)
print("Background subset: ", background_subset)
print("Signal subset: ", signal_subset)

colors = ["blue", "red", "lime", "black", "orange"]

comparation_list = [""]
if comparation_input == "mass_range":
    comparation_list = ["_M-115-135", "_M-110-150", "_M-100-180"]
elif comparation_input == "weight":
    comparation_list = ["_no-weight", "_XSxLumi","_XSxLumi+m_res"]
elif comparation_input == "standardization":
    comparation_list = ["_standardization","_XSxLumi+m_res"]
else:
    print("Plotting just nominal results")
if comparation_input != "Nominal":
    comparation_list.append("_runII")
subset_title = "B" + background_subset + "_S" + signal_subset

bdt_cuts = {"ggH" : [0.0, 0.19730769230769193, 0.4384615384615378, 1.0], "VBF": [0.0, 0.3114000000000005, 0.6228000000000008, 0.8650000000000007, 1.0]}
nominal = "_XSxLumi+m_res"
draw_bdt_cuts = False
log_x = False 
min_diff = []
bdt_cut_sig_eff = []
bdt_cut_bkg_eff = []
for i in range(len(bdt_cuts[channel_US])):
    min_diff.append(1)
    bdt_cut_sig_eff.append(1)
    bdt_cut_bkg_eff.append(1)

fig, ax = get_canvas()
for comparation, color in zip(comparation_list, colors):
    print("Plotting: ", comparation)
    fpr_list = []
    tpr_list = []
    file_path = "../python/xgboost/roc/" + channel_US +  "_" + era_input + "_" +\
                subset_title + "_roc" + comparation + ".txt"
    with open(file_path, "r") as file:
        for line in file:
            if comparation == "_runII":
                parts = line.strip().split(", ")
                fpr = float(parts[1])
                tpr = float(parts[0]) 
                fpr_list.append(fpr)
                tpr_list.append(tpr)
                continue 

            parts = line.strip().split(",")
            fpr = float(parts[1].split("=")[1].strip())
            tpr = float(parts[2].split("=")[1].strip())

            fpr_list.append(fpr)
            tpr_list.append(tpr)

            if comparation != nominal:
                continue

            cut = float(parts[0].split("=")[1].strip())
            for i, bdt_cut in enumerate(bdt_cuts[channel_US]):
                if abs(bdt_cut - cut) > min_diff[i]:
                    continue

                bdt_cut_sig_eff[i] = tpr
                bdt_cut_bkg_eff[i] = fpr
                min_diff[i] = abs(bdt_cut - cut)
                print("i: ", i )
                print("bdt_cut: ", bdt_cut)
                print("cut: ", cut)



    #print("f: ", fpr_list)
    #print("t: ", fpr_list)
    label = (comparation.replace("_", "") if comparation != "" else "RunIII")
    ax.plot(tpr_list, fpr_list, label=label, color = color)
if draw_bdt_cuts:
    ax.errorbar(bdt_cut_sig_eff, bdt_cut_bkg_eff, markersize=5, marker="o", linestyle = "", label = "Categories", color = "darkorange")

# Show x-axis ticks every 0.1 units
plt.xticks(np.arange(0, 1.1, 0.1))
ax.set_ylabel(r"$\epsilon_{bkg}$")
ax.set_xlabel(r"$\epsilon_{sig}$")
ax.set_yscale("log")
ax.set_ylim(0.0001, 1)
ax.set_xlim(0, 1)
ax.legend(frameon=False, loc="lower right")
hep.cms.label(data="False", label=channel_US + ", " + subset_title,
              year=era_input, com="13.6", ax=ax)
if log_x:
    ax.set_xscale("log")
    ax.set_xlim(0.001, 1)
ax.grid()

file_name = "roc_space_" + channel_US + "_" + era_input + "_" + subset_title + "_" + comparation_input
if log_x:
    file_name = file_name + "_logx"
#if len(eras) == 1:
#    file_name += "ONLY"
save_figure(fig, "../plots/roc/" + channel_US + "_category/",
            file_name)

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

colors = ["blue", "red", "lime", "black", "orange"]
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

fig, ax = get_canvas()
for era, colors in zip(eras, colors):
    fpr_list = []
    tpr_list = []
    file_path = "../python/xgboost/roc/" + channel_US +  "_" + era + "_" +\
                subset_title + "_roc.txt"
    with open(file_path, "r") as file:
        for line in file:
            parts = line.strip().split(",")
            fpr = float(parts[1].split("=")[1].strip())
            tpr = float(parts[2].split("=")[1].strip())
            fpr_list.append(fpr)
            tpr_list.append(tpr)

    ax.plot(tpr_list, fpr_list, label=era)

# Show x-axis ticks every 0.1 units
plt.xticks(np.arange(0, 1.1, 0.1))
ax.set_ylabel(r"$\epsilon_{bkg}$")
ax.set_xlabel(r"$\epsilon_{sig}$")
ax.set_ylim(0.0001, 1)
ax.set_xlim(0, 1)
ax.legend(frameon=False, loc="lower right")
hep.cms.label(data="False", label=channel_US + ", " + subset_title,
              year=era_input, com="13.6", ax=ax)
ax.set_yscale("log")
ax.grid()

file_name = "roc_space_" + channel_US + "_" + era_input
if len(eras) == 1:
    file_name += "ONLY"
save_figure(fig, "../plots/" + channel_US + "_category/roc/",
            file_name + "_" + subset_title)

from utils.diMuon_mass_peak_EVE import draw_diMuon_mass_peak_EVE
import sys

plot_version = "EVE_resolution_voigtian_merge_lowPt"
root_dir = "/eos/home-y/yulou/Fnal-hmm/hmm-tuples/EVE_pt_eta/ZCR_75-105/"

eras = ["2025"]
# ["2022", "2022EE", "2023", "2023BPix"]
peak_particle = "Z"

for era in eras:
    for channel in ["Data"]:#, "DY"]:
        draw_diMuon_mass_peak_EVE(peak_particle, era, channel, plot_version, root_dir)

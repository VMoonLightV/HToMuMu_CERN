from utils.diMuon_mass_peak_EVE import draw_diMuon_mass_peak_EVE
import sys

if len(sys.argv) != 3:
    print("Include argument with which peak to compare (Z or H), and channel")
    exit()

peak_particle = sys.argv[1]
if peak_particle != "H" and peak_particle != "Z":
    raise Exception("No valid particle peak (choose H or Z)")

channel = sys.argv[2]

eras = ["2022", "2022EE", "2023", "2023BPix"]
# eras = ["2022", "2022EE"]
# eras = ["2023", "2023BPix"]
# eras = ["2024"]

for era in eras:
    draw_diMuon_mass_peak_EVE(peak_particle, era, channel)
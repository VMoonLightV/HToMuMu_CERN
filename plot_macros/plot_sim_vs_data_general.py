from utils.sim_vs_data_general import draw_data_and_simul_and_ratio

# from utils.Count_effs import draw_data_and_simul_and_ratio
import sys

base_input_dir = "../root_io/tuples/"
calibrated_input_dir = "../root_io/tuples/EVE_pt_eta/EVE_resolution_calibrated_all_channel/"

cali_draw = False # this is for drawing calibrated variables after calibration

njet_arg = sys.argv[1]
region = sys.argv[2]

use_ggH = False  # if sys.argv[1] != "ggH" else True
use_VBF = False  # if sys.argv[1] != "VBF" else True

# ordered from bottom to top in the plot, so order it from lower to bigger cross section
background_sources = [
    "EWK",
    "DiBoson",
    "TT",
    "DY",
]

signal_sources = [
    "ggH",
    "VBF",
    "ttH",
]

# variables = ["diMuon_mass", "diMuon_mass_Z", "diMuon_bsConstrainedMass", "diMuon_bsConstrainedMass_Z"]
variables = [
    "diMuon_bsConstrainedPt",
    # "diMuon_rapidity",
    # "diMuon_mass",
    # "diMuon_mass_Z",
    #"n_jet",
]

eras = ["2022", "2022EE", "2023", "2023BPix"]  # ,"2024"]

if "ZCR" in region:
    variables += ["diMuon_bsConstrainedMass_Z"]
if "SR" in region:
    variables += ["diMuon_bsConstrainedMass"]

if njet_arg == "nobin":
    njet_group = ["nobin_"]
if njet_arg == "bin":
    njet_group = ["0", "1", "2"]


if cali_draw == False:
    for njet in njet_group:
        for era in eras:
            input_dir = f"{base_input_dir}{njet}jet/{region}/"
            for variable in variables:
                draw_data_and_simul_and_ratio(
                    input_dir,
                    variable,
                    era,
                    background_sources,
                    signal_sources,
                    njet,
                    region,
                    cali_draw,
                    use_ggH_category=use_ggH,
                    use_VBF_category=use_VBF,
                )

else:

    variables = [
        "relative_diMuon_bsConstrainedMass_error",
        "calibrated_diMuon_bsConstrainedMass_error",
        # "relative_diMuon_bsConstrainedMass_sigma",
        # "calibrated_diMuon_bsConstrainedMass_sigma",
        # "diMuon_bsConstrainedPt",
        # "diMuon_bsConstrainedMass",
        # "diMuon_rapidity",
    ]
    region = "ZCR_75-105_calibrated_all_channel"

    for njet in njet_group:
        for era in eras:
            input_dir = "../root_io/tuples/EVE_pt_eta/ZCR_75-105_calibrated_all_channel/"
            
            for variable in variables:
                draw_data_and_simul_and_ratio(
                    input_dir,
                    variable,
                    era,
                    background_sources,
                    signal_sources,
                    njet,
                    region,
                    cali_draw,
                    use_ggH_category=use_ggH,
                    use_VBF_category=use_VBF,
                )

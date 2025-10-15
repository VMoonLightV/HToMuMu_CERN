from utils.data_vs_MC_2025 import draw_data_and_simul_and_ratio
import sys

# For quick test: plot 2025 data VS DY+TT, normalization has been done

base_input_dir = "/eos/home-y/yulou/Fnal-hmm/root_io/tuples/"

njet_arg = "nobin"
region = "All"

use_ggH = False  # if sys.argv[1] != "ggH" else True
use_VBF = False  # if sys.argv[1] != "VBF" else True

# ordered from bottom to top in the plot, so order it from lower to bigger cross section
background_sources = [
    #"EWK",
    #"DiBoson",
    "TT",
    "DY",
]

signal_sources = [
    #"ggH",
    #"VBF",
    #"ttH",
]


# eras = ["2022", "2022EE", "2023", "2023BPix"]  
# ,"2024"]
eras = ["2024"]  # ,"2024"]

if njet_arg == "nobin":
    njet_group = ["nobin_"]
if njet_arg == "bin":
    njet_group = ["0", "1", "2"]


variables = [
        #"diMuon_bsConstrainedPt",
        #"diMuon_bsConstrainedMass_Z",
        #"diMuon_mass_Z",
        #"diMuon_pt",
        #"diMuon_rapidity",
        #"diMuon_eta",
        #"diMuon_phi",
        
        #"mu1_bsConstrainedPt",
        #"mu2_bsConstrainedPt",
        
        #"relative_diMuon_bsConstrainedMass_error",
        #"calibrated_diMuon_bsConstrainedMass_error",
        #"relative_diMuon_bsConstrainedMass_sigma",
        #"calibrated_diMuon_bsConstrainedMass_sigma",
        "rho",
        "PV"
    ]

for njet in njet_group:
        for era in eras:
            input_dir = "/eos/home-y/yulou/Fnal-hmm/hmm-tuples-2025/"
            for variable in variables:
                draw_data_and_simul_and_ratio(
                    input_dir,
                    variable,
                    era,
                    background_sources,
                    signal_sources,
                    njet,
                    region,
                    use_ggH_category=use_ggH,
                    use_VBF_category=use_VBF,
                )

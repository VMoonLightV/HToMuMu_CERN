from utils.diMuon_mass_multi_reso import draw_diMuon_mass_multi_reso

peak_particle = "Z"
root_dir = "/eos/home-y/yulou/Fnal-hmm/hmm-tuples/EVE_pt_eta/ZCR_75-105/"

cali_root_dir = "/eos/home-y/yulou/Fnal-hmm/hmm-tuples/EVE_pt_eta/ZCR_75-105_calibrated_all_channel/"

# eras = ["2022", "2022EE", "2023", "2023BPix"]  #
# eras = ["2022", "2022EE"]
# eras = ["2023", "2023BPix"]
eras = ["2025"]

variableset = [
    # ["relative_diMuon_bsConstrainedMass_error"],
    # ["calibrated_diMuon_bsConstrainedMass_error"],
     ["relative_diMuon_bsConstrainedMass_sigma"],
    #["calibrated_diMuon_bsConstrainedMass_sigma"],
]

for era in eras:
    for channel in ["Data"]:#, "DY"]:
        for i in range(4):
            for variables in variableset:
                if "cali" in variables[0]:
                    draw_cali_root = True
                    use_root_dir = cali_root_dir
                else:
                    draw_cali_root = False
                    use_root_dir = root_dir

                draw_diMuon_mass_multi_reso(
                    variables,
                    era,
                    channel,
                    i,
                    draw_cali_root,
                    use_root_dir,
                    use_puweight=True,
                )

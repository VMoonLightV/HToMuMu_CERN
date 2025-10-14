from utils.diMuon_mass_multi_reso import draw_diMuon_mass_multi_reso

plot_version = "EVE_resolution_voigtian_merge_lowPt"

peak_particle = "Z"
root_dir = "../root_io/tuples/EVE_pt_eta/ZCR_75-105/"

# if you have done the calibration step, you can draw the calibrated result together
cali_root_dir = "../root_io/tuples/EVE_pt_eta/ZCR_75-105_calibrated_all_channel/"

eras = ["2022", "2022EE", "2023", "2023BPix"]  #
# eras = ["2022", "2022EE"]
# eras = ["2023", "2023BPix"]

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

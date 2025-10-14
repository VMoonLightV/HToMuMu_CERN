import os
import uproot

# directory where you store your Tuples
base_input_directory = "/eos/home-y/yulou/Fnal-hmm/root_io/tuples/"
# directory where your output files are
output_directory = "/eos/home-y/yulou/Fnal-hmm/hmm-tuples/EVE_pt_eta/ZCR_75-105/"
os.makedirs(output_directory, exist_ok=True)

muon1_pt_cuts = [26.0, 45.0, 52.0, 62.0, 200.0]

eta_cuts = {"B": [0.0, 0.9], "O": [0.9, 1.8], "E": [1.8, 2.4]}

eras = ["2024"]
# "2022", "2022EE", "2023", "2023BPix",
background_datasets = [
    "DY",
    "TT",
    #"DiBoson",
    #"EWK",
]
signal_datasets = [
    #"ggH",
    #"VBF",
    #"ttH",
]


def split_tuples_by_category(input_file_name, output_file_name):

    with uproot.recreate(output_file_name) as file_output:

        print(f"[Info] Opening input file: {input_file_name}")
        branches = uproot.open(input_file_name)["tree_output"].arrays(library="np")
        print(f"[Info] Inital events: {len(branches['diMuon_bsConstrainedMass'])}")

        for i in range(len(muon1_pt_cuts) - 1):
            for region_1, eta_range_1 in eta_cuts.items():
                for region_2, eta_range_2 in eta_cuts.items():

                    cuts = []
                    selected_events = {}

                    cuts = (
                        (abs(branches["mu1_eta"]) > eta_range_1[0])
                        & (abs(branches["mu1_eta"]) < eta_range_1[1])
                        & (abs(branches["mu2_eta"]) > eta_range_2[0])
                        & (abs(branches["mu2_eta"]) < eta_range_2[1])
                        & (branches["mu1_bsConstrainedPt"] > muon1_pt_cuts[i])
                        & (branches["mu1_bsConstrainedPt"] < muon1_pt_cuts[i + 1])
                        & (branches["diMuon_bsConstrainedMass"] > 75)
                        & (branches["diMuon_bsConstrainedMass"] < 105)
                    )

                    category_name = f"{region_1}{region_2}_mu1_pt_{muon1_pt_cuts[i]}_{muon1_pt_cuts[i+1]}"
                    tree_name = f"tree_EVE_{category_name}"

                    selected_events = {
                        name: array[cuts] for name, array in branches.items()
                    }
                    print(
                        f"[Info] Final events in {category_name}: {len(selected_events['diMuon_bsConstrainedMass'])}"
                    )

                    ### add relative_dimuon_mass_sigma
                    rela_error = selected_events[
                        "relative_diMuon_bsConstrainedMass_error"
                    ]
                    mass = selected_events["diMuon_bsConstrainedMass"]
                    rela_sigma = rela_error * mass
                    selected_events["relative_diMuon_bsConstrainedMass_sigma"] = (
                        rela_sigma
                    )

                    file_output[tree_name] = selected_events

    print(f"[Done] Created: {output_file_name}")


if __name__ == "__main__":

    for era in eras:
        input_file_name = base_input_directory + "Data_" + era + "_tuples.root"
        output_file_name = output_directory + "Data_" + era + "_skim.root"
        #split_tuples_by_category(input_file_name, output_file_name)
        for dataset in signal_datasets:
            input_file_name = (
                base_input_directory + dataset + "_" + era + "_tuples.root"
            )
            output_file_name = output_directory + dataset + "_" + era + "_skim.root"
            split_tuples_by_category(input_file_name, output_file_name)
        for dataset in background_datasets:
            input_file_name = (
                base_input_directory + dataset + "_" + era + "_tuples.root"
            )
            output_file_name = output_directory + dataset + "_" + era + "_skim.root"
            split_tuples_by_category(input_file_name, output_file_name)

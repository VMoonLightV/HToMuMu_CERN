import pandas as pd

plot_version = "/eos/home-y/yulou/Fnal-hmm/plots_ole/EVE_resolution_voigtian_merge_lowPt"

eras = ["2025"]
# eras = ["2022", "2022EE", "2023", "2023BPix"]

for channel in ["Data", "DY"]:
    for era in eras:

        df1 = pd.read_csv(
            f"{plot_version}/{channel}/{era}/BCS_Z_mass_multi_median_rela_sigma.csv"
        )
        df2 = pd.read_csv(f"{plot_version}/{channel}/{era}/BSC_Z_mass_reso_results.csv")

        df = pd.concat([df1, df2], axis=1)

        columns_to_keep = [
            "muon1_pt_cut_low",
            "muon1_pt_cut_high",
            "region_1",
            "region_2",
            "median_value_rela_sigma",
            "BSC_voi_sigma",
            "calibration_factors",
        ]

        df["calibration_factors"] = df["BSC_voi_sigma"] / df["median_value_rela_sigma"]

        final_df = df.loc[:, columns_to_keep]

        print(final_df.head())

        csv_name = f"{plot_version}/{channel}/{era}/BSC_Z_mass_reso_factors.csv"

        final_df.to_csv(csv_name, index=False)

        print("\nsave EVE calibration factors in ", csv_name)

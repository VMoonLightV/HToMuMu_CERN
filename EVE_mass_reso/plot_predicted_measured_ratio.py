import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

plot_version = "EVE_resolution_voigtian_merge_lowPt"

eras = ["2022", "2022EE", "2023", "2023BPix"]

plot_sigma = True

if plot_sigma == False:
    x_rela_label = "median_value_rela_reso"
    x_cali_label = "median_value_cali_reso"
    y_measure_label = "BSC_res"  #

    min_val = 0
    max_val = 0.04

    for era in eras:
        print(f"--- Processing era: {era} ---")

        columns_to_keep = [
            "pt_range",
            "eta_category",
            x_rela_label,
            x_cali_label,
            y_measure_label,
        ]

        try:
            df_rela_data = pd.read_csv(
                f"../plots/{plot_version}/Data/{era}/BCS_Z_mass_multi_median_rela_reso.csv"
            )
            df_cali_data = pd.read_csv(
                f"../plots/{plot_version}/Data/{era}/BCS_Z_mass_multi_median_cali_reso.csv"
            )
            df_meas_data = pd.read_csv(
                f"../plots/{plot_version}/Data/{era}/BSC_Z_mass_reso_results.csv"
            )

            df_reso_data = df_cali_data.join(df_rela_data, rsuffix="_rela").join(
                df_meas_data, rsuffix="_meas"
            )
            df_data = df_reso_data.loc[:, columns_to_keep].copy()
            print(f"Loaded Data for {era}")

            df_rela_DY = pd.read_csv(
                f"../plots/{plot_version}/DY/{era}/BCS_Z_mass_multi_median_rela_reso.csv"
            )
            df_cali_DY = pd.read_csv(
                f"../plots/{plot_version}/DY/{era}/BCS_Z_mass_multi_median_cali_reso.csv"
            )
            df_meas_DY = pd.read_csv(
                f"../plots/{plot_version}/DY/{era}/BSC_Z_mass_reso_results.csv"
            )

            df_reso_DY = df_cali_DY.join(df_rela_DY, rsuffix="_rela").join(
                df_meas_DY, rsuffix="_meas"
            )
            df_DY = df_reso_DY.loc[:, columns_to_keep].copy()
            print(f"Loaded DY for {era}")

        except FileNotFoundError as e:
            print(f"Could not find file for era {era}. Skipping... Error: {e}")
            continue

        fig, ax = plt.subplots(figsize=(10, 10))

        ax.scatter(
            df_data[x_rela_label],
            df_data[y_measure_label],
            color="blue",
            label="Data",
            s=20,
            zorder=5,
        )
        ax.scatter(
            df_DY[x_rela_label],
            df_DY[y_measure_label],
            color="red",
            label="DY",
            s=20,
            zorder=5,
        )

        line_x = np.linspace(min_val, max_val, 101)

        ax.plot(line_x, line_x, color="black", linestyle="-", label="y = x")
        ax.plot(
            line_x, 1.1 * line_x, color="gray", linestyle="--", label="y = 1.1x / 0.9x"
        )
        ax.plot(line_x, 0.9 * line_x, color="gray", linestyle="--")

        ax.set_xlabel("Predicted Resolution (median_value_rela_reso)", fontsize=14)
        ax.set_ylabel("Measured Resolution (BSC_mass_reso)", fontsize=14)
        ax.set_title(f"Measured vs. Predicted Resolution - {era}", fontsize=16)
        ax.legend(fontsize=12)
        ax.grid(True, which="both", linestyle=":", linewidth=0.6)

        ax.set_xlim(min_val, max_val)
        ax.set_ylim(min_val, max_val)

        plot_name = (
            f"../plots/{plot_version}/{era}_nobinned_predicted_measured_rela_reso.png"
        )
        plt.savefig(plot_name, dpi=300, bbox_inches="tight")
        plt.close(fig)

        print(f"Plot saved to: {plot_name}\n")

        fig, ax = plt.subplots(figsize=(10, 10))

        ax.scatter(
            df_data[x_cali_label],
            df_data[y_measure_label],
            color="blue",
            label="Data",
            s=20,
            zorder=5,
        )
        ax.scatter(
            df_DY[x_cali_label],
            df_DY[y_measure_label],
            color="red",
            label="DY",
            s=20,
            zorder=5,
        )

        ax.plot(line_x, line_x, color="black", linestyle="-", label="y = x")
        ax.plot(
            line_x, 1.1 * line_x, color="gray", linestyle="--", label="y = 1.1x / 0.9x"
        )
        ax.plot(line_x, 0.9 * line_x, color="gray", linestyle="--")

        ax.set_xlabel(
            "Calibrated Predicted Resolution (median_value_cali_reso)", fontsize=14
        )
        ax.set_ylabel("Measured Resolution (BSC_mass_reso)", fontsize=14)
        ax.set_title(f"Measured vs. Predicted Resolution - {era}", fontsize=16)
        ax.legend(fontsize=12)
        ax.grid(True, which="both", linestyle=":", linewidth=0.6)

        ax.set_xlim(min_val, max_val)
        ax.set_ylim(min_val, max_val)

        plot_name = (
            f"../plots/{plot_version}/{era}_nobinned_predicted_measured_cali_reso.png"
        )
        plt.savefig(plot_name, dpi=300, bbox_inches="tight")
        plt.close(fig)

        print(f"Plot saved to: {plot_name}\n")

    print("All eras processed.")


else:
    x_rela_label = "median_value_rela_sigma"
    x_cali_label = "median_value_cali_sigma"
    y_measure_label = "BSC_voi_sigma"

    min_val = 0
    max_val = 4  # 5

    for era in eras:
        print(f"--- Processing era: {era} ---")

        columns_to_keep = [
            "pt_range",
            "eta_category",
            x_rela_label,
            x_cali_label,
            y_measure_label,
        ]

        try:
            df_rela_data = pd.read_csv(
                f"../plots/{plot_version}/Data/{era}/BCS_Z_mass_multi_median_rela_sigma.csv"
            )
            df_cali_data = pd.read_csv(
                f"../plots/{plot_version}/Data/{era}/BCS_Z_mass_multi_median_cali_sigma.csv"
            )
            df_meas_data = pd.read_csv(
                f"../plots/{plot_version}/Data/{era}/BSC_Z_mass_reso_results.csv"
            )

            df_reso_data = df_cali_data.join(df_rela_data, rsuffix="_rela").join(
                df_meas_data, rsuffix="_meas"
            )
            df_data = df_reso_data.loc[:, columns_to_keep].copy()
            print(f"Loaded Data for {era}")

            df_rela_DY = pd.read_csv(
                f"../plots/{plot_version}/DY/{era}/BCS_Z_mass_multi_median_rela_sigma.csv"
            )
            df_cali_DY = pd.read_csv(
                f"../plots/{plot_version}/DY/{era}/BCS_Z_mass_multi_median_cali_sigma.csv"
            )
            df_meas_DY = pd.read_csv(
                f"../plots/{plot_version}/DY/{era}/BSC_Z_mass_reso_results.csv"
            )

            df_reso_DY = df_cali_DY.join(df_rela_DY, rsuffix="_rela").join(
                df_meas_DY, rsuffix="_meas"
            )
            df_DY = df_reso_DY.loc[:, columns_to_keep].copy()
            print(f"Loaded DY for {era}")

        except FileNotFoundError as e:
            print(f"Could not find file for era {era}. Skipping... Error: {e}")
            continue

        fig, ax = plt.subplots(figsize=(10, 10))

        ax.scatter(
            df_data[x_rela_label],
            df_data[y_measure_label],
            color="blue",
            label="Data",
            s=20,
            zorder=5,
        )
        ax.scatter(
            df_DY[x_rela_label],
            df_DY[y_measure_label],
            color="red",
            label="DY",
            s=20,
            zorder=5,
        )

        line_x = np.linspace(min_val, max_val, 101)

        ax.plot(line_x, line_x, color="black", linestyle="-", label="y = x")
        ax.plot(
            line_x, 1.1 * line_x, color="gray", linestyle="--", label="y = 1.1x / 0.9x"
        )
        ax.plot(line_x, 0.9 * line_x, color="gray", linestyle="--")

        ax.set_xlabel("Predicted Resolution (median_value_rela_sigma)", fontsize=14)
        ax.set_ylabel("Measured Resolution (BSC_mass_sigma)", fontsize=14)
        ax.set_title(f"Measured vs. Predicted Resolution - {era}", fontsize=16)
        ax.legend(fontsize=12)
        ax.grid(True, which="both", linestyle=":", linewidth=0.6)

        ax.set_xlim(min_val, max_val)
        ax.set_ylim(min_val, max_val)

        plot_name = (
            f"../plots/{plot_version}/{era}_nobinned_predicted_measured_rela_sigma.png"
        )
        plt.savefig(plot_name, dpi=300, bbox_inches="tight")
        plt.close(fig)

        print(f"Plot saved to: {plot_name}\n")

        fig, ax = plt.subplots(figsize=(10, 10))

        ax.scatter(
            df_data[x_cali_label],
            df_data[y_measure_label],
            color="blue",
            label="Data",
            s=20,
            zorder=5,
        )
        ax.scatter(
            df_DY[x_cali_label],
            df_DY[y_measure_label],
            color="red",
            label="DY",
            s=20,
            zorder=5,
        )

        ax.plot(line_x, line_x, color="black", linestyle="-", label="y = x")
        ax.plot(
            line_x, 1.1 * line_x, color="gray", linestyle="--", label="y = 1.1x / 0.9x"
        )
        ax.plot(line_x, 0.9 * line_x, color="gray", linestyle="--")

        ax.set_xlabel(
            "Calibrated Predicted Resolution (median_value_cali_sigma)", fontsize=14
        )
        ax.set_ylabel("Measured Resolution (BSC_mass_sigma)", fontsize=14)
        ax.set_title(f"Measured vs. Predicted Resolution - {era}", fontsize=16)
        ax.legend(fontsize=12)
        ax.grid(True, which="both", linestyle=":", linewidth=0.6)

        ax.set_xlim(min_val, max_val)
        ax.set_ylim(min_val, max_val)

        plot_name = (
            f"../plots/{plot_version}/{era}_nobinned_predicted_measured_cali_sigma.png"
        )
        plt.savefig(plot_name, dpi=300, bbox_inches="tight")
        plt.close(fig)

        print(f"Plot saved to: {plot_name}\n")

    print("All eras processed.")

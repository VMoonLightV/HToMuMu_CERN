#!/usr/bin/env python
# coding: utf-8
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_curve, roc_auc_score
import xgb_utils
import numpy as np
import pandas as pd
import mplhep as hep
import math
import pickle as pickle
import ROOT as root
import os
import shlex
import uproot
import sys

if len(sys.argv) < 3:
    print(
        "Arguments missing: Channel_under_study, era, background_subset, signal_subset"
    )
    exit()
channel_US = sys.argv[1]
era = sys.argv[2]
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
print("Era: ", era)
print("Background subset: ", background_subset)
print("Signal subset: ", signal_subset)


plt.style.use(hep.style.CMS)
root.gROOT.SetBatch(True)
root.gStyle.SetOptStat(0)
root.gStyle.SetOptFit(111)
root.gStyle.SetPaintTextFormat("2.1f")

luminosity = {
    "2022": 7.9804,
    "2022EE": 26.6717,
    "2022Combined": 34.6521,
    "2023": 17.794,
    "2023BPix": 9.451,
    "2023Combined": 27.245,
    # "Combined": 61.897,
    "Combined": 170.905,
}

draw_corr = False
variable_standatization = True
use_weight = False
use_weight_mass_res = True

subset_title = "B" + background_subset + "_S" + signal_subset

test_name = channel_US + "_" + era + "_" + subset_title
plotDir = "../../plots/xgboost/" + channel_US + "/" + subset_title + "/"
pwd = os.getcwd()
data_directory = "../../root_io/skim/" + channel_US + "/"
signal_file_name = data_directory + "signal_" + era + "_skim_" + signal_subset + ".root"
bkg_file_name = data_directory + "background_" + era + "_skim_" + background_subset + ".root"

os.system("mkdir -p " + plotDir)
os.system("mkdir -p " + plotDir + "training")
os.system("mkdir -p " + plotDir + "results")
os.system("mkdir -p " + plotDir + "scores")
os.system("mkdir -p " + plotDir + "variables")
os.system("mkdir -p models")
os.system("mkdir -p roc")
os.system("cp ../index.php " + plotDir)
os.system("cp ../index.php " + plotDir + "training/")
os.system("cp ../index.php " + plotDir + "results/")
os.system("cp ../index.php " + plotDir + "scores/")
os.system("cp ../index.php " + plotDir + "variables/")

variables = [
    ["diMuon_rapidity", "diMuon_rapidity", r"$y_{\mu\mu}$"],
    ["diMuon_pt", "diMuon_pt", r"$p_T^{\mu\mu}$ [GeV]"],
    ["mu1_pt_mass_ratio", "mu1_pt_mass_ratio", r"$p_T^{\mu 1}/m_{\mu\mu}$"],
    ["mu2_pt_mass_ratio", "mu2_pt_mass_ratio", r"$p_T^{\mu 2}/m_{\mu\mu}$"],
    ["mu1_eta", "mu1_eta", r"$\eta_{\mu 1}$"],
    ["mu2_eta", "mu2_eta", r"$\eta_{\mu 2}$"],
    ["phi_CS", "phi_CS", r"$\phi_{CS}$"],
    ["cos_theta_CS", "cos_theta_CS", r"$cos(\theta_{CS})$"],
    # # Jet variables
    ["n_jet", "n_jet", r"$N_{jets}$"],
    ["leading_jet_pt", "leading_jet_pt", r"$p_T^{j1}$"],
    ["leading_jet_eta", "leading_jet_eta", r"$\eta_{j1}$"],
    ["subleading_jet_pt", "subleading_jet_pt", r"$p_T^{j2}$ [GeV]"],
    ["diJet_mass", "diJet_mass", r"$m_{jj}$ [GeV]"],
    ["delta_eta_diJet", "delta_eta_diJet", r"$\Delta\eta_{jj}$"],
    ["delta_phi_diJet", "delta_phi_diJet", r"$\Delta\phi_{jj}$ [rad]"],
    ["z_zeppenfeld", "z_zeppenfeld", r"$Z^{*} Zeppendfeld$"],
    [
        "min_delta_eta_diMuon_jet",
        "min_delta_eta_diMuon_jet",
        r"min$|\Delta\eta_{\mu\mu,j}|$",
    ],
    [
        "min_delta_phi_diMuon_jet",
        "min_delta_phi_diMuon_jet",
        r"min$|\Delta\phi_{\mu\mu,j}|$ [rad]",
    ],
]
if channel_US == "VBF":
    variables += [
        # VBF sspecific variables
        ["pt_balance", "pt_balance", r"$R(p_T)$"],
        ["pt_centrality", "pt_centrality", r"$p_{T}-centrality$"],
        ["n_SoftJet_pt2", "n_SoftJet_pt2", r"$N_{2}^{soft}$"],
        ["HT", "HT", r"$H_{T}^{2}(soft)$"],
    ]
variables += [["diMuon_mass", "diMuon_mass", "diMuon_mass"]]
variables += [
    [
        "relative_diMuon_mass_error",
        "relative_diMuon_mass_error",
        "relative_diMuon_mass_error",
    ]
]
# Add weight at the end!
variables += [["weight", "weight", "weight"]]

print("number of variables", len(variables))

##Getting ROOT files into pandas


with uproot.open(signal_file_name) as file:
    df_signal = pd.DataFrame(
        file["tree_output"].arrays([row[0] for row in variables], library="np"),
    )

print("Signal data frame created")
with uproot.open(bkg_file_name) as file:
    df_bkg = pd.DataFrame(
        file["tree_output"].arrays([row[0] for row in variables], library="np"),
    )

bkg_events = df_bkg["weight"][(df_bkg["diMuon_mass"] > 121) & (df_bkg["diMuon_mass"] < 129)].sum()
signal_events = df_signal["weight"][(df_signal["diMuon_mass"] > 121) & (df_signal["diMuon_mass"] < 129)].sum()

####  weight Normalization
# print("weights : ", df_signal["weight"])
signal_weight_sum = df_signal["weight"].sum()
bkg_weight_sum = df_bkg["weight"].sum()
df_signal["weight"] = df_signal["weight"] * (bkg_weight_sum / signal_weight_sum)
# print("weight normalized: ", df_signal["weight"])

print(
    "[INFO]: S = "
    + str(signal_events)
    + "; B = "
    + str(bkg_events)
    + "; S/sqrt(B) = "
    + str(signal_events / math.sqrt(bkg_events))
)


print("Background data frame created")
##Getting a numpy array out of two pandas data frame

# getting a numpy array from two pandas data frames
x = np.concatenate([df_bkg.values, df_signal.values])
# creating numpy array for target variables
y = np.concatenate([np.zeros(len(df_bkg)), np.ones(len(df_signal))])

print("signal sample size: " + str(len(df_signal.values)))
print("bkg sample size: " + str(len(df_bkg.values)))




###plot correlation
if draw_corr:
    correlation_vars = variables[:-2]
    file_sig = root.TFile(signal_file_name)
    tree_sig = file_sig.Get("tree_output")
    file_bkg = root.TFile(bkg_file_name)
    tree_bkg = file_bkg.Get("tree_output")
    n_corr = len(correlation_vars)
    h2_corr_sig = root.TH2F(
        "h2_corr_sig", "h2_corr_sig", n_corr, 0, n_corr, n_corr, 0, n_corr
    )
    h2_corr_bkg = root.TH2F(
        "h2_corr_bkg", "h2_corr_bkg", n_corr, 0, n_corr, n_corr, 0, n_corr
    )

    for idx1 in range(n_corr):
        for idx2 in range(n_corr):
            tree_sig.Draw(correlation_vars[idx1][0] + ":" + correlation_vars[idx2][0] + ">>temp_sig")
            tree_bkg.Draw(correlation_vars[idx1][0] + ":" + correlation_vars[idx2][0] + ">>temp_bkg")
            sig_hist = root.gDirectory.Get("temp_sig")
            h2_corr_sig.SetBinContent(idx1 + 1, idx2 + 1, sig_hist.GetCorrelationFactor())
            bkg_hist = root.gDirectory.Get("temp_bkg")
            h2_corr_bkg.SetBinContent(idx1 + 1, idx2 + 1, bkg_hist.GetCorrelationFactor())
            root.gDirectory.Delete("temp_sig")
            root.gDirectory.Delete("temp_bkg")
            h2_corr_sig.GetZaxis().SetRangeUser(-1.0, 1.0)
            h2_corr_bkg.GetZaxis().SetRangeUser(-1.0, 1.0)
            for idx in range(n_corr):
                h2_corr_sig.GetXaxis().SetBinLabel(idx + 1, correlation_vars[idx][2])
                h2_corr_sig.GetYaxis().SetBinLabel(idx + 1, correlation_vars[idx][2])
                h2_corr_bkg.GetXaxis().SetBinLabel(idx + 1, correlation_vars[idx][2])
                h2_corr_bkg.GetYaxis().SetBinLabel(idx + 1, correlation_vars[idx][2])

    h2_corr_sig.LabelsOption("v", "X")
    h2_corr_bkg.LabelsOption("v", "X")
    my_canvas = root.TCanvas("my_canvas", "my_canvas", 200, 10, 900, 800)
    my_canvas.SetHighLightColor(2)
    my_canvas.SetFillColor(0)
    my_canvas.SetBorderMode(0)
    my_canvas.SetBorderSize(2)
    my_canvas.SetLeftMargin(0.12)
    my_canvas.SetRightMargin(0.12)
    my_canvas.SetBottomMargin(0.12)
    my_canvas.SetTopMargin(0.12)
    my_canvas.SetFrameBorderMode(0)
    my_canvas.SetFrameBorderMode(0)

    stops = np.array([0.00, 0.34, 0.61, 0.84, 1.00])
    red = np.array([0.50, 0.50, 1.00, 1.00, 1.00])
    green = np.array([0.50, 1.00, 1.00, 0.60, 0.50])
    blue = np.array([1.00, 1.00, 0.50, 0.40, 0.50])
    root.TColor.CreateGradientColorTable(len(stops), stops, red, green, blue, 255)
    root.gStyle.SetNumberContours(255)

    h2_corr_sig.Draw("COLZTEXT")
    h2_corr_sig.SetTitle("")
    my_canvas.SaveAs(plotDir + "variables/" + test_name + "_correlation_matrix_sig.png")
    h2_corr_bkg.Draw("COLZTEXT")
    h2_corr_bkg.SetTitle("")
    my_canvas.SaveAs(plotDir + "variables/" + test_name + "_correlation_matrix_bkg.png")
    my_canvas.SaveAs(plotDir + "variables/" + test_name + "_correlation_matrix_bkg.C")


# split data into train and test sets
seed = 7
test_size = 0.4
sample_size = 1.0
x_train_p, x_test_p, y_train, y_test = train_test_split(
    x,
    y,
    train_size=sample_size * (1 - test_size),
    test_size=sample_size * test_size,
    random_state=seed,
)

# x_train = x_train_p[:, :-1]
# x_test = x_test_p[:, :-1]
x_train = x_train_p[:, :-3]
x_test = x_test_p[:, :-3]
sample_weights_train = x_train_p[:, -1]
sample_weights_test = x_test_p[:, -1]

print("-inf position (by index):", np.isneginf(x_train)[np.isneginf(x_train)])
print("inf position (by index):", np.isinf(x_train)[np.isinf(x_train)])
print("nan position (by index):", np.isnan(x_train)[np.isnan(x_train)])
x_train[np.isneginf(x_train)] = np.nan
x_train[np.isinf(x_train)] = np.nan
x_train[np.isnan(x_train)] = 0.

print("x_train:", x_train)
mean_map = {}
std_map = {}
if variable_standatization:
    for i, var in enumerate(variables[:-3]):
        print("standarizing : ", var[0])
        print("Iterator : ", i)
        null_value = 0
        if var[0] in ["delta_phi_diJet", "pt_balance"]:
            null_value = -1

        mask_train = x_train[:,i] != null_value
        mask_test = x_test[:,i] != null_value
        mean_map[var[0]] = x_train[mask_train,i].mean()
        std_map[var[0]] = x_train[mask_train,i].std()
        print("[Info]: Train Sample Mean: ", mean_map[var[0]])
        print("[Info]: Train Sample std: ", std_map[var[0]])
        x_train[mask_train,i] = (x_train[mask_train,i] - mean_map[var[0]]) / std_map[var[0]]
        x_test[mask_test,i] = (x_test[mask_test,i] - mean_map[var[0]]) / std_map[var[0]]

print("x_train standaried:", x_train)
# fit model no training data
model = xgb.XGBClassifier(
    max_depth=3,
    learning_rate=0.1,
    n_estimators=400,
    verbosity=2,
    n_jobs=4,
    reg_lambda=1.0,
)

print("weights: ", sample_weights_train)
print("abs(weights): ", np.absolute(sample_weights_train[y_train == 1]))
print("abs(weights) mean: ", sample_weights_train[y_train == 1].mean())
print("relative_diMuon_mass_error: ", x_test_p[:, -2])
print("new error : ", np.absolute(sample_weights_train) / np.array(x_train_p[:, -2]))

if not use_weight and not use_weight_mass_res:
    print("[Info]: Training without weights")
    model.fit(x_train, y_train)
if use_weight:
    print("[Info]: Training with regular  weights")
    model.fit(x_train, y_train , sample_weight=np.absolute(sample_weights_train))
if use_weight_mass_res:
    print("[Info]: Training with mass_res weights")
    model.fit(x_train, y_train,
        sample_weight=np.absolute(sample_weights_train) / np.array(x_train_p[:, -2]),
    )

y_pred = model.predict_proba(x_test)[:, 1]

plt.figure(figsize=(8, 6))
plt.hist(y_pred, bins=50, color="skyblue", edgecolor="black")
plt.xlabel("y pred")
plt.ylabel("events")
plt.grid(True)

# Save the histogram to a file
plt.savefig(plotDir + "y_pred.png")  # Change filename and format as needed
plt.close()  # Close the fig

print("y_pred:", y_pred)
print("y_test:", y_test)
y_pred_train = model.predict_proba(x_train)[:, 1]
print("y_pred_train:", y_pred_train)
predictions = [round(value) for value in y_pred]
# evaluate predictions
accuracy = accuracy_score(y_test, predictions)
print("Accuracy: %.2f%%" % (accuracy * 100.0))

AUC = roc_auc_score(y_test, y_pred)
print("AUC: " + str(AUC))
# get roc curve
# roc = roc_curve(y_test, y_pred)
diMuon_mass_test = x_test_p[:, -3]
print(
    "diMuon_mass: ",
    diMuon_mass_test[(diMuon_mass_test < 130) & (diMuon_mass_test > 120)],
)
sample_weights_test[y_test == 1] = sample_weights_test[y_test == 1] * (
    signal_weight_sum / bkg_weight_sum
)
fpr, tpr, thr = roc_curve(
    y_test[(diMuon_mass_test < 130) & (diMuon_mass_test > 120)],
    y_pred[(diMuon_mass_test < 130) & (diMuon_mass_test > 120)],
    sample_weight=sample_weights_test[
        (diMuon_mass_test < 130) & (diMuon_mass_test > 120)
    ],
)


significance = []
effSignal = []
effBkg = []
thresholds = []

ctr = 0
f_roc = open("roc/" + test_name + "_roc.txt", "w")

for i in range(len(fpr)):
    if fpr[i] > 1e-5 and tpr[i] > 1e-5:
        # print(
        # "thr = " + str(thr[i]) + ", fpr = " + str(fpr[i]) + ", tpr = " + str(tpr[i])
        # )
        f_roc.write(
            "thr = "
            + str(thr[i])
            + ", fpr = "
            + str(fpr[i])
            + ", tpr = "
            + str(tpr[i])
            + " \n"
        )
        significance.append(signal_events * tpr[i] / math.sqrt(fpr[i] * bkg_events))
        effSignal.append(tpr[i])
        effBkg.append(fpr[i])
        thresholds.append(thr[i])
        # print significance[ctr], ' ' , fpr[ctr], ' ', tpr[ctr]
        ctr = ctr + 1
f_roc.close()

max_significance = max(significance)
idx_max_significance = np.argmax(np.array(significance))
best_threshold = thresholds[idx_max_significance]
best_effSignal = effSignal[idx_max_significance]
best_effBkg = effBkg[idx_max_significance]

print("max_significance: " + str(max_significance))
print("best_threshold: " + str(best_threshold))
print("best_effSignal: " + str(best_effSignal))
print("best_effBkg: " + str(best_effBkg))

idx_WP80 = 0
minD0p8 = 999.0
for idx in range(len(effSignal)):
    if abs(effSignal[idx] - 0.80) < minD0p8:
        idx_WP80 = idx
        minD0p8 = abs(effSignal[idx] - 0.80)

WP80_significance = significance[idx_WP80]
WP80_threshold = thresholds[idx_WP80]
WP80_effSignal = effSignal[idx_WP80]
WP80_effBkg = effBkg[idx_WP80]

print("WP80_significance: " + str(WP80_significance))
print("WP80_threshold: " + str(WP80_threshold))
print("WP80_effSignal: " + str(WP80_effSignal))
print("WP80_effBkg: " + str(WP80_effBkg))

##########################################################
# make histogram of discriminator value for signal and bkg
##########################################################
# pd.DataFrame({'truth':y_test, 'disc':y_pred}).hist(column='disc', by='truth', bins=50)
y_frame = pd.DataFrame({"truth": y_test, "disc": y_pred, "weight": sample_weights_test})
y_frame_train = pd.DataFrame(
    {
        "truth": y_train,
        "disc": y_pred_train,
        "weight": sample_weights_train,
    }
)
disc_bkg = y_frame[y_frame["truth"] == 0]["disc"].values
disc_bkg_train = y_frame_train[y_frame_train["truth"] == 0]["disc"].values
disc_signal = y_frame[y_frame["truth"] == 1]["disc"].values
disc_signal_train = y_frame_train[y_frame_train["truth"] == 1]["disc"].values
weight_bkg = y_frame[y_frame["truth"] == 0]["weight"].values
weight_bkg_train = y_frame_train[y_frame_train["truth"] == 0]["weight"].values
weight_signal = y_frame[y_frame["truth"] == 1]["weight"].values
weight_signal_train = y_frame_train[y_frame_train["truth"] == 1]["weight"].values

f = plt.figure()
ax = f.add_subplot(111)
plt.hist(
    disc_signal,
    density=True,
    bins=100,
    alpha=1.0,
    histtype="step",
    lw=2,
    label="Signal - test",
    weights=weight_signal,
)
plt.hist(
    disc_signal_train,
    density=True,
    bins=100,
    alpha=1.0,
    histtype="step",
    lw=2,
    label="Signal  - train",
    weights=weight_signal_train,
)

plt.hist(
    disc_bkg,
    density=True,
    bins=100,
    alpha=1.0,
    histtype="step",
    lw=2,
    label="Bkg - test",
    weights=weight_bkg,
)
plt.hist(
    disc_bkg_train,
    density=True,
    bins=100,
    alpha=1.0,
    histtype="step",
    lw=2,
    label="Bkg - train",
    weights=weight_bkg_train,
)
plt.yscale("log")
plt.xlim([0.0, 1.0])
plt.ylim([0.001, 1000.0])
plt.legend(loc="upper right")
plt.xlabel("BDT response")
plt.ylabel("Events")
hep.cms.label(
    data="True",
    label="",
    year=era,
    com="13.6",
    lumi=str(luminosity[era]),
)
# plt.axvline(x=WP90_threshold, color="black", linestyle="--")
# plt.axvline(x=WP80_threshold, color="black")

plt.savefig(plotDir + "training/mydiscriminator_" + test_name + "_logY.pdf")
plt.savefig(plotDir + "training/mydiscriminator_" + test_name + "_logY.png")


f = plt.figure()
ax = f.add_subplot(111)
plt.hist(
    disc_signal,
    density=True,
    bins=100,
    alpha=1.0,
    histtype="step",
    lw=2,
    label="Signal - test",
    weights=weight_signal,
)
plt.hist(
    disc_signal_train,
    density=True,
    bins=100,
    alpha=1.0,
    histtype="step",
    lw=2,
    label="Signal  - train",
    weights=weight_signal_train,
)
plt.hist(
    disc_bkg,
    density=True,
    bins=100,
    alpha=1.0,
    histtype="step",
    lw=2,
    label="Bkg - test",
    weights=weight_bkg,
)
plt.hist(
    disc_bkg_train,
    density=True,
    bins=100,
    alpha=1.0,
    histtype="step",
    lw=2,
    label="Bkg - train",
    weights=weight_bkg_train,
)
plt.yscale("linear")
plt.xlim([0.0, 1.0])
# plt.ylim([0.001, 100.0])
plt.legend(loc="upper right")
plt.xlabel("BDT response")
plt.ylabel("Events")
hep.cms.label(
    data="True",
    label="",
    year=era,
    com="13.6",
    lumi=str(luminosity[era]),
)
plt.savefig(plotDir + "training/mydiscriminator_" + test_name + "_linY.pdf")
plt.savefig(plotDir + "training/mydiscriminator_" + test_name + "_linY.png")


# plot roc curve
f = plt.figure()
# ax = f.add_subplot(111)
lw = 2
plt.plot(fpr, tpr, color="darkorange", lw=lw, label="ROC curve")
plt.plot([0, 1], [0, 1], color="navy", lw=lw, linestyle="--")
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.ylabel("Signal Efficiency")
plt.xlabel("Background Efficiency")
# plt.axhline(y=0.9, color="black", linestyle="--")
# plt.axhline(y=0.8, color="black")
# plt.text(0.5,0.1,'WP80: bkg eff = %.4f'%WP80_effBkg, fontsize=12)
# plt.text(0.5,0.2,'WP90: bkg eff = %.4f'%WP90_effBkg, fontsize=12)
# plt.text(0.5,0.3,'WP90: S/sqrt(B) = %.2f'%WP90_significance, fontsize=12)
# plt.text(0.5, 0.3, "AUC = %.4f" % AUC, hhhontsize=12)
plt.text(0.5, 0.3, "AUC = %.4f" % AUC)
# plt.title('Receiver operating characteristic example')
# plt.legend(loc="lower right")

hep.cms.label(
    data="True",
    label="",
    year=era,
    com="13.6",
    lumi=str(luminosity[era]),
)
plt.savefig(plotDir + "training/myroc_" + test_name + ".pdf")
plt.savefig(plotDir + "training/myroc_" + test_name + ".png")

# Pickle dictionary using protocol 0.
output = open("models/model_" + test_name + ".pkl", "wb")
pickle.dump(model, output)
output.close()
model.get_booster().dump_model("models/model_" + test_name + ".txt")
model.get_booster().save_model("models/model_" + test_name + ".xgb")

# plot feature importances

model.get_booster().feature_names = [row[2] for row in variables[:-3]]
# model.get_booster().feature_names = [row[2] for row in variables[:-1]]

xgb.plot_importance(
    model, max_num_features=len(variables) - 3, xlabel="F score (weight)"
)
plt.savefig(
    plotDir + "training/myImportances_Fscore_" + test_name + ".pdf", bbox_inches="tight"
)
plt.savefig(
    plotDir + "training/myImportances_Fscore_" + test_name + ".png", bbox_inches="tight"
)

model.get_booster().feature_names = [row[1] for row in variables[:-3]]
# model.get_booster().feature_names = [row[1] for row in variables[:-1]]

# xgb.plot_tree( model.get_booster() )
xgb.plot_tree(model)
fig = plt.gcf()
fig.set_size_inches(150, 100)
# fig.set_size_inches(500, 50)
plt.draw()
plt.savefig(plotDir + "training/myTree_" + test_name + ".pdf")
plt.savefig(plotDir + "training/myTree_" + test_name + ".png")

print(
    "[INFO]: S ="
    + str(signal_events)
    + "; B ="
    + str(bkg_events)
    + "; S/sqrt(B) = "
    + str(signal_events / math.sqrt(bkg_events))
)
print(
    "[INFO] WP90: S = %6.3f" % (signal_events * 0.90)
    + ", B = %6.3f" % (bkg_events * WP90_effBkg)
)
print(
    "[INFO] WP80: S = %6.3f" % (signal_events * 0.80)
    + ", B = %6.3f" % (bkg_events * WP80_effBkg)
)

if append_variables:
    print("[INFO]: BDT score was not added to the trees")
    exit()

tuples= ["Data", "DY", "EWK", "TT", "DiBoson", "ggH", "VBF", "ttH"]
print("variables model: ", variables[:-3])
for file_type in tuples:
    xgb_utils.append_BDT_score(file_type, channel_US, era, "Combined", signal_subset, background_subset, variables[:-3], mean_map, std_map, variable_standatization)
    xgb_utils.append_BDT_score(file_type, channel_US, "2023BPix", "Combined", signal_subset, background_subset, variables[:-3], mean_map, std_map, variable_standatization)
    xgb_utils.append_BDT_score(file_type, channel_US, "2023BPix", "Combined", signal_subset, background_subset, variables[:-3], mean_map, std_map, variable_standatization)
xgb_utils.append_BDT_score("Data", channel_US, "2024", "Combined", signal_subset, background_subset, variables[:-3], mean_map, std_map, variable_standatization)

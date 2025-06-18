#ifndef LIB_GETHISTOGRAMS_H
#define LIB_GETHISTOGRAMS_H

#include "Constants.h"
#include "Run3Constants.h"
#include "Utils.h"
#include <TChain.h>
#include <TFile.h>
#include <TH1F.h>
#include <TLorentzVector.h>
#include <TNtuple.h>
#include <TString.h>
#include <cmath>
#include <iostream>
#include <math.h>

class CreateHistograms {
  public:
    // Methods
    CreateHistograms(TString input, TString output, TString era,
                     TString channel, bool is_data, bool is_signal_);
    virtual ~CreateHistograms();
    void fillChain();
    void defineHistograms();
    void setBranchesAddresses();
    void fillHistogramsData();
    void fillHistogramsSimulation();
    void saveHistograms();

  private:
    // Members

    TChain *tuple;
    bool is_signal;
    long double gen_weight_sum;
    double scale_factor; // luminosity * cross_section / gen_weight_sum
    const float luminosity;
    const float cross_section;
    TString input_name;
    TString output_name;
    TString output_directory;
    TNtuple *ntuple_output;
    TFile *output_file;

    // Read Tuples
    // DiMuon variables
    float diMuon_mass, diMuon_bsConstrainedMass, diMuon_pt, diMuon_phi, diMuon_eta, gen_weight,
        pileup_weight, pileup;
    // Muon variables
    int mu1_index, mu2_index;
    std::vector<int> *mu_charge;
    std::vector<float> *mu_pt, *mu_phi, *mu_eta;
    // Jet variables
    int n_jet;
    std::vector<float> *jet_mass, *jet_pt, *jet_phi, *jet_eta;
    // diJet variables
    float diJet_pt, diJet_eta, diJet_phi, diJet_mass, diJet_mass_mo;

    // Histograms
    // DiMuon variables
    TH1F diMuon_mass_hist, diMuon_pt_hist, diMuon_eta_hist, diMuon_phi_hist,
        diMuon_rapidity_hist, diMuon_mass_hist_full_range, diMuon_bsConstrainedMass_hist_full_range;
    // Muon variables
    TH1F mu1_pt_mass_ratio_hist, mu2_pt_mass_ratio_hist, mu1_eta_hist,
        mu2_eta_hist, phi_CS_hist, cos_theta_CS_hist;
    // Jet variables
    TH1F n_jet_hist, jet_mass_hist, jet_pt_hist, jet_phi_hist, jet_eta_hist;
    // diJet variables
    TH1F diJet_pt_hist, diJet_eta_hist, diJet_phi_hist, diJet_mass_hist,
        diJet_mass_mo_hist, delta_eta_hist;

    // Variables to save
    const char *variables_list =
        "gen_weight:scale_factor:weight:diMuon_pt:"
        "diMuon_rapidity:mu1_pt_mass_ratio:mu2_pt_mass_"
        "ratio:mu1_eta:mu2_eta:phi_CS:cos_theta_CS";
};

CreateHistograms::CreateHistograms(TString input, TString output, TString era,
                                   TString channel, bool is_data,
                                   bool is_signal_)
    : luminosity(LUMINOSITY.at(era)), cross_section(CROSS_SECTION.at(channel)) {

    tuple = new TChain("tree");
    ntuple_output = new TNtuple("tree", "", variables_list);
    input_name = input;
    output_directory = output;
    is_signal = is_signal_;
    output_name = channel + "_" + era + "_histos.root";
    std::cout << "Luminosity: " << luminosity
              << ", cross section: " << cross_section << std::endl;
    if (!is_data) {
        gen_weight_sum = GetGenWeightSum(input_name);
        scale_factor =
            GetScaleFactor(luminosity, cross_section, gen_weight_sum);
    }
    fillChain();
}

CreateHistograms::~CreateHistograms() {
    delete tuple->GetCurrentFile();
    delete ntuple_output;
    delete output_file;
}

void CreateHistograms::fillChain() {
    tuple->Add(input_name);
    if (!tuple) {
        throw std::runtime_error("Tuple file not found");
        return;
    }
    std::cout << "Tuple loaded" << std::endl;
}

void CreateHistograms::defineHistograms() {

    // DiMuon variables
    diMuon_mass_hist = TH1F("diMuon_mass", "diMuon_mass", 80, 110, 150);
    diMuon_pt_hist = TH1F("diMuon_pt", "diMuon_pt", 100, 0, 250);
    diMuon_phi_hist = TH1F("diMuon_phi", "diMuon_phi", 100, -3.1415, 3.1415);
    diMuon_eta_hist = TH1F("diMuon_eta", "diMuon_eta", 50, -10, 10);
    diMuon_rapidity_hist =
        TH1F("diMuon_rapidity", "diMuon_rapidity", 50, -2.5, 2.5);
    diMuon_mass_hist_full_range =
        TH1F("diMuon_mass_full_range", "diMuon_mass_full_range", 400, 50, 150);
    diMuon_bsConstrainedMass_hist_full_range =
    TH1F("diMuon_bsConstrainedMass_full_range", "diMuon_bsConstrainedMass_full_range", 400, 50, 150);
    
    // Muon variables
    mu1_pt_mass_ratio_hist =
        TH1F("mu1_pt_mass_ratio", "mu1_pt_mass_ratio", 50, 0, 1.4);
    mu2_pt_mass_ratio_hist =
        TH1F("mu2_pt_mass_ratio", "mu2_pt_mass_ratio", 50, 0, 1.4);
    mu1_eta_hist = TH1F("mu1_eta", "mu1_eta", 50, -2.4, 2.4);
    mu2_eta_hist = TH1F("mu2_eta", "mu2_eta", 50, -2.4, 2.4);
    phi_CS_hist = TH1F("phi_CS", "phi_CS", 50, -3.14, 3.14);
    cos_theta_CS_hist = TH1F("cos_theta_CS", "cos_theta_CS", 50, -1, 1);

    // Jet variables
    n_jet_hist = TH1F("n_jet", "n_jet", 10, 0, 10);
    jet_pt_hist = TH1F("jet_pt", "jet_pt", 400, 0, 400);
    jet_eta_hist = TH1F("jet_eta", "jet_eta", 200, -10, 10);
    jet_phi_hist = TH1F("jet_phi", "jet_phi", 100, -3.1415, 3.1415);
    jet_mass_hist = TH1F("jet_mass", "jet_mass", 240, 0, 120);

    // DiJet variables
    diJet_pt_hist = TH1F("diJet_pt", "diJet_pt", 800, 0, 800);
    diJet_eta_hist = TH1F("diJet_eta", "diJet_eta", 200, -10, 10);
    diJet_phi_hist = TH1F("diJet_phi", "diJet_phi", 100, -3.1415, 3.1415);
    diJet_mass_hist = TH1F("diJet_mass", "diJet_mass", 800, 0, 800);
    diJet_mass_mo_hist = TH1F("diJet_mass_mo", "diJet_mass_mo", 800, 0, 800);
    delta_eta_hist = TH1F("diJet_DeltaEta", "diJet_DeltaEta", 240, -12, 12);
}

void CreateHistograms::setBranchesAddresses() {

    tuple->SetBranchAddress("t_genWeight", &gen_weight);
    tuple->SetBranchAddress("t_puWeight", &pileup_weight);

    // DiMuon variables
    tuple->SetBranchAddress("t_diMuon_mass", &diMuon_mass);
    tuple->SetBranchAddress("t_diMuon_bsConstrainedMass", &diMuon_bsConstrainedMass);
    tuple->SetBranchAddress("t_diMuon_pt", &diMuon_pt);
    tuple->SetBranchAddress("t_diMuon_phi", &diMuon_phi);
    tuple->SetBranchAddress("t_diMuon_eta", &diMuon_eta);

    // Muon variables
    tuple->SetBranchAddress("t_mu1", &mu1_index);
    tuple->SetBranchAddress("t_mu2", &mu2_index);
    tuple->SetBranchAddress("t_Mu_charge", &mu_charge);
    tuple->SetBranchAddress("t_Mu_pt", &mu_pt);
    tuple->SetBranchAddress("t_Mu_phi", &mu_phi);
    tuple->SetBranchAddress("t_Mu_eta", &mu_eta);

    // Jet variables
    tuple->SetBranchAddress("t_nJet", &n_jet);
    tuple->SetBranchAddress("t_Jet_mass", &jet_mass);
    tuple->SetBranchAddress("t_Jet_pt", &jet_pt);
    tuple->SetBranchAddress("t_Jet_phi", &jet_phi);
    tuple->SetBranchAddress("t_Jet_eta", &jet_eta);

    // DiJet variables
    tuple->SetBranchAddress("t_diJet_mass", &diJet_mass);
    tuple->SetBranchAddress("t_diJet_mass_mo", &diJet_mass_mo);
    tuple->SetBranchAddress("t_diJet_pt", &diJet_pt);
    tuple->SetBranchAddress("t_diJet_phi", &diJet_phi);
    tuple->SetBranchAddress("t_diJet_eta", &diJet_eta);

    std::cout << "Branches addressed setted" << std::endl;
}

void CreateHistograms::fillHistogramsData() {

    std::cout << "Filling data histograms" << std::endl;
    int total_entries = tuple->GetEntries();
    TLorentzVector mu1_vector;
    TLorentzVector mu2_vector;
    std::pair<float, float> angles_CS;
    for (int event_index = 0; event_index < total_entries; event_index++) {
        tuple->GetEntry(event_index);
        if (diMuon_mass > 120 && diMuon_mass < 130)
            continue;
        diMuon_mass_hist_full_range.Fill(diMuon_mass);
        diMuon_bsConstrainedMass_hist_full_range.Fill(diMuon_bsConstrainedMass);
        if (diMuon_mass < 110 || diMuon_mass > 150)
            continue;

        // DiMuon variables
        diMuon_pt_hist.Fill(diMuon_pt);
        diMuon_phi_hist.Fill(diMuon_phi);
        diMuon_eta_hist.Fill(diMuon_eta);
        diMuon_mass_hist.Fill(diMuon_mass);
        diMuon_rapidity_hist.Fill((mu1_vector + mu2_vector).Rapidity());

        // Muon variables
        mu1_vector.SetPtEtaPhiM((*mu_pt)[mu1_index], (*mu_eta)[mu1_index],
                                (*mu_phi)[mu1_index], MUON_MASS);
        mu2_vector.SetPtEtaPhiM((*mu_pt)[mu2_index], (*mu_eta)[mu2_index],
                                (*mu_phi)[mu2_index], MUON_MASS);

        angles_CS = CSAngles(mu1_vector, mu2_vector, (*mu_charge)[mu1_index]);

        // Muon variables
        mu1_vector.SetPtEtaPhiM((*mu_pt)[mu1_index], (*mu_eta)[mu1_index],
                                (*mu_phi)[mu1_index], MUON_MASS);
        mu2_vector.SetPtEtaPhiM((*mu_pt)[mu2_index], (*mu_eta)[mu2_index],
                                (*mu_phi)[mu2_index], MUON_MASS);

        std::pair<float, float> angles_CS =
            CSAngles(mu1_vector, mu2_vector, (*mu_charge)[mu1_index]);

        mu1_pt_mass_ratio_hist.Fill((*mu_pt)[mu1_index] / diMuon_mass);
        mu2_pt_mass_ratio_hist.Fill((*mu_pt)[mu2_index] / diMuon_mass);
        mu1_eta_hist.Fill((*mu_eta)[mu1_index]);
        mu2_eta_hist.Fill((*mu_eta)[mu2_index]);
        phi_CS_hist.Fill(angles_CS.second);
        cos_theta_CS_hist.Fill(angles_CS.first);

        // Jet variables
        n_jet_hist.Fill(n_jet);

        if (n_jet < 2)
            continue;
        for (int j = 0; j < n_jet; j++) {
            jet_mass_hist.Fill(jet_mass->at(j));
            jet_pt_hist.Fill(jet_pt->at(j));
            jet_phi_hist.Fill(jet_phi->at(j));
            jet_eta_hist.Fill(jet_eta->at(j));
        }

        // diJet variables
        diJet_pt_hist.Fill(diJet_pt);
        diJet_eta_hist.Fill(diJet_eta);
        diJet_phi_hist.Fill(diJet_phi);
        diJet_mass_hist.Fill(diJet_mass);
        diJet_mass_mo_hist.Fill(diJet_mass_mo);
        delta_eta_hist.Fill(jet_eta->at(0) - jet_eta->at(1));

        ntuple_output->Fill(
            1, 1, 1, diMuon_pt, (mu1_vector + mu2_vector).Rapidity(),
            (*mu_pt)[mu1_index] / diMuon_mass,
            (*mu_pt)[mu2_index] / diMuon_mass, (*mu_eta)[mu1_index],
            (*mu_eta)[mu2_index], angles_CS.second, angles_CS.first);
    }
    std::cout << "Histograms filled" << std::endl;
}

void CreateHistograms::fillHistogramsSimulation() {

    std::cout << "Filling simulation histograms" << std::endl;
    double total_entries = tuple->GetEntries();
    double weight;
    TLorentzVector mu1_vector;
    TLorentzVector mu2_vector;
    std::pair<float, float> angles_CS;
    // float mu_1_pt, mu_1_phi, mu_3_pt;
    for (int event_index = 0; event_index < total_entries; event_index++) {
        tuple->GetEntry(event_index);
        weight = GetEventWeight(gen_weight, pileup_weight, scale_factor);
        diMuon_mass_hist_full_range.Fill(diMuon_mass, weight);
        diMuon_bsConstrainedMass_hist_full_range.Fill(diMuon_bsConstrainedMass, weight);
        diMuon_mass_hist.Fill(diMuon_mass, weight);

        if ((diMuon_mass > 120 && diMuon_mass < 130) && !is_signal)
            continue;
        if (diMuon_mass < 110 || diMuon_mass > 150)
            continue;

        // DiMuon variables
        diMuon_pt_hist.Fill(diMuon_pt, weight);
        diMuon_phi_hist.Fill(diMuon_phi, weight);
        diMuon_eta_hist.Fill(diMuon_eta, weight);
        diMuon_rapidity_hist.Fill((mu1_vector + mu2_vector).Rapidity(), weight);

        // Muon variables
        mu1_vector.SetPtEtaPhiM((*mu_pt)[mu1_index], (*mu_eta)[mu1_index],
                                (*mu_phi)[mu1_index], MUON_MASS);
        mu2_vector.SetPtEtaPhiM((*mu_pt)[mu2_index], (*mu_eta)[mu2_index],
                                (*mu_phi)[mu2_index], MUON_MASS);

        angles_CS = CSAngles(mu1_vector, mu2_vector, (*mu_charge)[mu1_index]);

        mu1_pt_mass_ratio_hist.Fill((*mu_pt)[mu1_index] / diMuon_mass, weight);
        mu2_pt_mass_ratio_hist.Fill((*mu_pt)[mu2_index] / diMuon_mass, weight);
        mu1_eta_hist.Fill((*mu_eta)[mu1_index], weight);
        mu2_eta_hist.Fill((*mu_eta)[mu2_index], weight);
        phi_CS_hist.Fill(angles_CS.second, weight);
        cos_theta_CS_hist.Fill(angles_CS.first, weight);

        // Jet variables
        n_jet_hist.Fill(n_jet, weight);
        if (n_jet < 2)
            continue;
        for (int j = 0; j < n_jet; j++) {
            jet_mass_hist.Fill(jet_mass->at(j), weight);
            jet_pt_hist.Fill(jet_pt->at(j), weight);
            jet_phi_hist.Fill(jet_phi->at(j), weight);
            jet_eta_hist.Fill(jet_eta->at(j), weight);
        }

        // diJet variables
        diJet_pt_hist.Fill(diJet_pt, weight);
        diJet_eta_hist.Fill(diJet_eta, weight);
        diJet_phi_hist.Fill(diJet_phi, weight);
        diJet_mass_hist.Fill(diJet_mass, weight);
        diJet_mass_mo_hist.Fill(diJet_mass_mo, weight);
        delta_eta_hist.Fill(jet_eta->at(0) - jet_eta->at(1), weight);

        ntuple_output->Fill(gen_weight, scale_factor, weight, diMuon_pt,
                            (mu1_vector + mu2_vector).Rapidity(),
                            (*mu_pt)[mu1_index] / diMuon_mass,
                            (*mu_pt)[mu2_index] / diMuon_mass,
                            (*mu_eta)[mu1_index], (*mu_eta)[mu2_index],
                            angles_CS.second, angles_CS.first);
    }

    std::cout << "Histograms filled" << std::endl;
}

void CreateHistograms::saveHistograms() {

    output_file = new TFile(output_directory + output_name, "RECREATE");
    output_file->cd();
    diMuon_mass_hist.Write();
    diMuon_pt_hist.Write();
    diMuon_phi_hist.Write();
    diMuon_eta_hist.Write();
    diMuon_rapidity_hist.Write();
    diMuon_mass_hist_full_range.Write();
    diMuon_bsConstrainedMass_hist_full_range.Write();

    mu1_pt_mass_ratio_hist.Write();
    mu2_pt_mass_ratio_hist.Write();
    mu1_eta_hist.Write();
    mu2_eta_hist.Write();
    phi_CS_hist.Write();
    cos_theta_CS_hist.Write();

    n_jet_hist.Write();
    jet_mass_hist.Write();
    jet_pt_hist.Write();
    jet_phi_hist.Write();
    jet_eta_hist.Write();

    diJet_pt_hist.Write();
    diJet_eta_hist.Write();
    diJet_phi_hist.Write();
    diJet_mass_hist.Write();
    diJet_mass_mo_hist.Write();
    delta_eta_hist.Write();

    ntuple_output->Write();

    output_file->Close();
    std::cout << "Histograms saved" << std::endl;
}

#endif // if LIB_GETHISTOGRAMS_H

#ifndef LIB_SKIMTUPLES_H
#define LIB_SKIMTUPLES_H

#include "Constants.h"
#include "Run3Constants.h"
#include "Utils.h"
#include <TChain.h>
#include <TH1F.h>
#include <TLorentzVector.h>
#include <TMath.h>
#include <TNtuple.h>
#include <TString.h>
#include <cmath>
#include <iostream>
#include <math.h>

class SkimTuples {
  public:
    // Methods
    SkimTuples(TString input, TString output, TString era, TString channel,
               bool is_data_);
    virtual ~SkimTuples();
    // double eventWeight();
    void fillChain();
    void setBranchesAddresses();
    bool isggHCategory() const;
    void fillTree();
    void saveFile();

  private:
    // Members
    TChain *tuple;
    bool is_data;
    long double gen_weight_sum;
    double scale_factor; // luminosity * cross_section / gen_weight_sum
    const float luminosity;
    const float cross_section;
    TNtuple *ntuple_output;
    TString input_name;
    TString output_name;
    TString output_directory;
    TFile *output_file;

    // Read Branches
    // DiMuon
    float diMuon_mass, diMuon_pt, diMuon_phi, diMuon_eta, gen_weight,
        pileup_weight;
    // Muons
    int mu1_index, mu2_index;
    std::vector<int> *mu_charge;
    std::vector<float> *mu_pt, *mu_phi, *mu_eta;
    // Electrons
    std::vector<float> *elec_pt;
    // Jets
    int number_of_b_jets, number_of_jets;
    std::vector<float> *jet_eta, *jet_pt, *jet_phi, *jet_mass;
    // diJets
    float diJet_mass;

    // Variables to save
    const char *variables_list =
        "diMuon_pt:diMuon_rapidity:mu1_pt_mass_ratio:mu2_pt_mass_ratio:mu1_eta:"
        "mu2_eta:phi_CS:cos_theta_CS:n_jet:leading_jet_pt:leading_jet_eta:"
        "delta_eta_dimuon_jet:"
        "delta_phi_diMuon_jet:diJet_mass:delta_eta_diJet:delta_phi_diJet:"
        "z_zeppenfeld:min_delta_eta_dimuon_jet:min_delta_phi_dimuon_jet:weight";
};

SkimTuples::SkimTuples(TString input, TString output, TString era,
                       TString channel, bool is_data_)
    : is_data(is_data_), luminosity(LUMINOSITY.at(era)),
      cross_section(CROSS_SECTION.at(channel)) {

    ntuple_output = new TNtuple("tree_skim", "", variables_list);
    tuple = new TChain("tree");
    input_name = input;
    output_directory = output;
    output_name = channel + "_" + era + "_skim.root";
    if (!is_data) {
        gen_weight_sum = GetGenWeightSum(input_name);
        scale_factor =
            GetScaleFactor(luminosity, cross_section, gen_weight_sum) /
            luminosity;
    }
    mu_charge = nullptr;
    mu_pt = nullptr;
    mu_phi = nullptr;
    mu_eta = nullptr;
    elec_pt = nullptr;
    jet_eta = nullptr;
    jet_pt = nullptr;
    jet_phi = nullptr;
    jet_mass = nullptr;

    std::cout << "Luminosity: " << luminosity
              << ", cross section: " << cross_section << std::endl;
    fillChain();
}

SkimTuples::~SkimTuples() {

    delete tuple->GetCurrentFile();
    delete ntuple_output;
    delete output_file;
    std::cout << "SkimTuples object delete" << std::endl;
}

void SkimTuples::fillChain() {
    tuple->Add(input_name);
    if (!tuple) {
        throw std::runtime_error("Tuple file not found");
        return;
    }
    std::cout << "Tuple loaded" << std::endl;
}

void SkimTuples::setBranchesAddresses() {

    tuple->SetBranchAddress("t_diMuon_mass", &diMuon_mass);
    tuple->SetBranchAddress("t_diMuon_pt", &diMuon_pt);
    tuple->SetBranchAddress("t_diMuon_phi", &diMuon_phi);
    tuple->SetBranchAddress("t_diMuon_eta", &diMuon_eta);

    tuple->SetBranchAddress("t_genWeight", &gen_weight);
    tuple->SetBranchAddress("t_puWeight", &pileup_weight);

    tuple->SetBranchAddress("t_mu1", &mu1_index);
    tuple->SetBranchAddress("t_mu2", &mu2_index);
    tuple->SetBranchAddress("t_Mu_charge", &mu_charge);
    tuple->SetBranchAddress("t_Mu_pt", &mu_pt);
    tuple->SetBranchAddress("t_Mu_phi", &mu_phi);
    tuple->SetBranchAddress("t_Mu_eta", &mu_eta);

    tuple->SetBranchAddress("t_nbJet", &number_of_b_jets);
    tuple->SetBranchAddress("t_nJet", &number_of_jets);
    tuple->SetBranchAddress("t_Jet_eta", &jet_eta);
    tuple->SetBranchAddress("t_Jet_pt", &jet_pt);
    tuple->SetBranchAddress("t_Jet_phi", &jet_phi);
    tuple->SetBranchAddress("t_Jet_mass", &jet_mass);

    tuple->SetBranchAddress("t_diJet_mass", &diJet_mass);

    tuple->SetBranchAddress("t_El_pt", &elec_pt);

    // tuple->SetBranchAddress("t_pileup", &pileup);
    std::cout << "Branches addressed setted" << std::endl;
}

void SkimTuples::fillTree() {

    std::cout << "Filling tree" << std::endl;
    double total_entries = tuple->GetEntries();
    std::cout << "Events: " << total_entries << std::endl;
    double weight;
    float diMuon_rapidity;
    TLorentzVector mu1_vector, mu2_vector;
    std::pair<float, float> angles_CS;

    float leading_jet_pt, leading_jet_eta, delta_eta_diMuon_jet,
        delta_phi_diMuon_jet, delta_eta_diJet, delta_phi_diJet, z_zeppenfeld,
        min_delta_eta_dimuon_jet, min_delta_phi_dimuon_jet;

    for (int event_index = 0; event_index < total_entries; event_index++) {
        tuple->GetEntry(event_index);

        if (diMuon_mass < 110 || diMuon_mass > 150)
            continue;

        if (!isggHCategory()) {
            continue;
        }

        weight = GetEventWeight(gen_weight, pileup_weight, scale_factor);
        mu1_vector.SetPtEtaPhiM((*mu_pt)[mu1_index], (*mu_eta)[mu1_index],
                                (*mu_phi)[mu1_index], MUON_MASS);
        mu2_vector.SetPtEtaPhiM((*mu_pt)[mu2_index], (*mu_eta)[mu2_index],
                                (*mu_phi)[mu2_index], MUON_MASS);

        diMuon_rapidity = (mu1_vector + mu2_vector).Rapidity();

        angles_CS = CSAngles(mu1_vector, mu2_vector, (*mu_charge)[mu1_index]);
        int number_of_saving_variables = 20; // Number of arguments
        // Float_t values[number_of_saving_variables];

        if (number_of_jets == 0) {
            leading_jet_pt = 0;
            leading_jet_eta = 0;
            delta_eta_diMuon_jet = 0;
            delta_phi_diMuon_jet = 0;
            diJet_mass = 0;
            delta_eta_diJet = 0;
            delta_phi_diJet = -1;
            z_zeppenfeld = 0;
            min_delta_eta_dimuon_jet = 0;
            min_delta_phi_dimuon_jet = 0;
        } else if (number_of_jets == 1) {

            leading_jet_pt = jet_pt->at(0);
            leading_jet_eta = jet_eta->at(0);
            delta_eta_diMuon_jet = diMuon_eta - jet_eta->at(0);
            delta_phi_diMuon_jet = DeltaPhi(diMuon_phi, jet_phi->at(0));
            diJet_mass = 0;
            delta_eta_diJet = 0;
            delta_phi_diJet = -1;
            z_zeppenfeld = 0;
            min_delta_eta_dimuon_jet = 0;
            min_delta_phi_dimuon_jet = 0;
        } else {
            leading_jet_pt = jet_pt->at(0);
            leading_jet_eta = jet_eta->at(0);
            delta_eta_diMuon_jet = diMuon_eta - jet_eta->at(0);
            delta_phi_diMuon_jet = DeltaPhi(diMuon_phi, jet_phi->at(0));
            // diJet_mass;
            //  std::cout << "Two events DJ Mass: " << diJet_mass;
            delta_eta_diJet = jet_eta->at(0) - jet_eta->at(1);
            delta_phi_diJet = DeltaPhi(jet_phi->at(0), jet_phi->at(1));
            z_zeppenfeld = GetZZeppenfeldVariable(diMuon_rapidity, jet_pt,
                                                  jet_phi, jet_eta, jet_mass);
            min_delta_eta_dimuon_jet = TMath::Min(diMuon_eta - jet_eta->at(0),
                                                  diMuon_eta - jet_eta->at(1));
            min_delta_phi_dimuon_jet =
                TMath::Min(DeltaPhi(diMuon_eta, jet_eta->at(0)),
                           DeltaPhi(diMuon_eta, jet_eta->at(1)));
        }

        float values[number_of_saving_variables] = {
            diMuon_pt,
            diMuon_rapidity,
            (*mu_pt)[mu1_index] / diMuon_mass,
            (*mu_pt)[mu2_index] / diMuon_mass,
            (*mu_eta)[mu1_index],
            (*mu_eta)[mu2_index],
            angles_CS.second,
            angles_CS.first,
            static_cast<float>(number_of_jets),
            leading_jet_pt,
            leading_jet_eta,
            delta_eta_diMuon_jet,
            delta_phi_diMuon_jet,
            diJet_mass,
            delta_eta_diJet,
            delta_phi_diJet,
            z_zeppenfeld,
            min_delta_eta_dimuon_jet,
            min_delta_phi_dimuon_jet,
            static_cast<float>(weight),
        };

        ntuple_output->Fill(values);
    }

    std::cout << "Ntuple filled" << std::endl;
}

bool SkimTuples::isggHCategory() const {

    if ((number_of_b_jets == 0) && (mu_pt->size() < 3) &&
        (elec_pt->size() == 0)) {
        if (jet_eta->size() >= 2) {
            if ((diJet_mass < 400) &&
                ((jet_eta->at(0) - jet_eta->at(1)) < 2.5)) {
                return true;
            } else {
                return false;
            }
        } else {
            return true;
        }
    }
    return false;
}

void SkimTuples::saveFile() {

    output_file = new TFile(output_directory + output_name, "RECREATE");
    output_file->cd();
    ntuple_output->Write();
    output_file->Close();
    std::cout << "Ntuple saved" << std::endl;
}

#endif // if LIB_SKIMTUPLES_H

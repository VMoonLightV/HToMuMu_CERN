#include <TBranch.h>
#include <TFile.h>
#include <TROOT.h>
#include <TTree.h>
#include <TTreeFormula.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <TSystem.h>
#include <TError.h>
#include <algorithm>

#include "correction.h"
#include "../lib/LeptonEfficiencyCorrector.h"

// g++ "/afs/cern.ch/user/y/yulou/CMSSW_14_0_14/src/HToMuMu/src/LeptonEfficiencyCorrector.cc" -o ./bin/Eff_on_tuple src/Eff_on_tuple.cc $(root-config --cflags --libs)  $(correction config --cflags --ldflags)

int main(int argc, char *argv[])
{
    if (argc != 7)
    {
        std::cerr << "Please give 8 arguments: input, output, channel, era, is_data, njet, zone, coffi_csv"
                  << std::endl;
        return -1;
    }

    TString input_name(argv[1]);
    TString output(argv[2]);
    TString era(argv[3]);
    TString channel(argv[4]);
    const bool is_data = *argv[5] == 'T';
    TString region(argv[6]);
    std::cout << "channel: " << channel << std::endl;
    std::cout << "era: " << era << std::endl;

    LeptonEfficiencyCorrector corrector;
    corrector.initializeCorrections(era.Data());

    TFile inputFile(input_name, "READ");
    if (inputFile.IsZombie())
    {
        std::cerr << "Error opening input file!" << std::endl;
        return 0;
    }

    TTree *tree_input = (TTree *)inputFile.Get("tree_output");
    if (!tree_input)
    {
        std::cerr << "Tree output not found in file " << input_name << std::endl;
        return 0;
    }

    tree_input->SetBranchStatus("*", 1);

    double weight = 0;
    float dimuon_mass = 0;
    float mu1_pt = 0;
    float mu1_eta = 0;
    float mu2_pt = 0;
    float mu2_eta = 0;
    tree_input->SetBranchAddress("weight", &weight);
    tree_input->SetBranchAddress("diMuon_mass", &dimuon_mass);
    tree_input->SetBranchAddress("mu1_pt", &mu1_pt);
    tree_input->SetBranchAddress("mu1_eta", &mu1_eta);
    tree_input->SetBranchAddress("mu2_pt", &mu2_pt);
    tree_input->SetBranchAddress("mu2_eta", &mu2_eta);

    ////TString output_file_path = output + njet +"jet/Zpt_self_normalization_reweighting_8-th/" + channel + "_" + era + "_skim.root";
    TString output_file_path = output + region + "_eff/" + channel + "_" + era + "_skim.root";

    TString output_dir = gSystem->DirName(output_file_path);

    if (gSystem->AccessPathName(output_dir, kWritePermission))
    {

        if (gSystem->mkdir(output_dir, kTRUE) != 0)
        {
            Error("", "Failed to create directory: %s", output_dir.Data());
            return 1;
        }
    }
    TFile output_file(output_file_path, "RECREATE");

    TTree *tree_output = tree_input->CloneTree(0);

    Long64_t n_entries = tree_input->GetEntries();
    Long64_t n_selected = 0;
    int zero_division_warnings = 0;
    const int MAX_WARNINGS = 5;

    float Mu1_ID_SF = 0;
    float Mu1_ISO_SF = 0;
    float Mu2_ID_SF = 0;
    float Mu2_ISO_SF = 0;

    tree_output->Branch("Mu1_ID_SF", &Mu1_ID_SF, "Mu1_ID_SF/F");
    tree_output->Branch("Mu1_ISO_SF", &Mu1_ISO_SF, "Mu1_ISO_SF/F");
    tree_output->Branch("Mu2_ID_SF", &Mu2_ID_SF, "Mu2_ID_SF/F");
    tree_output->Branch("Mu2_ISO_SF", &Mu2_ISO_SF, "Mu2_ISO_SF/F");

    std::cout << "\nstart processing " << n_entries << " events..." << std::endl;
    std::cout << "\nregion:  " << region << std::endl;

    for (Long64_t i = 0; i < n_entries; i++)
    {
        tree_input->GetEntry(i);

        if ((region == "ZCR" && dimuon_mass > 70 && dimuon_mass < 110) ||
            (region == "SR" && dimuon_mass > 110 && dimuon_mass < 150)) {

            if (channel == "DY" || channel == "EWK" || channel == "TT" || channel == "DiBoson") {
                Mu1_ID_SF = corrector.give_eff("Muon_eff_SF_ID", mu1_pt, mu1_eta);
                Mu1_ISO_SF = corrector.give_eff("Muon_eff_SF_ISO", mu1_pt, mu1_eta);
                Mu2_ID_SF = corrector.give_eff("Muon_eff_SF_ID", mu2_pt, mu2_eta);
                Mu2_ISO_SF = corrector.give_eff("Muon_eff_SF_ISO", mu2_pt, mu2_eta);

                weight = weight * Mu1_ID_SF * Mu1_ISO_SF * Mu2_ID_SF * Mu2_ISO_SF;
                if (i < 10)
                {
                    std::cout << "Muon1 eff (ID and ISO): " << Mu1_ID_SF << Mu1_ISO_SF << std::endl;
                }

            }
            
            tree_output->Fill();
        }
    }

    output_file.cd();
    tree_output->Write();
    output_file.Close();
    inputFile.Close();

    std::cout << "file in: " << output_file_path << std::endl;

    return 0;
}
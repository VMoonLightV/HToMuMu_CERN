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
#include <map>
#include <utility> 

// g++ -o ./bin/EVE_mass_reso_calibration src/EVE_mass_reso_calibration.cc $(root-config --cflags --libs)

struct BinInfo {
    float muon1_pt_cut_low;
    float muon1_pt_cut_high;
    std::string region_1;	
    std::string region_2;	
    float edian_value;	
    float BSC_res;
    float calibration_factors;
};

std::map<std::string, std::pair<double, double>> eta_cuts = {
    {"B", {0.0, 0.9}},
    {"O", {0.9, 1.8}},
    {"E", {1.8, 2.4}}
};

int main(int argc, char *argv[]) {
    if (argc != 7) {
        std::cerr << "Please give 8 arguments: input, output, channel, era, is_data, njet, zone, coffi_csv"
                  << std::endl;
        return -1;
    }

    TString input_name(argv[1]);
    TString output(argv[2]);
    TString era(argv[3]);
    TString channel(argv[4]);
    const bool is_data = *argv[5] == 'T';
    TString csvFile(argv[6]);
    std::cout << "channel: " << channel << std::endl;
    std::cout << "era: " << era << std::endl;
    std::cout << "calibration_factor_file " << csvFile << std::endl;
    
    TFile inputFile(input_name, "READ");
    if (inputFile.IsZombie()) {
        std::cerr << "Error opening input file!" << std::endl;
        return 0;
    }

    TTree *tree_input = (TTree *)inputFile.Get("tree_output");
    if (!tree_input) {
        std::cerr << "Tree output not found in file " << input_name << std::endl;
        return 0;
    }

    tree_input->SetBranchStatus("*", 1);
    
    float relative_bsCMass_error =0;
    float mu1_bsConstrainedPt = 0;
    float mu1_eta = 0;
    float mu2_eta = 0;

    tree_input->SetBranchAddress("relative_diMuon_bsConstrainedMass_error", &relative_bsCMass_error);
    tree_input->SetBranchAddress("mu1_bsConstrainedPt", &mu1_bsConstrainedPt);
    tree_input->SetBranchAddress("mu1_eta", &mu1_eta);
    tree_input->SetBranchAddress("mu2_eta", &mu2_eta);

    
    TString output_file_path = output + channel + "_" + era + "_skim.root";
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
    TTree* tree_output = tree_input->CloneTree(0);

    Long64_t n_entries = tree_input->GetEntries();
    Long64_t n_selected = 0;
    int zero_division_warnings = 0;
    const int MAX_WARNINGS = 5;

    std::ifstream file(csvFile);
    if (!file.is_open()) {
        std::cerr << "Error opening file: " << csvFile << std::endl;
        return 1;
    }

    std::string line;
    std::vector<BinInfo> bins;

    std::getline(file, line);
    //muon1_pt_cut_low	muon1_pt_cut_high	region_1	region_2	median_value	BSC_res	calibration_factors

    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string cell;
        BinInfo bin;

        std::getline(ss, cell, ',');
        bin.muon1_pt_cut_low = std::stod(cell);

        std::getline(ss, cell, ',');
        bin.muon1_pt_cut_high = std::stod(cell);

        std::getline(ss, cell, ',');
        bin.region_1 = cell;

        std::getline(ss, cell, ',');
        bin.region_2 = cell;

        std::getline(ss, cell, ',');
        std::getline(ss, cell, ','); 

        std::getline(ss, cell, ','); 
        bin.calibration_factors = std::stod(cell);

        bins.push_back(bin);
    }
    file.close();
    
    std::cout << "\n start processing " << n_entries << " events..." << std::endl;    
    std::cout << "\n start event-by-event mass resolution calibration " << channel << std::endl;
    
    float bsCMass_error = 1;
    tree_output->Branch("calibrated_diMuon_bsConstrainedMass_error", &bsCMass_error, "calibrated_diMuon_bsConstrainedMass_error/F");
    
    for (Long64_t i = 0; i < n_entries; i++) {
        tree_input->GetEntry(i);  
        bsCMass_error = relative_bsCMass_error;
            
        if (channel == "DY" || channel =="Data")  {
            //std::cout << "\n start normalization for DY" << std::endl;
            //weight = weight * ratio;
            for (const auto &bin : bins) {
                if (mu1_bsConstrainedPt > bin.muon1_pt_cut_low && mu1_bsConstrainedPt < bin.muon1_pt_cut_high &&
                    mu1_eta > eta_cuts[bin.region_1].first && mu1_eta < eta_cuts[bin.region_1].second &&
                    mu2_eta > eta_cuts[bin.region_2].first && mu2_eta < eta_cuts[bin.region_2].second
                ) {
                    bsCMass_error = relative_bsCMass_error * bin.calibration_factors;
                    break;
                }  
            }
            
        }
        tree_output->Fill();
    }
    

    output_file.cd();
    tree_output->Write();
    output_file.Close();
    inputFile.Close();

    std::cout << "file in: " << output_file_path << std::endl;

    return 0;
}
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

// g++ -o ./bin/normalization src/normalization.cc $(root-config --cflags --libs)


int main(int argc, char *argv[]) {
    if (argc != 8) {
        std::cerr << "Please give 8 arguments: input, output, channel, era, is_data, njet, zone, coffi_csv"
                  << std::endl;
        return -1;
    }

    TString input_name(argv[1]);
    TString output(argv[2]);
    TString era(argv[3]);
    TString channel(argv[4]);
    const bool is_data = *argv[5] == 'T';
    TString njet(argv[6]);
    double ratio = atof(argv[7]);
    std::cout << "channel: " << channel << std::endl;
    std::cout << "era: " << era << std::endl;
    std::cout << "ratio: " << ratio << std::endl;
    
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
    
    double weight = 0;
    float dimuon_pt = 0;
    tree_input->SetBranchAddress("weight", &weight);
    tree_input->SetBranchAddress("diMuon_pt", &dimuon_pt);

    TString output_file_path = output + njet +"jet/ZCR_normalization/" + channel + "_" + era + "_skim.root";
    TFile output_file(output_file_path, "RECREATE");
    
    TTree* tree_output = tree_input->CloneTree(0);

    Long64_t n_entries = tree_input->GetEntries();
    Long64_t n_selected = 0;
    int zero_division_warnings = 0;
    const int MAX_WARNINGS = 5;
    
    std::cout << "\n start processing " << n_entries << " events..." << std::endl;
    

    
    for (Long64_t i = 0; i < n_entries; i++) {
        tree_input->GetEntry(i);  
            
        if (channel == "DY" || channel == "TT" || channel == "DiBoson" || channel == "EWK")  {
            //std::cout << "\n start normalization for MC bkg" << std::endl;
            weight = weight * ratio;
                
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
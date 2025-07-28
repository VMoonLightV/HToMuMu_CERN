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

// g++ -o ./bin/reweighting_Zpt src/reweighting_Zpt.cc $(root-config --cflags --libs)



double Polynomial(const std::vector<double>& coefficients, double x) {
    double result = 0.0;
    for (size_t i = 0; i < coefficients.size(); i++) {
        result = result * x + coefficients[i];
    }
    return result;
}

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
    TString njet(argv[6]);
    TString coeff_csv = "/afs/cern.ch/user/y/yulou/CMSSW_14_0_14/src/HToMuMu/plots/ratio/njet/"+ njet +"jet_ratio_table_dimuon_pt_ZCR_normalization/polynomial_"+ era +"_coefficients.csv";
    std::cout << "channel: " << channel << std::endl;
    std::cout << "era: " << era << std::endl;
    std::cout << "coffi_csv: " << coeff_csv << std::endl;
    
    std::vector<double> coefficients;
    try {
        std::ifstream csv_file(coeff_csv.Data());
        if (!csv_file.is_open()) {
            throw std::runtime_error("can't open coffi_csv file: " + coeff_csv);
        }
        
        std::string line;
        std::getline(csv_file, line);
        
        while (std::getline(csv_file, line)) {
            std::istringstream iss(line);
            std::string order_str, coeff_str;
            
            if (std::getline(iss, order_str, ',') && std::getline(iss, coeff_str)) {
                try {
                    double coeff_value = std::stod(coeff_str);
                    coefficients.push_back(coeff_value);
                } catch (const std::exception& e) {
                    std::cerr << "wrong transfrorm " << e.what() << " line: " << line << std::endl;
                }
            }
        }
        
        if (coefficients.size() != 9) {
            throw std::runtime_error("need 9 coffis, read: " + std::to_string(coefficients.size()));
        }
        
        //std::cout << "\nnominal order (high to low):" << std::endl;
        for (int i = 0; i < 9; i++) {
            //std::cout << "order " << 8-i << ": " << coefficients[i] << std::endl;
        }
        
    } catch (const std::exception& e) {
        std::cerr << "wrong read: " << e.what() << std::endl;
        return -1;
    }

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

    TString output_file_path = output + njet +"jet/ZCR_self_reweighting_0-250pt/" + channel + "_" + era + "_skim.root";

    TString output_dir = gSystem->DirName(output_file_path);

    if (gSystem->AccessPathName(output_dir, kWritePermission)) {

        if (gSystem->mkdir(output_dir, kTRUE) != 0) {
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
    
    std::cout << "\n start processing " << n_entries << " events..." << std::endl;
    
    for (Long64_t i = 0; i < n_entries; i++) {
        tree_input->GetEntry(i);  
        
        double f_pt = Polynomial(coefficients, dimuon_pt);

        if (f_pt < 0.1) {
            std::cout << "\n strange F(pt): " << f_pt << ", with dimuon_pt:" << dimuon_pt << std::endl;
        }
        
        //if (channel == "DY" || channel == "TT" || channel == "DiBoson" || channel == "EWK")  {
        if (channel == "DY") {
            /*if (fabs(f_pt) < 1e-10) {
                if (zero_division_warnings < MAX_WARNINGS) {
                    std::cerr << "warning: at event " << i << " dimuon_pt = " << dimuon_pt
                            << ", f(pt) ≈ 0 (" << f_pt << ")weight set as 0" << std::endl;
                    zero_division_warnings++;
                }
                weight = 0;
            } else {
                weight = weight * f_pt;
            }*/
            if ((dimuon_pt) < 250.0) {
                weight = weight * f_pt;
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
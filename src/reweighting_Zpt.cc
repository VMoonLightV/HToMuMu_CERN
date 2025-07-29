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

// g++ -o ./bin/reweighting_Zpt src/reweighting_Zpt.cc $(root-config --cflags --libs)



float Polynomial(const std::vector<float>& coefficients, float x) {
    float result = 0.0;
    for (size_t i = 0; i < coefficients.size(); i++) {
        result = result * x + coefficients[i];
    }
    return result;
}

struct PolynomialSegment {
    double range_L;
    double range_R;
    int power;
    double coefficient;
};

float PiecewisePolynomial(const std::vector<PolynomialSegment>& segments, float x) {
    auto seg = std::find_if(segments.begin(), segments.end(), [x](const auto& s) {
        
        return x >= s.range_L && x <= s.range_R; 
    });

    if (seg == segments.end()) {
        return std::numeric_limits<float>::quiet_NaN(); 
    }
    std::vector<float> coeffs;
    for (const auto& s : segments) {
        if (s.range_L == seg->range_L && s.range_R == seg->range_R) {
            if (coeffs.size() <= static_cast<size_t>(s.power)) {
                coeffs.resize(s.power + 1, 0.0);
            }
            coeffs[s.power] = s.coefficient;
        }
    }
    float result = 0.0;
    for (size_t i = 0; i < coeffs.size(); i++) {
        result = result * x + coeffs[i];
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
    TString coeff_csv = "/afs/cern.ch/user/y/yulou/CMSSW_14_0_14/src/HToMuMu/plots/ratio/njet/"+ njet +"jet_ratio_table_dimuon_pt_ZCR_normalization_piecewise_8-th/polynomial_"+ era +"_coefficients.csv";
    std::cout << "channel: " << channel << std::endl;
    std::cout << "era: " << era << std::endl;
    std::cout << "coffi_csv: " << coeff_csv << std::endl;
    /*
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
        */

    std::vector<PolynomialSegment> segments; // 替换原有的coefficients

    std::ifstream csv_file(coeff_csv.Data());
    if (!csv_file.is_open()) {
            throw std::runtime_error("can't open coffi_csv file: " + coeff_csv);
    }
        
    std::string line;
    std::getline(csv_file, line);
    while (std::getline(csv_file, line)) {
        std::istringstream iss(line);
        std::string rangeL_str, rangeR_str, power_str, coeff_str;
        
        // 按列解析：区间左、右、幂次、系数
        std::getline(iss, rangeL_str, ',');
        std::getline(iss, rangeR_str, ',');
        std::getline(iss, power_str, ','); 
        std::getline(iss, coeff_str);
        try {
                PolynomialSegment seg{
                    std::stod(rangeL_str),
                    std::stod(rangeR_str),
                    std::stoi(power_str),
                    std::stod(coeff_str)
                };
                segments.push_back(seg);
        
        } catch (...) {}
        
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

    TString output_file_path = output + njet +"jet/Zpt_self_normalization_reweighting_8-th/" + channel + "_" + era + "_skim.root";

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
                float f_pt = PiecewisePolynomial(segments, dimuon_pt);
                weight = weight * f_pt;
                if (i<10) {std::cout << f_pt << " in pt: " << dimuon_pt << std::endl;}
                if (f_pt < 0.1) {
                    std::cout << "\n strange F(pt): " << f_pt << ", with dimuon_pt:" << dimuon_pt << std::endl;
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
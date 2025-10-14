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
#include <cmath>

// g++ -o ./bin/EVE_mass_reso_calibration src/EVE_mass_reso_calibration.cc $(root-config --cflags --libs)

struct BinInfo
{
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
    {"E", {1.8, 2.4}},
    {"B+O+E", {0.0, 2.4}}};

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
    TString csvFile(argv[6]);
    std::cout << "channel: " << channel << std::endl;
    std::cout << "era: " << era << std::endl;
    std::cout << "calibration_factor_file " << csvFile << std::endl;

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

    float diMuon_bsConstrainedMass = 0;
    float rela_bsCMass_error = 0;
    float mu1_bsConstrainedPt = 0;
    float mu1_eta = 0;
    float mu2_eta = 0;

    tree_input->SetBranchAddress("diMuon_bsConstrainedMass", &diMuon_bsConstrainedMass);
    tree_input->SetBranchAddress("relative_diMuon_bsConstrainedMass_error", &rela_bsCMass_error);
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
    TTree *tree_output = tree_input->CloneTree(0);

    Long64_t n_entries = tree_input->GetEntries();
    Long64_t n_selected = 0;
    int zero_division_warnings = 0;
    const int MAX_WARNINGS = 5;

    std::ifstream file(csvFile);
    if (!file.is_open())
    {
        std::cerr << "Error opening file: " << csvFile << std::endl;
        return 1;
    }

    std::string line;
    std::vector<BinInfo> bins;

    std::getline(file, line);
    // muon1_pt_cut_low	muon1_pt_cut_high	region_1	region_2	median_value	BSC_res	calibration_factors

    while (std::getline(file, line))
    {
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
    /*
        std::cout << "\n--- Printing loaded bin information ---" << std::endl;
        for (size_t i = 0; i < bins.size(); ++i)
        {
            const auto &bin = bins[i];
            std::cout << "Bin " << i << ":" << "  muon1_pt_cut_low: " << bin.muon1_pt_cut_low << "  muon1_pt_cut_high: " << bin.muon1_pt_cut_high << std::endl;
            std::cout << "  region_1: " << bin.region_1 << ":" << eta_cuts[bin.region_1].first << "-" << eta_cuts[bin.region_1].second << "  region_2: " << bin.region_2 << ":" << eta_cuts[bin.region_2].first << "-" << eta_cuts[bin.region_2].second << std::endl;
            std::cout << "  calibration_factors: " << bin.calibration_factors << std::endl;
            std::cout << "----------------------------------------" << std::endl;
        }
        std::cout << "--- Finished printing bin information ---" << std::endl;
    */
    std::cout << "\n start processing " << n_entries << " events..." << std::endl;
    std::cout << "\n start event-by-event mass resolution calibration " << channel << std::endl;

    float cali_bsCMass_error = 1;
    float rela_bsCMass_sigma = 1;
    float cali_bsCMass_sigma = 1;
    tree_output->Branch("calibrated_diMuon_bsConstrainedMass_error", &cali_bsCMass_error, "calibrated_diMuon_bsConstrainedMass_error/F");
    tree_output->Branch("relative_diMuon_bsConstrainedMass_sigma", &rela_bsCMass_sigma, "relative_diMuon_bsConstrainedMass_sigma/F");
    tree_output->Branch("calibrated_diMuon_bsConstrainedMass_sigma", &cali_bsCMass_sigma, "calibrated_diMuon_bsConstrainedMass_sigma/F");

    float abs_mu1_eta = 0.0;
    float abs_mu2_eta = 0.0;

    for (Long64_t i = 0; i < n_entries; i++)
    {
        tree_input->GetEntry(i);
        rela_bsCMass_sigma = rela_bsCMass_error * diMuon_bsConstrainedMass;
        cali_bsCMass_sigma = rela_bsCMass_sigma;

        abs_mu1_eta = std::fabs(mu1_eta);
        abs_mu2_eta = std::fabs(mu2_eta);

        // if (channel == "DY" || channel == "Data")
        //{
        for (const auto &bin : bins)
        {
            if (mu1_bsConstrainedPt > bin.muon1_pt_cut_low && mu1_bsConstrainedPt < bin.muon1_pt_cut_high &&
                abs_mu1_eta > eta_cuts[bin.region_1].first && abs_mu1_eta < eta_cuts[bin.region_1].second &&
                abs_mu2_eta > eta_cuts[bin.region_2].first && abs_mu2_eta < eta_cuts[bin.region_2].second)
            {
                cali_bsCMass_sigma = rela_bsCMass_sigma * bin.calibration_factors;
                break;
            }
        }
        //}

        cali_bsCMass_error = cali_bsCMass_sigma / diMuon_bsConstrainedMass;

        tree_output->Fill();
    }

    output_file.cd();
    tree_output->Write();
    output_file.Close();
    inputFile.Close();

    std::cout << "file in: " << output_file_path << std::endl;

    return 0;
}
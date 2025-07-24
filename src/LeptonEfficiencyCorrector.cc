#include "../lib/LeptonEfficiencyCorrector.h"


#include <algorithm>
#include <stdexcept>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>
#include <cassert>
#include <filesystem>
#include <cmath>

#include "correction.h"

/*
void LeptonEfficiencyCorrector::init(std::vector<std::string> files,
                                     std::vector<std::string> histos) {
    effmaps_.clear();
    if (files.size() != histos.size()) {
        std::cout << "ERROR! There should be one histogram per input file! "
                     "Returning 0 as SF."
                  << std::endl;
        return;
    }

    for (int i = 0; i < (int)files.size(); ++i) {
        TFile *f = TFile::Open(files[i].c_str(), "read");
        if (!f) {
            std::cout << "WARNING! File " << files[i]
                      << " cannot be opened. Skipping this scale factor "
                      << std::endl;
            continue;
        }
        TH2F *hist = (TH2F *)(f->Get(histos[i].c_str()))
                         ->Clone(("eff_" + histos[i]).c_str());
        hist->SetDirectory(0);
        if (!hist) {
            std::cout << "ERROR! Histogram " << histos[i] << " not in file "
                      << files[i] << ". Not considering this SF. " << std::endl;
            continue;
        } else {
            std::cout << "Loading histogram " << histos[i] << " from file "
                      << files[i] << "... " << std::endl;
        }
        effmaps_.push_back(hist);
        f->Close();
    }
}

void LeptonEfficiencyCorrector::setLeptons(int nLep, int *lepPdgId,
                                           float *lepPt, float *lepEta) {
    nLep_ = nLep;
    Lep_pdgId_ = lepPdgId;
    Lep_pt_ = lepPt;
    Lep_eta_ = lepEta;
}

float LeptonEfficiencyCorrector::getSF(int pdgid, float pt, float eta) {
    float out = 1.;
    float x = abs(pdgid) == 13 ? pt : eta;
    float y = abs(pdgid) == 13 ? fabs(eta) : pt;
    for (std::vector<TH2F *>::iterator hist = effmaps_.begin();
         hist < effmaps_.end(); ++hist) {
        WeightCalculatorFromHistogram wc(*hist);
        out *= wc.getWeight(x, y);
    }
    return out;
}

float LeptonEfficiencyCorrector::getSFAve(int pdgid, float pt, float eta,
                                          float weight) {
    float out = 0.;
    float x = abs(pdgid) == 13 ? pt : eta;
    float y = abs(pdgid) == 13 ? fabs(eta) : pt;
    int index = 0;
    for (std::vector<TH2F *>::iterator hist = effmaps_.begin();
         hist < effmaps_.end(); ++hist) {
        WeightCalculatorFromHistogram wc(*hist);
        index++;
        if (index == 1) {
            out += weight * wc.getWeight(x, y);
            // std::cout <<"1: "<<wc.getWeight(x,y)<<std::endl;
        } else if (index == 2) {
            out += (1. - weight) * wc.getWeight(x, y);
            // std::cout <<"2: "<<wc.getWeight(x,y)<<std::endl;
        } else
            out = -666.;
    }
    // std::cout <<"final: "<<out<<std::endl;
    return out;
}

float LeptonEfficiencyCorrector::getSFErr(int pdgid, float pt, float eta) {
    float out = 1.;
    float x = abs(pdgid) == 13 ? pt : eta;
    float y = abs(pdgid) == 13 ? fabs(eta) : pt;
    // float x = pt;
    // float y = abs(pdgid)==13 ? fabs(eta) : eta;
    for (std::vector<TH2F *>::iterator hist = effmaps_.begin();
         hist < effmaps_.end(); ++hist) {
        WeightCalculatorFromHistogram wc(*hist);
        out *= wc.getWeightErr(x, y);
    }
    return out;
}

const std::vector<float> &LeptonEfficiencyCorrector::run() {
    ret_.clear();
    for (int iL = 0, nL = nLep_; iL < nL; ++iL) {
        ret_.push_back(getSF((Lep_pdgId_)[iL], (Lep_pt_)[iL], (Lep_eta_)[iL]));
    }
    return ret_;
}
*/


//read run3 muon efficiency json files

using namespace std;
namespace fs = filesystem;

unique_ptr<correction::CorrectionSet> cset_L;
unique_ptr<correction::CorrectionSet> cset_M;
unique_ptr<correction::CorrectionSet> cset_H;

void LeptonEfficiencyCorrector::initializeCorrections(const std::string& year_num) {
    std::string basePath = "/afs/cern.ch/user/y/yulou/CMSSW_14_0_14/src/HToMuMu/data/leptonSF/";
    
    const std::vector<std::string> valid_eras = {"2022", "2022EE", "2023", "2023BPix"};
    
    if (std::find(valid_eras.begin(), valid_eras.end(), year_num) != valid_eras.end()) {
        basePath += year_num + "/";
    } else {
        throw std::runtime_error("Unsupported era: " + year_num);
    }    

    auto loadCorrectionSet = [](const std::string& path) -> std::unique_ptr<correction::CorrectionSet> {
        std::cout << "Loading JSON file: " << path << std::endl;
        if (!std::filesystem::exists(path)) {
            throw std::runtime_error("File not found: " + path);
        }
        return correction::CorrectionSet::from_file(path);
    };

    cset_L = loadCorrectionSet(basePath + "muon_JPsi.json.gz");
    cset_M = loadCorrectionSet(basePath + "muon_Z.json.gz");
    cset_H = loadCorrectionSet(basePath + "muon_HighPt.json.gz");

    std::cout << "Muon efficiency corrections initialized" << std::endl;
}

float LeptonEfficiencyCorrector::runner(const unique_ptr<correction::CorrectionSet>& cset,
          const string& key,
          const map<string, correction::Variable::Type>& example)
{
    correction::Correction::Ref sf = cset->at(key);
    vector<correction::Variable::Type> inputs;
    for (const correction::Variable& input: sf->inputs())
        inputs.push_back(example.at(input.name()));
    float result = sf->evaluate(inputs);

    return result;
}

float LeptonEfficiencyCorrector::give_eff(const string& type, float muon_pt, float muon_eta) {

    //"We recommend you to use the latest version of high-pT muon ID for the full Run-2 and Run-3 analyses"
    //Currently, we are use different Muon EFF for different muon pt.
    //SF type and pt range below, no EFF is provided for TRIG and ISO in low pt range
    static const map<string, map<string, pair<string, string>>> type_config = {
        {"TRIG", {
            {"low",  {"", "nominal"}},      
            {"medium",  {"NUM_IsoMu24_DEN_CutBasedIdMedium_and_PFIsoMedium", "nominal"}},
            {"high", {"NUM_HLT_DEN_MediumIDLooseRelIsoProbes", "nominal"}}
        }},
        {"ID", {
            {"low",  {"NUM_MediumID_DEN_TrackerMuons", "nominal"}},
            {"medium",  {"NUM_MediumID_DEN_TrackerMuons", "nominal"}},
            {"high", {"NUM_MediumID_DEN_GlobalMuonProbes", "nominal"}}  
        }},
        {"ISO", {
            {"low",  {"", "nominal"}},      
            {"medium",  {"NUM_LoosePFIso_DEN_MediumID", "nominal"}},
            {"high", {"NUM_probe_LooseRelTkIso_DEN_MediumIDProbes", "nominal"}}
        }}
    };

    std::string category;
    if (type.find("TRIG") != std::string::npos)       category = "TRIG";
    else if (type.find("ID") != std::string::npos)    category = "ID";
    else if (type.find("ISO") != std::string::npos)   category = "ISO";
    else return 0.0f; 

    std::string pt_range;
    // even the low pt require the pt > 3.0, but I think we don't need low muon pt EFFSF, just put it here now.
    if (muon_pt < 3.0)      return ((type.find("SFerr") != std::string::npos)
                                    ||(type.find("_s") != std::string::npos)) ? 0.0f : 1.0f;
    else if (muon_pt < 30)  pt_range = "low";
    else if (muon_pt < 200) pt_range = "medium";
    else                    pt_range = "high";

    if (pt_range == "low" && (category != "TRIG" || category != "ISO")) {
        return ((type.find("SFerr") != std::string::npos)
                    ||(type.find("_s") != std::string::npos)) ? 0.0f : 1.0f;
    }

    const auto& config = type_config.at(category).at(pt_range);
    const std::string& final_key = config.first;
    std::string scale_type = config.second; 

    if (type.find("stat") != std::string::npos)       scale_type = "stat";
    else if (type.find("syst") != std::string::npos)  scale_type = "syst";

    std::map<std::string, correction::Variable::Type> params = {
        {"pt", muon_pt}, {"eta", muon_eta}, {"scale_factors", scale_type}
    };

    //only for Muon_eff_SFerr_TRIG = sqrt(stat^2 + syst^2)
    if (type.find("eff_SFerr_TRIG") != std::string::npos) {

        float stat = 0.0;
        float syst = 0.0;
        scale_type = "stat";
        params = {{"pt", muon_pt}, {"eta", muon_eta}, {"scale_factors", scale_type}};
        if (pt_range == "low")       stat = runner(cset_L, final_key, params);
        else if (pt_range == "medium") stat = runner(cset_M, final_key, params);
        else                    stat = runner(cset_H, final_key, params);

        scale_type = "syst";
        params = {{"pt", muon_pt}, {"eta", muon_eta}, {"scale_factors", scale_type}};
        if (pt_range == "low")       syst = runner(cset_L, final_key, params);
        else if (pt_range == "medium") syst = runner(cset_M, final_key, params);
        else                    syst = runner(cset_H, final_key, params);

        float result = std::sqrt(stat * stat + syst * syst);

        return  result;
    } 

    if (pt_range == "low")       return runner(cset_L, final_key, params);
    else if (pt_range == "medium") return runner(cset_M, final_key, params);
    else                    return runner(cset_H, final_key, params);
}


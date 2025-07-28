#ifndef PhysicsTools_NanoAODTools_LeptonEfficiencyCorrector_h
#define PhysicsTools_NanoAODTools_LeptonEfficiencyCorrector_h

#include <iostream>
#include <string>
#include <vector>
#include <TH2.h>
#include <TFile.h>
#include <memory>    
#include <map> 

#include "WeightCalculatorFromHistogram.h"
#include "correction.h"

using namespace std;
namespace fs = filesystem;

extern std::unique_ptr<correction::CorrectionSet> cset;


class LeptonEfficiencyCorrector {
  public:

    LeptonEfficiencyCorrector() {effmaps_.clear();}
    //LeptonEfficiencyCorrector(std::vector<std::string> files, std::vector<std::string> histos);
    ~LeptonEfficiencyCorrector() {}

    void init(std::vector<std::string> files, std::vector<std::string> histos);
    void setLeptons(int nLep, int *lepPdgId, float *lepPt, float *lepEta);

    float getSF(int pdgid, float pt, float eta);
    float getSFAve(int pdgid, float pt, float eta, float weight); 
    float getSFErr(int pdgid, float pt, float eta);
    const std::vector<float> & run();

    //read run3 muon efficiency json files
    void initializeCorrections(const std::string& year_num);
    float runner(const unique_ptr<correction::CorrectionSet>& cset,
            const string& key,
            const map<string, correction::Variable::Type>& example
          );
    float give_eff(const string& type, float muon_pt, float muon_eta);
  

private:
  std::vector<TH2F*> effmaps_;
  std::vector<float> ret_;
  int nLep_;
  float *Lep_eta_, *Lep_pt_;
  int *Lep_pdgId_;
};

#endif

#include <cassert>
#include <filesystem>
#include <iostream>
#include <string>
#include "correction.h"

using namespace std;
namespace fs = filesystem;

void run (const unique_ptr<correction::CorrectionSet>& cset,
          const string& key,
          const map<string, correction::Variable::Type>& example)
{
    correction::Correction::Ref sf = cset->at(key);
    vector<correction::Variable::Type> inputs;
    for (const correction::Variable& input: sf->inputs())
        inputs.push_back(example.at(input.name()));
    double result = sf->evaluate(inputs);
    cout << "JSON result: " << result << endl;
}

int main ()
{
    ////////////////////////////
    // Example A: 2016postVFP //
    ////////////////////////////

    fs::path fname = "/afs/cern.ch/user/y/yulou/CMSSW_14_0_14/src/HToMuMu/data/leptonSF/2022/muon_Z.json.gz";
    cout << "Loading JSON file: " << fname << endl;
    assert(fs::exists(fname));
    unique_ptr<correction::CorrectionSet> cset =
                correction::CorrectionSet::from_file(fname.string());

    cout << "finish first" << endl;
    // TrackerMuon Reconstruction UL scale factor ==> NOTE the year key has been removed, for consistency with Run 3
    map<string, correction::Variable::Type> example {
        {"pt", 50.0}, // muon transverse momentum
        {"eta", -1.1}, // muon absolute pseudorapidity
        {"scale_factors", "nominal"}, // variation
    };
    run(cset, "NUM_MediumID_DEN_TrackerMuons", example);


    // Medium ID 2022 scale factor using eta as input
    example = {{"eta", -1.1}, {"pt", 45.0}, {"scale_factors", "nominal"}};
    run(cset, "NUM_MediumID_DEN_TrackerMuons", example);

    // Medium ID 2022 scale factor using eta as input ==> Note that this value should be the same
    // as the previous one, since even though the input can be signed eta, the SFs for 2022 were
    // computed for |eta|. This is valid for ALL the years and jsons
    example["eta"] = 1.1;
    run(cset, "NUM_MediumID_DEN_TrackerMuons", example);

    // Trigger 2022 systematic uncertainty only 
    example = {{"eta", -1.8}, {"pt", 54.0}, {"scale_factors", "syst"}};
    run(cset, "NUM_IsoMu24_DEN_CutBasedIdMedium_and_PFIsoMedium", example);
    
    fname = "/afs/cern.ch/user/y/yulou/CMSSW_14_0_14/src/HToMuMu/data/leptonSF/2022/muon_HighPt.json.gz";
    cout << "Loading JSON file: " << fname << endl;
    assert(fs::exists(fname));
    cset = correction::CorrectionSet::from_file(fname.string());


        // TrackerMuon Reconstruction UL scale factor ==> NOTE the year key has been removed, for consistency with Run 3
    example = {
        {"pt", 250.0}, // muon transverse momentum
        {"eta", -1.1}, // muon absolute pseudorapidity
        {"scale_factors", "nominal"}, // variation
    };
    run(cset, "NUM_MediumID_DEN_TrackerMuons", example);


    // Medium ID 2022 scale factor using eta as input
    example = {{"eta", -1.1}, {"pt", 245.0}, {"scale_factors", "nominal"}};
    run(cset, "NUM_MediumID_DEN_TrackerMuons", example);
    
    
    return 0;
}

This code is based in the Run2 Analysis https://github.com/irenedutta23/HmmAna

## Setup

```
cmsrel CMSSW_14_0_14
cd CMSSW_14_0_14/src
cmsenv
git clone git@github.com:MatBarria/HmmAnalysis.git
cd HmmAnalysis
make -j4
```

## Run the analyzer 
For simulations
```
./bin/HmmAnalyzer runList.txt out.root mc F 2016
```

For data
```
./bin/HmmAnalyzer runList.txt out.root data T 2016
```

## Run CreateHistograms 

This will create a root file with the histogrmas filled with the corresponding weights.

For data/simulation
```
./bin/HmmAnalyzer analyzer_output.root output_directory era channel T(data)/F(simulation)
```

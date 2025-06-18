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

To run over all the data sets look at condor/README.md to run it in condor jobs

## Run CreateTuples

This will create a root file with tuples with all the usefull variables and the correspodeting weights;

For data/simulation
```
./bin/CreateTuple analyzer_output.root output_directory era dataset T(data)/F(simulation) T(signal)/F(Bkg-data)
```


To run over all the data sets look at condor/README.md to run it in condor jobs.   
If you want to run it over a small dataset look at scripts/README.md

## BDT Training
Look at python/xgboost/README.md

## Plotting 
All plotting codes are located at plot_macros/

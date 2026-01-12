### Statement
Author: Yuyang
This work is based on HtoMuMu github branch - main in yuyang's repo, which is modified from Matias' repo from FinalFit. And yuyang updates it for run2 and run3 significance combination.

# Run2 & Run3 significance combination

After building datacard root workspace for Combine, we can compute significance of different categories, and try combining Run2 and Run3 significance. However, although we can compute Run3 datacard in CMSSW_14_X environment, I failed to reproduce Run2 significance using Run2 [datacards](https://gitlab.cern.ch/cms-analysis/hig/HIG-19-006/datacards/-/tree/master?ref_type=heads) in CMSSW_14, because of the different version of Combine and RooMultipdf functions in Run2. 

Therefore, we turn to find a version of CMSSW where we can run both Run2 and Run3 datacards, which is done successfully by others. After trying different versions of CMSSW, now we can run both Run2 and Run3 in CMSSW_11_3_4. You can use the following commands:

```
cmssw-el7
cmsrel CMSSW_11_3_4
cd CMSSW_11_3_4/src
cmsenv
git -c advice.detachedHead=false clone --depth 1 --branch v9.2.1 https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit

git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester
cd CombineHarvester
git checkout v2.1.0
# The v2.1.0 tag should be used in CMSSW_11_3_X, v3.0.0 for CMSSW_14_X. --https://github.com/cms-analysis/CombineHarvester

cd ${CMSSW_BASE}/src
git clone https://github.com/VMoonLightV/flashggFinalFit.git
# or for ssh: git clone git@github.com:VMoonLightV/flashggFinalFit.git

# to add pdfs in run2 datacard:
cp -f flashggFinalFit/tools/classes.h HiggsAnalysis/CombinedLimit/src/classes.h
cp -f flashggFinalFit/tools/classes_def.xml HiggsAnalysis/CombinedLimit/src/classes_def.xml
cp -f flashggFinalFit/tools/HMuMuRooPdfs.cc HiggsAnalysis/CombinedLimit/src/HMuMuRooPdfs.cc
cp -f flashggFinalFit/tools/HMuMuRooPdfs.h HiggsAnalysis/CombinedLimit/interface/HMuMuRooPdfs.h

scram b clean
scram b -j 8

cd flashggFinalFit/
source setup.sh
```

Then you can follow Matias' instruction of BDT training, I copied the Mass Fit section here.
* The code above can't be compiled successfully in CMSSW_14_0_14 due to different version of Combine and RooMultipdf functions. If you want to run Combine in CMSSW_14_0_14, go to [Matias' instruction](https://github.com/MatBarria/flashggFinalFit#): 


### Mass fits code

The code is now in my personal git account, you can move it to the organization if you want. However, if you want to change the name of the repo you will have to modify the code because the repo name is hardcoded in some file.

#### Fits 
Once you have cloned the code (don't forget to run source setup.sh each time you close your lpc session), you can execute all the mass fits just by running the script. 
<span style="color:red"> IMPORTANT: My paths are still hardcoded here, this must be changed!. For now, update manually the paths in the following files(changes what is before/HToMuMu/)

- ./run_fits.sh : 4 paths, lines 11, 18, 24, 30.
- ./Signal/config_tutorial_combined.py : line 9
- ./Signal/config_tutorial_combined_VBF.py : line 9
- ./Background/config_tutorial.py : line 7
- ./Background/config_tutorial_VBF.py : line 7
- ./Datacard/generate_datacards.sh : line 74, 92
If there are other paths, please change them as well.

```
bash run_fits.sh 
```

This will generate all the necessary fits and will save them in `flashggFinalFit/Signal/outdir_packaged`, `pflashggFinalFit/Background/outdir_tutorial`, and `flashggFinalFit/Plots/plots_tutorial`. 
Also, will create Datacards in this path: `flashggFinalFit/Datacard`

To understand what the scripts do, please read the whole [Tutorial](https://gitlab.cern.ch/jspah/higgsdna_finalfits_tutorial_24/-/tree/master/07_FinalFits?ref_type=heads) mentioned before. Also, [here]( https://www.notion.so/Higgs-To-MuMu-c33f76b4fe0845869da467b6a4c4da0d?p=1f2b56b1870b8082aa86d1465bc6941c&pm=s ) is a list of all the commands individually in case you want to execute them one by one to debug something

#### Significance and Limits.
The overall commands are listed in the end of this part.

To calculate the limits, first do:

```
cd Combine
mkdir -p Models/signal
mkdir -p Models/background
cp ../Signal/outdir_packaged/CMS-HGG_sigfit_packaged*.root Models/signal/
cp ../Background/outdir_tutorial/CMS-HGG_multipdf*.root Models/background/
cp ../Datacard/Datacard_tutorial*.txt .
```

This will move the root files with the fits and the datacards to the right directory.

To go from datacarts.txt to datacards.root do:
```
python3 RunText2Workspace.py --mode mu_inclusive --batch local --ext _tutorial_(category)
```

where categorie can be ggH,,ggHcat1, gHcat2, gHcat3, VBF, VBFcat1, VBFcat2, VBFcat3, VBFcat4.

Then obtain the significance by running. 
```
combine -M Significance Datacard_tutorial_(category)_mu_inclusive.root -m 125 -t -1 --expectSignal 1
```

And for the asymptotic limits:
```
combine -M AsymptoticLimits Datacard_tutorial_(category)_mu_inclusive.root -m 125 -t -1 --run blind
```

All above Combine steps can be done by running:
```
cd Combine
bash run_workplace.sh
bash run_sig.sh
bash run_asym.sh
```

The **run_sig.sh** or **run_asym.sh** will generate a table with time(YYYYMMDD_HHMMSS) in its title.




## Attention!
Note that here are some differences:
#### 1 Combine command
In CMSSW_14_X, our initial Combine command for Run3 datacards is: (Let's call it Command 1, this is what we use in **run_sig.sh**)
```
combine -M Significance Datacard_tutorial_(category)_mu_inclusive.root -m 125 -t -1 --expectSignal 1
```

But in Run2, we use this command for Run2 ggH+VBF datacards: (Command 2)
```
combine -M Significance -d Datacard_tutorial_(category)_mu_inclusive.root -m 125  --cminDefaultMinimizerStrategy 1  -t -1  --toysFrequentist --expectSignal 1 --X-rtd FITTER_NEWER_GIVE_UP --X-rtd FITTER_BOUND --cminRunAllDiscreteCombinations --setParameterRanges r=-10,10 --X-rtd MINIMIZER_freezeDisassociatedParam --cminDefaultMinimizerTolerance 0.01 --X-rtd MINIMIZER_MaxCalls=9999999 --X-rtd FAST_VERTICAL_MORPH
```

As you see, this one is much more complicated with detailed settings, which are required to fit successfully. But here raises another problem: this command is too complicated to run Run2+Run3_ggH+VBF datacard(cost too much time). Thus you may just use this command instead: (Command 3)
```
combine -M Significance Datacard_tutorial_Run2_Run3_ggH_VBF_mu_inclusive.root -m 125 -t -1 --expectSignal 1 --cminDefaultMinimizerTolerance 0.01 --toysFrequentist
```

Compared to **"Command 1"**, we add this two [Combine settings](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part3/runningthetool/), which account for 99% of the significance difference between **Command 1 & Command 2**. (A detailed test of it is recorded in yuyang's Sep.29th slide) :

* **--toysFrequentist**: generate the toy datasets after fitting based on μ=1 instead of μ=0, involved the signal’s influence on background model.
  *  *The nuisance parameters in each toy are set to their nominal values which are obtained after first fitting to the observed data, with the POIs fixed, before generating the toy data sets. For evaluating likelihoods, the constraint terms are instead randomized within their PDFs around the post-fit nuisance parameter values.*
* **--cminDefaultMinimizerTolerance 0.01**
  * *Set the default minimizer tolerance, the default is 0.1.*

Here show the difference of difference Commands for 2022+23+24 data and 2023BPix signal sample:

| Sig. in CMSSW_11 | Command 2 (and Sig. in AN2019) | Command 1 (and Sig. in CMSSW_14) | Command 3 (with 2 key parameters) |
| :---: | :---: | :---: | :---: |
| Run2_ggH | 1.57574 (**1.56**) | 1.94943 | 1.57024 |
| Run2_VBF | 1.79575 (**1.77**) | 1.76866 | 1.79575 |
| Run2_ggH_VBF | 2.38605 | 2.62499 | 2.38611 |
| Run3_ggH | 2.32657 | 2.32711 (**2.21621**) | 2.33595 |
| Run3_VBF | 2.08192 | 2.14455 (**2.07891**) | 2.08199 |
| Run3_ggH_VBF | 3.12104 | 3.31713 (**3.25787**) | 3.11514 |
| Run2+Run3 ggH+VBF | TBD (cost too much time) | 4.22939 | 3.91095 |

#### 2 Current datasets to run BDT and Combine
Currently, we are using 2022+23+24 data and 2023BPix signal sample to run BDT, the signal sample will be rescale. And the lumi-map is in **flashggFinalFit/tools/commonObjects.py**, you can change the lumi if you need. 

**Latest update**: In lumi-map we are using "combine: 234.35" with 2025 data, the significance using Command 3 (Run3 command with 2 key parameters) is about 4.8$\sigma$.

### Impact
After you have the Rooworkspace files generated from datacards, you can start to draw Impact plots for each category. You can just run the following command:
```
cd ./Impact
bash Run_Impact.sh
```
This command includes following steps after copying workspace root files into ./Impact:
1. Do initial fit:
    combineTool.py -M Impacts -d "\$WORKSPACE" -m "\$MASS" --doInitialFit --robustFit 1 -t -1 --setParameters r=1 --setParameterRanges r=0,2 \$COMMON_OPTS --freezeParameters MH
2. Fit all:
    combineTool.py -M Impacts -d "\$WORKSPACE" -m "\$MASS" --doFits --robustFit 1 -t -1 --setParameters r=1 --setParameterRanges r=0,2 \$COMMON_OPTS --freezeParameters MH --parallel "\$N_CORES"
3. Collect all fit results and output to JSON file
    combineTool.py -M Impacts -d "\$WORKSPACE" -m "\$MASS" -o "\$JSON_OUTPUT"
4. Draw Impact plots
    plotImpacts.py -i "\$JSON_OUTPUT" -o "\$PLOT_OUTPUT"

Note that each category may cost more than half an hour or 2 hours to run. The "Run2+Run3_ggH+VBF" may take more than 10 hours (I never finished it hhh). You can use more cpu cores by change the "N_CORES" parameter in the bash script.

#### Existing issues
The Run3 ggH related Impact plot have zero value in the 1st line of run2+run3_ggH and run3_ggH_VBF plots, maybe some problems with run3 ggH PDFs.
This code do the BDT training for the ggH Categorization.

## First use

Go to https://uscms.org/uscms_at_work/computing/setup/gpu.shtml and follow the EAF instructions.

When you are in do 

```
"${SHELL}" <(curl -L micro.mamba.pm/install.sh)
micromamba create -n xgboost_env xgboost python=3.10 krb5  curl cfitsio root tensorflow keras -c conda-forge
pip3 install pandas 
pip3 install uproot
pip3 install matplotlib
pip3 install graphviz
pip3 install mplhep
pip3 install gpustat

```

## How to run

Pick your node https://analytics-hub.fnal.gov/hub/home and activate the enviroment
```
eval "$(micromamba shell hook --shell bash)"
micromamba activate xgboost_env
```
Go to the xgboost directory

```
cd /your_path/HmmAnalysis/python/xgboost
```
Run the training (Make your you generate the skim tuples first)
```
python3 train.py era
```

2017 nanoAOD:

MC: https://github.com/irenedutta23/HmmAna/blob/master/data/nanoAODlist_2017_MC.txt
files are in directory: /mnt/hadoop/store/mc/RunIIFall17NanoAODv4

Data:

/mnt/hadoop/store/data/Run2017B/SingleMuon/NANOAOD/Nano14Dec2018-v1  
/mnt/hadoop/store/data/Run2017C/SingleMuon/NANOAOD/Nano14Dec2018-v1  
/mnt/hadoop/store/data/Run2017D/SingleMuon/NANOAOD/Nano14Dec2018-v1
/mnt/hadoop/store/data/Run2017E/SingleMuon/NANOAOD/Nano14Dec2018-v1
/mnt/hadoop/store/data/Run2017F/SingleMuon/NANOAOD/Nano14Dec2018-v1

2018 nanoAOD:

MC: https://github.com/irenedutta23/HmmAna/blob/master/data/nanoAODlist_2018_MC.txt
files are in directory: /mnt/hadoop/store/mc/RunIIAutumn18NanoAODv4

Data: 
/mnt/hadoop/store/data/Run2018A/SingleMuon/NANOAOD/Nano14Dec2018-v1  
/mnt/hadoop/store/data/Run2018B/SingleMuon/NANOAOD/Nano14Dec2018-v1  
/mnt/hadoop/store/data/Run2018C/SingleMuon/NANOAOD/Nano14Dec2018-v1
/mnt/hadoop/store/data/Run2018D/SingleMuon/NANOAOD/22Jan2019_Nano14Dec2018-v1

# Correction types
btagSF:

leptonSF:

pileup:

Rocco:

# Corrections plottings
```bash
ssh -Y -L localhost:8888:localhost:8888 <FNALuser>@cmslpc-el8.fnal.gov
cd nobackup/CMSSW_14_0_14/src
cmsenv
cd HmmAnalysis
jupyter notebook --no-browser --port=8888
```
Then copy the http://localhost:8888/?token=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX into your browser

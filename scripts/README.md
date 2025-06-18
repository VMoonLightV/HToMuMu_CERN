## Scripts
**All this scripts must be run in the main directory HToMuMu**

### Skim tuples ggH/VBF
Run the skim tuples code over a list of datasets.   
You can change the datasets changing the lists `eras`, `background_datasets`, and `signal_datasets` in the script.

Run
```
python3 ./scripts/run_skim_ggH.py 
python3 ./scripts/run_skim_VBF.py 
```

### Run Create tuples 
Run the Createtuples code over a list of datasets.   
You can change the datasets changing the lists `eras`, `data_datasets`, `background_datasets`, and `signal_datasets` in the script.

Run 
```
python3 ./scripts/run_tuple.py
```

### Copy tuples in the eos space
Copy the analyser tuples from an space to user eos space (/lpchmumu/$USER/).

Run 
```
bash ./scripts/cp_script.sh source_user data_set_type
```
`source_user`: EOS username of the person you're copying from
`data_set_type`: One of `Data`, `MC_background`, or `MC_Signal`

### Split tuples
This generate a root file with the tuples necesary for the mass fits.

#### Step 1: Merge (hadd) tuples with BDT scores

Update the `path` variable in `hadd_bdt.sh` to point to your ROOT files.

Run 
```
bash ./scripts/hadd_bdt.sh
```

#### Step 2: Generate split ROOT files  
This step processes the merged tuples and generates ROOT files for mass fitting.

Before running, update the following variables insde `split_tuples.py`:
- `data_type`: Set to either `signal` or `data`
- `channel`: Set to either `ggH` or `VBF`

Run
```
python3 ./scripts/split_tuples.py
```

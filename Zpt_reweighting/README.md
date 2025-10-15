AN2019 - 4.5.Correction to Zpt: Reweight dimuon pt of MC based on Z boson pt. The correction function is derived from ZCR(70-110GeV), then applied to SR(110-120, 130-150GeV) to have a better agreement between data and MC in dimuon_pt distribution. 

The instruction works on *_tuples.root, the related scripts are in ./Zpt_reweighting.

1. Currently, run3 muon efficiency hasn't been done before creating tuples, so I add ID and ISO efficieencies while divide the tuples into different regions (and Njet group).
* This step retains all parameters in the tuple files.
* Maybe this muon efficiencies will be added while creating the tuples in the future. 
split njet and region 
* In each era, we divide events into 3 groups: 
    * Njet = 0, =1, >=2. 
* Or you can do it inclusively without jet binning 

we are not sure which we will use finally, you can use "bin or nobin" to chose it.
```
python3 "run_eff_on_tuple_region.py"  bin(or nobin)  SR(or ZCR)
```

2. Plot ZCR vars and count to do ZCR DY normalization 
* Normalize DY with data/MC in ZCR for each era and Njet group 
    * Just make sure data and MC_bkg have same events counts. 
    * The count file is produced by "plot_sim_vs_data_general.py"
    * The events count table is saved in "scripts/event_counts_{region}.csv" by default

```
python3 "plot_sim_vs_data_general.py" bin(or nobin)  ZCR
Some plot region: ZCR, ZCR_normalization, ZCR_self_reweighting, SR, SR_reweighting

python3 "normalization.py" bin(or nobin)  "count_file_name"
```

3. Plot ZCR_normalization and fitting corr_func, you can see the fitting curve in the ZCR_normalization dimuon_pt plot.
* Fit the ratio of dimuon_pt in ZCR with polynominal. 
    * Define different polynominal in different dimuon_pt range:
    * In [0,100]: 6-th; in [100, 250]: 3-th; in [250, 600]: 3-th.
    * We will only use [0, 250] finally.
    * the function info is saved in:
        * ../plots/ratio/njet/{njet}jet_ratio_table_dimuon_pt_{region}/polynomial_{era}_coefficients.csv
```
python3 "plot_sim_vs_data_general.py" bin(or nobin) ZCR_normalization
```

4. Apply the reweighting to ZCR itself and SR
* Apply the correction function to SR events. 
    * weight = weight * Func_cor(dimuon_pt)

```
python3 "reweighting_Zpt.py" bin SR_reweighting(or ZCR_self_reweighting)
```


### Statement
Author: Yuyang
This work is based on HtoMuMu github branch - yuyang-work.
# Mass reso Calibratiion
"The sensitivity of the research depends on the resolution of the Higgs boson mass peak. --AN2019" As dimuon mass resolution can potentially improve S-B discrimination, we study the mass resolution in Run3 and perform calibration using similar methods in Run2.

* We use beam-spot constrained muon momentum measurements.
* To perform mass resolution calibration, we categorize events based on leading muon pT and eta region combination of muon1 and muon2:
    * Leading muon pT bins: [26,45,52,62,200]
    * Muon1 & Muon2 |η| bins: [0, 0.9, 1.8, 2.4] , defined as “B, O, and E”
* In each category, we fit the data mass spectrum using a Voigtian function.
* Obtain calibration factor by comparison fitted $\sigma$ with median estimated $\sigma$ value in each category.

The calibration factor is derived from Z boson control region (75 < ${m_{\mu\mu}}$ < 105 GeV). We use the calibration factor from DY sample to calibrate all MC samples. 
1. We split the events by Muon1 pT and eta region combination of Muon1 and Muon2. This step will generate **relative_diMuon_bsConstrainedMass_sigma** and save them into the **../root_io/tuples/EVE_pt_eta/ZCR_75-105/{channel}_{era}_skim.root**.

    ```
    python3 ./EVE_mass_reso/muon_eta_split.py
    ```


2. In each category, we calculate the median value of the dimuon mass resolution ($\sigma_{estimated}$) to represent this category. This step will draw plots of median $\sigma_{estimated}$ of each category of the same pT range in **../plots/{plot_version}/{channel}/{era}/**, and the $\sigma_{estimated}$ of different categories will be saved into BCS_Z_mass_multi_median_{var_label}.csv.
    * by default, **plot_version** = "EVE_resolution_voigtian_merge_lowPt"
    ```
    python3 ./plot_macros/plot_diMuon_mass_multi_reso.py
    ```
    By the way, our initial dimuon mass resolution is computed by muon pT and pT error: 
$$
\frac{\sigma_{m_{\mu\mu}}}{m_{\mu\mu}} = \sqrt{\left(\frac{\sigma_{p_{T,1}}}{p_{T,1}}\right)^2 + \left(\frac{\sigma_{p_{T,2}}}{p_{T,2}}\right)^2}
$$

2. Then in each category, we fit the Z peak using a voigtian function, and take the $\sigma$ from it as $\sigma_{measured}$. This step will draw plots of fitting Z peak in **../plots/{plot_version}/{channel}/{era}/** for each pT-eta bin, and the $\sigma_{measured}$ of different categories will be saved into **BSC_Z_mass_reso_results.csv**.
    ```
    python3 ./plot_macros/plot_diMuon_mass_peak_EVE.py
    ```
    Note: We use fitting_width=4GeV, which will be saved in the table as well. If the fitting_width is not enough to fit, we will rise it 1 GeV by 1 GeV until 10 GeV
<br>

3. Next, we calculate the the calibration factor as $\sigma_{measured}/\sigma_{estimated}$ i each pT-eta bin. The calibration factor of different categories will be saved into ../plots/{plot_version}/{channel}/{era}/**BSC_Z_mass_reso_factors.csv**.
    ```
    python3 ./EVE_mass_reso/make_calibration_factor.py
    ```
    Note that my calibration factors range from 0.5~0.7. (In Run2 AN2019, the factors mainly range from 1.0~1.3)
<br>

4. With calibration factors, we can calibrate the $\sigma_{estimated}$ to $\sigma_{calibrated}$ (called "calibrated_diMuon_bsConstrainedMass_sigma") now. 
    ```
    python3 ./EVE_mass_reso/EVE_mass_reso_calibration.py
    ```

5. After calibration, we can plot $\sigma_{measured}$ vs $\sigma_{estimated}$ to confirm that the calibration works well. These plots will be saved in **../plots/{plot_version}/**.
    ```
    python3 ./EVE_mass_reso/plot_reso_binning_EVE.py
    ```

6. Finally, we can check the $\sigma/\mu$ distribution in the ZCR and SR to see the performance of calibration.
    ```
    python3 ./plot_macros/*
    ```
    * However, this doesn't work as well as Run2, our $\sigma/\mu$ distribution has worse data/MC agreement after calibration.

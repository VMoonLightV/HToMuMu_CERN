#!/bin/bash

if [[ $# -ne 1 ]]; then
    echo "Use Channel Under Study as argument only!"
    exit
fi
HIGGS_CHANNEL=$1

## declare an array variable
declare -a bkg_subset=("Full")
#declare -a bkg_subset=("Full" "NoDY50")
# declare -a sig_subset=("Full" "NottH" "VBF")
declare -a sig_subset=("NottH")
#declare -a sig_subset=(${HIGGS_CHANNEL})
# declare -a eras=("2022" "2022EE" "2022Combined" "2023" "2023BPix" "2023Combined" "Combined")
declare -a eras=("Combined")
#declare -a eras=("2023BPix")

#declare -a tuples=("Data" "DY" "DY120to200" "EWK" "TT" "Top" "DiBoson" "TriBoson" "ggH" "VBF" "ttH" "VH")
declare -a tuples=("Data" "DY" "EWK" "TT" "DiBoson" "ggH" "VBF" "ttH")
#declare -a tuples=("ggH" "VBF" "ttH")

# now loop through the above array
for bs in "${bkg_subset[@]}"; do
    for ss in "${sig_subset[@]}"; do
        echo "--------- B ${bs} - S ${ss} ---------"
        for era in "${eras[@]}"; do
            python3 train.py ${HIGGS_CHANNEL} ${era} ${bs} ${ss}

            #for type in "signal" "background" "data"; do
                #echo "         --- ${era} Skim ${type} ---"
                #python3 append_xgboost_discriminator_to_tree.py ${HIGGS_CHANNEL} ${era} Combined ${type} ${bs} ${ss} --skim
            #done

            # Add BDT to tuples
            for type in "${tuples[@]}"; do
                echo "         --- ${era} Tuples ${type} ---"
               	#python3 append_xgboost_discriminator_to_tree.py ${HIGGS_CHANNEL} ${era} Combined ${type} ${bs} ${ss}
            done
        done
    done
done

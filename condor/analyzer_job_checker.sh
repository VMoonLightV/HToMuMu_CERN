#!/bin/bash

###############################
# Define input parameters
###############################
ANALYZER_VERSION_NUMBER=$1



DIR="analyzer_HiggsMuMu_v$ANALYZER_VERSION_NUMBER"

#for file in "$DIR"/*/err/*.err; do

# Output file for failures
OUTFILE="error_datasets.txt"
> "$OUTFILE"  # clear it at start

fail_count=0

for block in "$DIR"/*; do
    echo "Checking $block files"
    blockError=false
    nFilesExpected=$(tail -n 2 $block/task.jdl | head -n 1)
    #echo "$nFilesExpected expected files"
    nFilesOut=$(ls $block/out/ | wc -l)
    #echo "$nFilesOut out files"

    if [[ "$nFilesExpected" == *"Queue"* ]]; then
        nFilesExpected=1
    fi
    
    if [ $nFilesExpected -ne $nFilesOut ]; then
        #echo "************** Not all analyzer ran in $block **************"
        blockError=true
        ((fail_count++))
        missingFiles=$((nFilesExpected - nFilesOut))
        echo "$block has $missingFiles missing files" >> "$OUTFILE"
    fi

    #expectedFileNum=0
    for file in "$block"/err/*.err; do
        # Skip if no .err files exist
        [ -e "$file" ] || continue

        # Count lines (change to wc -c if you meant bytes instead)
        count=$(wc -l < "$file")
        #echo "File $file count $count"

        last_line=$(tail -n 1 "$file")

        if [[ "$last_line" != "cp: cannot stat 'data/pileup/*.root': No such file or directory" ]]; then
            blockError=true
            ((fail_count++))
            echo "$file" >> "$OUTFILE"
        fi

        #if [ "$count" -ge 7 ]; then
        #    #echo "File '$file' has length $count (greater than 6)"
        #    blockError=true
        #    ((fail_count++))
        #    echo "$file" >> "$OUTFILE"
        #fi

    done

    if $blockError; then
        echo "************** Errors found in $block **************"
    fi

done

if [ "$fail_count" -eq 0 ]; then
    echo "No extra errors were thrown in any jobs"
    rm -f "$OUTFILE"
else
    echo "There are errors check $OUTFILE for a list of problematic eras"
fi

## How to run
1. Make sure you have generated the list of runs of a dataset from `../list/makeListFromDAS_Run3.py`.
2. Add/remove/update dataset list in `create_analyzer_jobs_LPC.py` using the corresponding `.list` file as the key.
3. Run `python3 create_analyzer_jobs_LPC.py`. This will create an analyzer directory with a subfolder for each dataset in the list.
    - To submit a single job, run `condor_submit task.jdl` inside the corresponding dataset directory. Note that the output of step 2 provides a one-line command to do this!
    - You can also run `bash condor_job_sender.sh` to send the jobs for all of the new datasets!
    - After the jobs have run, run `analyzer_job_checker.sh` in order to see if there were errors with any of the datasets. The problematic datasets are stored in an output text file. 
4. Once all jobs have finished, you might want to add the created tuples in order to compute the total SumGenWeight. To do so, run `python3 condor_job_hadd.py`. This will send a job that does hadd over all datasets listed in `condor_job_sender.sh`.
    - In case of having missing runs inside a dataset, a new 'job sender' will be created with the missing files only. Run with `bash condor_job_sender_missing_files.sh`.
    - If you want to hadd a specific list of datasets, you can hardcode them inside the `condor_job_hadd.py` macro.
    > Note that this hadd macro includes the extended runs (i.e. those with the suffix `_ext1`) to the final file!
5. Re-run `condor_job_hadd.py` to check if the final tuples were correctly saved.
    - If a dataset couldn't be hadded, you can try manually with the command line prompted.

## How to run histos
1. Run `python3 create_histo_jobs_LPC.py`. 
    - To submit run `bash condor_histo_job_sender.sh` to send the jobs

## Considerations
- The `/err/` folder in each dataset directory contains the error output of each job. Don't worry if there is a short list of missing files, since they were added in case you want to run the process manually. In some cases there might be missing branches from problematic runs that can be ignored. Any other error message might need to be reviewed.
- The `/out/` folder contains the output info. Inside the corresponding `.out` file you will find the final tuples path!

# HGProducer

Description of the HGProducer script, to submit the generation of samples to HTcondor at LXplus.

It provides the following functionalities:

* cmsDriver: generation of GEN/SIM/DIGI/RECO samples using sequences of cmsDriver.py
* cmsRun: execution of cmsRun, providing an input python file



All functionalities can be tested before submission by using the dryrun option (which generates locally 10 events according to the defined sequences).

### Input/output files

Only a single script scripts/hgSubmit.py is necessary and can be executed within any CMS scram environment. The input script contains all the necessary information about the submission (e.g. number of jobs/events for GEN step, input dataset, ...).

Each job runs in a specific directory,being

```
$rundir/submission/$jobID/
```
where $rundir is the run directory as given in the input file (cfg_run_dir) and $jobID the number of the jobs (from 0 to cfg_njobs). 


The output ROOT files are stored in the cfg_storage_dir directory (can be EOS). For each step in the cmsDriver (or NANOProducer using cmsRun), a file is created with prefix the job ID number. E.g.: 0001_GEN-SIM.root, 0008_DIGI.root, 0111_RECO.root, 0111_NANO.root  etc.)

### How to run

The submission script in scripts/hgSubmit.py has the following options:

```
python scripts/hgSubmit.py -i <path to input> --args
```

The args have the following options:
* --dryrun
* --submit
* --status
* --resubmit --jobids=<job id string>
* --jobflavor=<CONDOR job flavors> (only for submission)

All the configuration (number of events, jobs, storage and run dir, ...) is stored in the input file (see input directory for examples).


### Examples

Three examples are provided in the input directory:
* electron_E100GeV_z.py: generation of 1000 events GEN/SIM/DIGI/RECO, stored in the EOS space. Three cmsDriver sequences are subsequently executed in the same job: GEN-SIM, DIGI and RECO, and will be stored in respectively GEN-SIM.root, DIGI.root and RECO.root (according to the cmsDriver command names).
* electron_E100GeV_z_RECO.py: only perform RECO step, on previously generated dataset, based on the output of the previously created DIGI step (DIGI.root). No need to provide njobs or nevents, it will figure it out from the input dataset.
* electron_E100GeV_z_NANO.py: NANO plugin producer. It relies on an additional config file which configures the NANO skim. Crucial in this file is the precense of input.root and output.root in the process.source and process.output respectively. The submission script will automatically overwrite these in/output ROOT files with the proper ROOT files according to the input dataset

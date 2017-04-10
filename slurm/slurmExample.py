#! /bin/env python

## Example usage of slurmTools
## Run `python slurmExample.py`

from cp3_llbb.CommonTools.slurmTools import slurmSubmitter

## Create an instance of the submitter for
## - sample n.2129
## - 10 files per job
## - specifying: * path to the executable (relative to where this script is launched)
##               * folder where the inputs/outputs/logs will be stored
##               * rescale MC
##               * maximum runtime of 1h
##               * maximum memory per cpu of 2GB

samples = [
        {
            "ID": 2129,
            # Either specify ID *OR* DB name
            #"db_name": "ST_t-channel_4f_leptonDecays_13TeV-amcatnlo_MiniAODv2_v1.0.0+7415_TTAnalysis_12d3865",
            "files_per_job": 10,
            # Optional: specify a path to a "json skeleton" that will be filled and used for this sample (see below)
            #"json_skeleton": "myJson.json",
        }
    ]

mySub = slurmSubmitter(samples, "<path to plotter / skimmer exe>", "test_slurm/", rescale=True, runtime="60", memory=2000)

## Create test_slurm directory and subdirs
mySub.setupDirs()

## Write command and data files in the slurm directory
mySub.createFiles()

## Actually submit the jobs
## It is recommended to do a dry-run first without submitting to slurm
#mySub.submit()


## Example Json skeleton: the field "#DB_NAME#" will be filled by slurmSubmitter.
## You can specify anything else you want that will be passed to createHistoWithtMultiDraw
## for this particular sample.
#{
#    "#DB_NAME#": {
#        "tree_name": "t",
#        "sample_cut": "1.",
#        # Optional:
#        # A job ID will be appended at the end of the name.
#        # If you have multiple runs, be sure to be change the name for each run in your python plot config.
#        "output_name": "output.root"
#    }
#}

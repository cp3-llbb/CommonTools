## Example usage of condorTools
## Run `python condorExample.py`

from condorTools import condorSubmitter

## Create an instance of the submitter for
## - sample n.517
## - 20 files per job
## - specifying: * path to the executable (relative to where this script is launched)
##               * path to the plot configuration python/JSON (relative to where this script is launched)
##               * folder where the inputs/outputs/logs will be stored

samples = [
        {
            "ID": 517,
            # Either specify ID *OR* DB name
            #"db_name": "ST_t-channel_4f_leptonDecays_13TeV-amcatnlo_MiniAODv2_v1.0.0+7415_TTAnalysis_12d3865",
            "files_per_job": 10,
            # Optional: specify a path to a "json skeleton" that will be filled and used for this sample (see below)
            #"json_skeleton": "myJson.json",
        }
    ]

mySub = condorSubmitter(samples, "build/createHistoWithMultiDraw.exe", "plots/TTAnalysis/generatePlots.py", "test_seb/")

## Create test_condor directory and subdirs
mySub.setupCondorDirs()

## Write command and data files in the condor directory
## Set createHadd to True to create a bash script to run when the jobs are finished,
## to automatically hadd the output files. This is currently only supported when
## the output file name is NOT specified in the Json skeleton, and when the multiple
## run feature is NOT used.
mySub.createCondorFiles(createHadd = True)

## Actually submit the jobs
## It is recommended to do a dry-run first without submitting to condor
#mySub.submitOnCondor()


## Example Json skeleton: the field "#DB_NAME#" will be filled by condorSubmitter.
## You can specify anything else you want that will be passed to createHistoWithtMultiDraw
## for this particular sample.
#{
#    "#DB_NAME#": {
#        "tree_name": "t",
#        "sample_cut": "1.",
#        # Optional, but if you use it, don't forget #JOB_ID#. If you have multiple runs, be sure to include a #RUN_NAME# field
#        # to be changed by your python plot config.
#        "output_name": "output_#JOB_ID#.root"
#    }
#}

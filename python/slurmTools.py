##
## Utilities to submit slurm jobs to create the histograms.
##

import os
import sys
import json
import stat
import copy
import subprocess
import math

try:
    from .samadhi_imports import CMSSW_BASE, DbStore, Sample
    sys.path.append(os.path.join(CMSSW_BASE, "cp3_llbb", "CommonTool", "histFactory"))
except ImportError, e:
    print "Problem importing necessary symbols (needs CMSSW environment, set up with `cmsenv`): {0}".format(str(e))
    sys.exit(1)

class slurmSubmitter:

    def __init__(self, sampleCfg, execPath, baseDir=".", rescale=False, runtime=None, memory=None):

        """
        Create a new slurm submitter helper

        Parameters:

          sampleCfg: list of samples to run over on the cluster. Each item is a dict containing the following keys:
            - ID: id of the sample in SAMAdhi (mutually exclusive with db_name)
            - db_name: name of the sample in SAMADhi (mutually exclusive with ID)
            - sample_fraction: int between 0 and 1. If specified, only the specified fraction of the sample will be considered when creating the jobs

          execPath: path to the executable to run, usually produced by histFactory or treeFactory
          baseDir: directory where the outputs of the jobs and the metadata will be stored. Optional, default to '.'
          rescale: if True, MC samples will be automatically rescaled to an integrated luminosity of 1 /pb using the cross-section and the sum of event weights stored in SAMADhi. Optional, default to False
          runtime: provide an estimate of the maximum runtime of the jobs. Optional, defaults to None, meaning using the maximum runtime possible. A runtime limit of zero requests that no runtime limit be imposed. Acceptable time formats include "minutes", "minutes:seconds", "hours:minutes:seconds", "days-hours", "days-hours:minutes" and "days-hours:minutes:seconds"
          memory: provide an estimate of the maximum memory needed per cpu, in MB. Optional, defaults to None, meaning using the maximum memory allowed
        """

        self.sampleCfg = sampleCfg
        self.baseDir = os.path.join(os.path.abspath(baseDir), "slurm")
        self.execPath = os.path.abspath(execPath)
        self.isCreated = False
        self.user = os.environ["USER"]
        self.runtime = runtime
        self.requestedMemory = memory

        for sample in self.sampleCfg:
            # Get list of files from DB based on sampe ID or name, and split the list according to
            # the split-level asked by the user
            if "ID" in sample.keys():
                dbSample = self.getSample(sample["ID"])
            elif "db_name" in sample.keys():
                dbSample = self.getSample(sample["db_name"])
            if dbSample.sampletype == u"SKIM" :
                files = [ (str(file.lfn), file.nevents, file.event_weight_sum, json.loads(file.extras_event_weight_sum)) for file in dbSample.files ]
            else:
                files = [ ("/storage/data/cms/" + str(file.lfn), file.nevents, file.event_weight_sum, json.loads(file.extras_event_weight_sum)) for file in dbSample.files ]
            if "sample_fraction" in sample.keys() and sample["sample_fraction"] < 1:
                # Truncate file list according to the required fraction
                # NB : the returned file list does not contain exactly nEvt_tot*fraction event
                #      it is rounded up to nEvt_tot * fraction + nEvt in next file
                nEvt_tot = dbSample.nevents
                nEvt_wanted = math.ceil(nEvt_tot * sample["sample_fraction"])
                nEvt_temp = 0
                truncated_files = []
                for file in files:
                    truncated_files.append(file)
                    nEvt_temp += file[1]
                    if nEvt_temp >= nEvt_wanted:
                        break
                files = truncated_files

            sample["db_name"] = dbSample.name

            self.splitSample(sample, files)

            rescale_sample = rescale

            is_data = False
            if dbSample.source_dataset.datatype == u"data":
                rescale_sample = False
                is_data = True

            sample["is-data"] = is_data

            if rescale_sample and dbSample.source_dataset.xsection == 1.0:
                print("Warning: cross-section for dataset %s not set." % str(dbSample.source_dataset.name))

            sample["extras-event-weight-sum"] = {}
            if rescale_sample:
                event_weights = [f[2] for f in files]
                sample["event-weight-sum"] = sum (event_weights)
                sample["cross-section"] = dbSample.source_dataset.xsection
                if dbSample.extras_event_weight_sum:
                    extras_event_weight_sum = {}
                    for f in files:
                        extras_event_weight_sum = { k: extras_event_weight_sum.get(k, 0) + f[3].get(k) for k in set(f[3]) }
                    if json.loads(dbSample.extras_event_weight_sum).viewkeys() != extras_event_weight_sum.viewkeys():
                        print("Error: all the files in %s do not have the same extras_event_weight_sum content!" % str(dbSample.source_dataset.name))
                        sys.exit()
                    sample["extras-event-weight-sum"] = extras_event_weight_sum
            else :
                sample["event-weight-sum"] = 1.
                sample["cross-section"] = 1.

            # If a path to a json skeleton was provided, use it, otherwise use the default
            if "json_skeleton" in sample.keys():
                with open(sample["json_skeleton"], "r") as js:
                    sample["json_skeleton"] = json.load(js)
                    if "#DB_NAME#" not in sample["json_skeleton"].keys():
                        raise Exception("Json entry should be named #DB_NAME#.")
                    if "path" in sample["json_skeleton"]["#DB_NAME#"].keys():
                        del sample["json_skeleton"]["#DB_NAME#"]["path"]
            else:
                sample["json_skeleton"] = {
                        sample["db_name"]:
                            {
                                "tree_name": "t",
                                "sample_cut": "1.",
                                "db_name": sample["db_name"],
                                "event-weight-sum": sample["event-weight-sum"],
                                "extras-event-weight-sum": sample["extras-event-weight-sum"],
                                "cross-section": sample["cross-section"],
                                "is-data": sample["is-data"]
                            }
                        }

        self.baseShell = """#!/bin/bash

# Slurm configuration
#SBATCH --workdir #BASE_PATH#
#SBATCH --job-name #JOB_NAME#
#SBATCH --output #LOGDIR_RELPATH#/slurm_%a.out
#SBATCH --error #LOGDIR_RELPATH#/slurm_%a.err
#ADDITIONAL_SBATCH_COMMANDS#
#SBATCH --array 0-#N_JOBS#

# Setup our CMS environment
pushd #CMS_PATH#
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scram runtime --sh`
popd

srun "#EXEC_PATH#" -d "#INDIR_PATH#/samples_${SLURM_ARRAY_TASK_ID}.json" -o output
"""

    def getSample(self, iSample):
        """ Get sample from the DB, using the sample ID or name. """
   
        sample = ""
        dbstore = DbStore()
        if isinstance(iSample, int):
            sample = dbstore.find(Sample, Sample.sample_id == iSample).one()
        elif isinstance(iSample, str):
            sample = dbstore.find(Sample, Sample.name == unicode(iSample)).one()
        else:
            raise Exception("Argument should be sample ID or DB name.")

        return sample

    def splitByFiles(self, files, N):
        """
        Split files in sub-lists containing at most N entries.
        files is expected to be an array of tuples (path, entries)

        return a list of tuples (files, start_entry, end_entry)
        """

        N = min(len(files), N)
        jobs = []

        for i in range(0, len(files), N):
            entries = 0
            files_ = []
            for f in files[i:i+N]:
                entries += f[1]
                files_.append(f[0])

            jobs.append((files_, 0, entries))

        return jobs

    def splitByEvents(self, files, N):
        """
        Split files in sub-lists containing at most N events.
        files is expected to be an array of tuples (path, entries)

        return a list of tuples (files, start_entry, end_entry)
        """

        events = 0
        for f in files:
            events += f[1]

        n_jobs = int(events / N)
        if events % N != 0:
            n_jobs += 1

        local_files = []
        for f in files:
            local_files.append((f[0], 0, f[1]))

        jobs = []
        for _ in range(0, n_jobs):

            # A job
            start = local_files[0][1]
            end = 0
            files_ = []

            remaining_events = N
            for f in local_files[:]:
                files_.append(f[0])

                remaining_events_in_file = f[2] - f[1]
                old_remaining_events = remaining_events
                remaining_events -= remaining_events_in_file
                if (remaining_events >= 0):
                    # Missing events, let's continue with the next file
                    local_files.remove(f)

                    if remaining_events == 0 or len(local_files) == 0:
                        jobs.append((files_, start, start + N - remaining_events - 1))
                        break

                else:
                    jobs.append((files_, start, start + N - 1))

                    # Compute new starting entry for next job
                    local_files[0] = (f[0], f[1] + old_remaining_events, f[2])
                    break

        return jobs

    def splitSample(self, sample, files):
        """
        Split a sample into sub-jobs according to the files-per-job or events-per-job values
        """

        if "files_per_job" in sample and "events_per_job" in sample:
            raise Exception("'files_per_job' and 'events_per_job' are mutually exclusive")

        if "files_per_job" in sample:
            jobs = self.splitByFiles(files, sample["files_per_job"])
        else:
            jobs = self.splitByEvents(files, sample["events_per_job"])

        sample["jobs"] = jobs
    
    
    def setupDirs(self):
        """ Setup the directories (input/output) in baseDir. """
    
        if not os.path.isdir(self.baseDir):
            os.makedirs(self.baseDir)
    
        inDir = os.path.join(self.baseDir, "input")
        if not os.path.isdir(inDir):
            os.makedirs(inDir)
        self.inDir = inDir
        
        outDir = os.path.join(self.baseDir, "output")
        if not os.path.isdir(outDir):
            os.makedirs(outDir)
        self.outDir = outDir

        logDir = os.path.join(self.baseDir, "logs")
        if not os.path.isdir(logDir):
            os.makedirs(logDir)
        self.logDir = logDir

    def createFiles(self):
        """ Create the jobs files."""

        jobCount = 0

        dico = {}
        dico["#BASE_PATH#"] = self.baseDir
        dico["#INDIR_PATH#"] = self.inDir
        dico["#OUTDIR_PATH#"] = self.outDir
        dico["#LOGDIR_RELPATH#"] = os.path.basename(self.logDir)
        dico["#EXEC_PATH#"] = self.execPath
        dico["#CMS_PATH#"] = CMSSW_BASE
        dico["#JOB_NAME#"] = "cp3-llbb"

        for sample in self.sampleCfg:
            name = sample["db_name"]
            jobList = sample["jobs"]

            for job in jobList:

                jsonFileName = os.path.join(self.inDir, "samples_{}.json".format(jobCount) )
                jsonContent = copy.deepcopy(sample["json_skeleton"])
                
                if "#DB_NAME#" in jsonContent.keys():
                    jsonContent = {}
                    jsonContent[name] = copy.deepcopy(sample["json_skeleton"]["#DB_NAME#"])
                    jsonContent[name]["db_name"] = name
                
                jsonContent[name]["files"] = job[0]
                jsonContent[name]["event-start"] = job[1]
                jsonContent[name]["event-end"] = job[2]
                
	        jsonContent[name]["output_name"] = name + "_histos_{}".format(jobCount)

                with open(jsonFileName, "w") as js:
                    json.dump(jsonContent, js)

                jobCount += 1
           
        dico["#N_JOBS#"] = str(jobCount - 1)

        # Extra sbatch commands
        extra_commands = ""
        if self.requestedMemory:
            extra_commands += "#SBATCH --mem-per-cpu {:.0f}\n".format(self.requestedMemory)
        if self.runtime:
            extra_commands += "#SBATCH --time {}\n".format(self.runtime)

        dico["#ADDITIONAL_SBATCH_COMMANDS#"] = extra_commands

        slurmFile = str(self.baseShell)

        for key in dico.items():
            slurmFile = slurmFile.replace(key[0], key[1])

        # Shell wrapper
        shFileName = os.path.join(self.inDir, "slurm.sh")
        with open(shFileName, "w") as sh:
            sh.write(slurmFile)
        perm = os.stat(shFileName)
        os.chmod(shFileName, perm.st_mode | stat.S_IEXEC)

        print "Created {} job command files. Caution: the jobs are not submitted yet!.".format(jobCount)

        self.jobCount = jobCount
        self.isCreated = True

        # Generate a command to hadd all the files when the jobs are done
        haddFile = os.path.join(self.baseDir, "hadd_histos.sh")
        with open(haddFile, "w") as f:
            cmd = """#!/usr/bin/env bash

function check_success {
  should_exit=false
  find #LOGDIR_PATH# -name "*.err" -not -size 0 |
  {
    while read f; do
      [[ $f =~ slurm_([0-9]+) ]]
      id=${BASH_REMATCH[1]}
      echo "Error: job #${id} failed."
      should_exit=true
    done

    if [ "${should_exit}" == true ]; then
      exit 1
    fi
  }

  if [ $? -eq 1 ]; then
    exit 1
  fi
}

function do_hadd {
 if [ ! -z "$1" ]; then
  to_add=( $(ls $1_*.root) )
  # If there is only one file to hadd, do not do it but simply rename the file (faster)
  if [[ ${#to_add[*]} == 1 ]]; then
    mv ${to_add[0]} $1.root
  else
    hadd $1.root $1_*.root && if [ "$2" == "-r" ]; then rm $1_*.root; fi
  fi
 fi
}

check_success

pushd #OUTDIR_PATH#

base_list=`find -regex ".*_[0-9]*.root" -printf "%f\\n" | sed "s/_[0-9]*.root//g" | sort | uniq`

for base in $base_list; do
 do_hadd $base $1
done
popd"""
            f.write(cmd.replace("#OUTDIR_PATH#", self.outDir)
                       .replace("#LOGDIR_PATH#", self.logDir))
        perm = os.stat(haddFile)
        os.chmod(haddFile, perm.st_mode | stat.S_IEXEC)
        self.haddCmd = haddFile


    def submit(self):

        if not self.isCreated:
            raise Exception("Job files must be created first using createFiles().")

        print "Submitting {} jobs.".format(self.jobCount)
        result = subprocess.check_output(["sbatch", os.path.join(self.inDir, "slurm.sh")])
        print result

        # # Get cluster id from condor_submit output
        # import re
        # r = re.compile("\d+ job\(s\) submitted to cluster (\d+)\.")
        # g = r.search(result)

        # clusterId = int(g.group(1))

        # with open(os.path.join(self.inDir, 'cluster_id'), 'w') as f:
            # f.write(str(clusterId))

        # print "Submitting {} jobs done. Job id is {}.".format(self.jobCount, clusterId)
        # print "Monitor your jobs with `condor_status -submitter` or `condor_q {}`".format(clusterId)
        # print "When they are all done, run the following command to hadd the files: `{}`".format(self.haddCmd)
        # print "If you also want to remove the original files, add the `-r` argument."



if __name__ == "__main__":
    raise Exception("Not destined to be run stand-alone.")

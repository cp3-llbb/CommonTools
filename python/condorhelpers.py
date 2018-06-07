"""
HTCondor tools (based on cp3-llbb/CommonTools condorSubmitter)
"""
__author__ = "Pieter David <pieter.david@uclouvain.be"
__date__ = "February 2017"

import logging
logger = logging.getLogger(__name__)

from itertools import izip, count
import os
import os.path
import subprocess

from .batchhelpers import CommandListJob

CondorJobStatus = [
          "Unexpanded"      # 0
        , "Idle"            # 1
        , "Running"         # 2
        , "Removed"         # 3
        , "Completed"       # 4
        , "Held"            # 5
        , "Submission_err"  # 6
        ]

class CommandListCondorJob(CommandListJob):
    """
    Helper class to create a condor master job from a list of commands (each becoming one subjob)

    Default work directory will be $(pwd)/condor_work, default output pattern is "*.root"
    """
    def __init__(self, commandList, workDir=None, envSetupLines=None, outputPatterns=None):
        self.envSetupLines = envSetupLines if envSetupLines is not None else []
        self.outputPatterns = outputPatterns if outputPatterns is not None else ["*.root"]

        super(CommandListCondorJob, self).__init__(commandList, workDir=workDir, workdir_default_pattern="condor_work")

        self.masterCmd = self._writeCondorFiles()
        self.clusterId = None ## will be set by submit
 
    MasterCmd = (
        "should_transfer_files   = YES\n"
        "when_to_transfer_output = ON_EXIT\n"
        "universe       = vanilla\n"
        "requirements   = (CMSFARM =?= TRUE)&&(Memory > 200)\n"
        "executable     = {indir}/condor.sh\n"
        "arguments      = $(Process)\n"
        "output         = {logdir_rel}/condor_$(Process).out\n"
        "error          = {logdir_rel}/condor_$(Process).err\n"
        "log            = {logdir_rel}/condor_$(Process).log\n"
        "queue {nJobs:d}\n"
        )
    MasterShell = (
        "#!/usr/bin/env bash\n"
        "\n"
        "{indir}/condor_$1.sh\n"
        )

    JobShell = (
        "#!/usr/bin/env bash\n"
        "\n"
        "{environment_setup}"
        # "# Setup our CMS environment\n"
        # "pushd {CMS_PATH}\n"
        # "source /cvmfs/cms.cern.ch/cmsset_default.sh\n"
        # "eval `scram runtime --sh`\n"
        # "popd\n"
        "\n"
        "function move_files {{\n"
        "{move_fragment}"
        "\n}}\n"
        "\n"
        "{command} && move_files"
        )

    def _writeCondorFiles(self):
        """ Create Condor .sh and .cmd files """
        masterCmdName = os.path.join(self.workDirs["in"], "condor.cmd")
        with open(masterCmdName, "w") as masterCmd:
            masterCmd.write(CommandListCondorJob.MasterCmd.format(
                  indir=self.workDirs["in"]
                , logdir_rel=os.path.relpath(self.workDirs["log"])
                , nJobs=len(self.commandList)
                ))
        masterShName = os.path.join(self.workDirs["in"], "condor.sh")
        with open(masterShName, "w") as masterSh:
            masterSh.write(CommandListCondorJob.MasterShell.format(
                  indir=self.workDirs["in"]
                ))
        makeExecutable(masterShName)

        for i,command in izip(count(), self.commandList):
            jobShName = os.path.join(self.workDirs["in"], "condor_{:d}.sh".format(i))
            job_outdir = os.path.join(self.workDirs["out"], str(i))
            os.makedirs(job_outdir)
            with open(jobShName, "w") as jobSh:
                jobSh.write(CommandListCondorJob.JobShell.format(
                      environment_setup="\n".join(self.envSetupLines)
                    , move_fragment="\n".join((
                        " for file in {pattern}; do\n"
                        '   echo "Moving $file to {outdir}/"\n'
                        "   mv $file {outdir}/\n"
                        " done"
                        ).format(pattern=ipatt, outdir=job_outdir)
                        for ipatt in self.outputPatterns)
                    , command=command
                    ))
            makeExecutable(jobShName)

        return masterCmdName

    def _commandOutDir(self, command):
        """ Output directory for a given command """
        return os.path.join(self.workDirs["out"], str(self.commandList.index(command)))
    def commandOutFiles(self, command):
        """ Output files for a given command """
        import fnmatch
        cmdOutDir = self._commandOutDir(command)
        return list( os.path.join(cmdOutDir, fn) for fn in os.listdir(cmdOutDir)
                if any( fnmatch.fnmatch(fn, pat) for pat in self.outputPatterns) )

    def submit(self):
        """ Submit the jobs to condor """
        logger.info("Submitting {0:d} condor jobs.".format(len(self.commandList)))
        result = subprocess.check_output(["condor_submit", self.masterCmd])

        import re
        pat = re.compile("\d+ job\(s\) submitted to cluster (\d+)\.")
        g = pat.search(result)
        self.clusterId = g.group(1)

        ## save to file in case
        with open(os.path.join(self.workDirs["in"], "cluster_id"), "w") as f:
            f.write(self.clusterId)

        logger.info("Submitted, job ID is {}".format(self.clusterId))

    def statuses(self):
        """ list of subjob statuses (numeric, using indices in CondorJobStatus) """
        if self.clusterId is None:
            raise Exception("Cannot get status before submitting the jobs to condor")
        return map(int, list(subprocess.check_output(["condor_q"      , self.clusterId, "-format", '%d ', "JobStatus"]).strip().split())
                      + list(subprocess.check_output(["condor_history", self.clusterId, "-format", '%d ', "JobStatus"]).strip().split()) )

    @property
    def status(self):
        statuses = self.statuses()
        if all(st == statuses[0] for st in statuses):
            return CondorJobStatus[statuses[0]]
        elif any(st == 2 for st in statuses):
            return "Running"
        elif any(st == 3 for st in statuses):
            return "Removed"
        else:
            return "unknown"

    def subjobStatus(self, i):
        subjobId = "{0}.{1:d}".format(self.clusterId, i)
        ret = subprocess.check_output(["condor_q", subjobId, "-format", '%d', "JobStatus"])
        if len(ret) == 0: # search in the completed ones
            ret = subprocess.check_output(["condor_history", subjobId, "-format", '%d', "JobStatus"])
        return CondorJobStatus[int(ret)]
    def commandStatus(self, command):
        return self.subjobStatus(self.commandList.index(command))

def makeCondorTasksMonitor(jobs=[], tasks=[], interval=120):
    """ make a TasksMonitor for condor jobs """
    from .batchhelpers import TasksMonitor
    return TasksMonitor(jobs=jobs, tasks=tasks, interval=interval
            , allStasuses=CondorJobStatus
            , activeStatuses=(1,2)
            , completedStatus=4
            )

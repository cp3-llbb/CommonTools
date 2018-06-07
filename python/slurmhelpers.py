"""
Slurm tools (based on previous condorhelpers and cp3-llbb/CommonTools condorSubmitter and slurmSubmitter)
"""
__author__ = "Pieter David <pieter.david@uclouvain.be>"
__date__ = "April 2017"

import logging
logger = logging.getLogger(__name__)

import os.path
import subprocess

from .batchhelpers import CommandListJob

SlurmJobStatus = ["PENDING", "RUNNING", "COMPLETED", "FAILED", "COMPLETING", "CONFIGURING", "CANCELLED", "BOOT_FAIL", "NODE_FAIL", "PREEMPTED", "RESIZING", "SUSPENDED", "TIMEOUT", "unknown"]

from contextlib import contextmanager

# take from contextlib when moving to python3
@contextmanager
def redirect_stdout(whereto=None):
    import sys
    bk_out = sys.stdout
    sys.stdout = whereto
    yield
    sys.stdout = bk_out

class CommandListSlurmJob(CommandListJob):
    """
    Helper class to create a slurm job array from a list of commands (each becoming a task in the array)

    Default work directory will be $(pwd)/slurm_work, default output pattern is "*.root"
    """
    default_cfg_opts = {
          "environmentType" : "cms"
        , "sbatch_time"     : "0-04:00"
        , "sbatch_mem"      : "2048"
        , "stageoutFiles"   : ["*.root"]
        }

    def __init__(self, commandList, workDir=None, configOpts=None):
        super(CommandListSlurmJob, self).__init__(commandList, workDir=workDir, workdir_default_pattern="slurm_work")
        ##
        from CP3SlurmUtils.Configuration import Configuration
        self.cfg = Configuration()
        ## apply user-specified
        cfg_opts = dict(CommandListSlurmJob.default_cfg_opts)
        if configOpts:
            cfg_opts.update(configOpts)
        for k, v in cfg_opts.iteritems():
            setattr(self.cfg, k, v)

        ## check working and output directory
        self.cfg.sbatch_workdir = self.workDir
        self.cfg.inputSandboxDir = self.workDirs["in"]
        self.cfg.batchScriptsDir = self.workDir
        self.cfg.batchScriptsFilename = "slurmSubmission.sh"
        self.cfg.stageoutDir = os.path.join(self.workDirs["out"], "${SLURM_ARRAY_TASK_ID}")
        self.cfg.stageoutLogsDir = self.workDirs["log"]
        self.cfg.useJobArray = True
        self.cfg.inputParamsNames = ["taskcmd"]
        self.cfg.inputParams = list([cmd] for cmd in self.commandList)
        self.cfg.payload = ("${taskcmd}")

        self.slurmScript = os.path.join(self.cfg.batchScriptsDir, self.cfg.batchScriptsFilename)
        self.clusterId = None ## will be set by submit
        self._finishedTasks = dict()
        self._statuses = ["PENDING" for cmd in self.commandList]

        ## output
        try:
            from CP3SlurmUtils.SubmitWorker import SubmitWorker as slurmSubmitWorker
        except ImportError as ex:
            logger.info("Could not import slurmSubmitWorker from CP3SlurmUtils.SubmitUtils. Please run 'module load slurm/slurm_utils'")
        try:
            slurm_submit = slurmSubmitWorker(self.cfg, submit=False, debug=False, quiet=False)
        except Exception as ex:
            logger.error("Problem constructing slurm submit worker from CP3SlurmUtils: {}".format(str(ex)))
            raise ex
        else:
            from StringIO import StringIO ## python3: from io import StringIO
            workerout = StringIO()
            submitLoggerFun = logger.debug
            try:
                with redirect_stdout(workerout):
                    slurm_submit()
            except Exception as ex:
                submitLoggerFun = logger.info
                raise RuntimeError("Problem in slurm_submit: {}".format(str()))
            finally:
                submitLoggerFun("==========     BEGIN slurm_submit output     ==========")
                for ln in workerout.getvalue().split("\n"):
                    submitLoggerFun(ln)
                submitLoggerFun("==========     END   slurm_submit output     ==========")

    def _commandOutDir(self, command):
        """ Output directory for a given command """
        return os.path.join(self.workDirs["out"], str(self.commandList.index(command)+1))

    def commandOutFiles(self, command):
        """ Output files for a given command """
        import fnmatch
        cmdOutDir = self._commandOutDir(command)
        return list( os.path.join(cmdOutDir, fn) for fn in os.listdir(cmdOutDir)
                if any( fnmatch.fnmatch(fn, pat) for pat in self.cfg.stageoutFiles) )

    def submit(self):
        """ Submit the job to slurm """
        logger.info("Submitting an array of {0:d} jobs to slurm".format(len(self.commandList)))
        result = subprocess.check_output(["sbatch"
            , "--partition={}".format(self.cfg.sbatch_partition)
            , "--qos={}".format(self.cfg.sbatch_qos)
            , "--wckey=cms"
            , self.slurmScript])

        self.clusterId = next(tok for tok in reversed(result.split()) if tok.isdigit())

        ## save to file in case
        with open(os.path.join(self.workDirs["in"], "cluster_id"), "w") as f:
            f.write(self.clusterId)

        logger.info("Submitted, job ID is {}".format(self.clusterId))

    def statuses(self, update=True):
        """ list of subjob statuses (numeric, using indices in SlurmJobStatus) """
        if update:
            self.updateStatuses()
        return [ SlurmJobStatus.index(sjst) for sjst in self._statuses ]

    @property
    def status(self):
        if all(st == self._statuses[0] for st in self._statuses):
            return self._statuses[0]
        elif any(st == "RUNNING" for st in self._statuses):
            return "RUNNING"
        elif any(st == "CANCELLED" for st in self._statuses):
            return "CANCELLED"
        else:
            return "unknown"

    def subjobStatus(self, i):
        return self._statuses[i-1]

    def updateStatuses(self):
        for i in xrange(len(self.commandList)):
            subjobId = "{0}_{1:d}".format(self.clusterId, i+1)
            status = "unknown"
            if subjobId in self._finishedTasks:
                status = self._finishedTasks[subjobId]
            else:
                sacctCmdArgs = ["sacct", "-n", "--format", "State", "-j", subjobId]
                ret = subprocess.check_output(sacctCmdArgs).strip()
                if "\n" in ret: ## if finished
                    if len(ret.split("\n")) == 2:
                        ret = subprocess.check_output(["sacct", "-n", "--format", "State", "-j", "{}.batch".format(subjobId)]).strip()
                        self._finishedTasks[subjobId] = ret
                        status = ret
                    else:
                        raise AssertionError("More than two lines in sacct... there's something wrong")
                else:
                    if len(ret) != 0:
                        status = ret
                    else:
                        squeueCmdArgs = ["squeue", "-h", "-O", "state", "-j", subjobId]
                        ret = subprocess.check_output(squeueCmdArgs).strip()
                        if len(ret) != 0:
                            status = ret
                        else: # fall back to previous status (probably PENDING or RUNNING)
                            status = self._statuses[i]
            self._statuses[i] = status

    def commandStatus(self, command):
        return self.subjobStatus(self.commandList.index(command)+1)

def makeSlurmTasksMonitor(jobs=[], tasks=[], interval=120):
    """ make a TasksMonitor for slurm jobs """
    from .batchhelpers import TasksMonitor
    return TasksMonitor(jobs=jobs, tasks=tasks, interval=interval
            , allStatuses=SlurmJobStatus
            , activeStatuses=[SlurmJobStatus.index(stNm) for stNm in ("CONFIGURING", "COMPLETING", "PENDING", "RUNNING", "RESIZING", "SUSPENDED")]
            , completedStatus=SlurmJobStatus.index("COMPLETED")
            )

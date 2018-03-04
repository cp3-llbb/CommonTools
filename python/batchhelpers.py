"""
Batch cluster tools (common part for HTCondor and slurm)
"""
__author__ = "Pieter David <pieter.david@uclouvain.be>"
__date__ = "February-April 2017"

import logging
logger = logging.getLogger(__name__)

import os
import os.path

def makeExecutable(path):
    """ Set file permissions to executable """
    import stat
    if os.path.exists(path) and os.path.isfile(path):
        perm = os.stat(path)
        os.chmod(path, perm.st_mode | stat.S_IEXEC)

class CommandListJob(object):
    """ Interface/base for 'backend' classes to create a job cluster/array from a list of commands (eah becoming a subjob) """
    def __init__(self, commandList, workDir=None, workdir_default_pattern="batch_work"):
        self.commandList = commandList
        self.workDir = self.init_dirtowrite(workDir, default_pattern=workdir_default_pattern)
        self.workDirs = self.setupBatchDirs(self.workDir)

    ## interface methods
    def submit(self):
        """ Submit the job(s) """
        pass
    def commandOutFiles(self, command):
        """ Output files for a given command (when finished) """
        pass
    ## for monitoring
    @property
    def status(self):
        """ overall job status summary """
        pass
    def statuses(self):
        """ list of subjob statuses (numeric, using indices in CondorJobStatus) """
        pass
    def updateStatuses(self):
        """ Update the subjob status cache (if used in the implementation) """
        pass
    def subjobStatus(self, i):
        """ get status of subjob """
        pass
    def commandStatus(self, command):
        """ get the status of the jobs corresponding to one of the commands """
        pass

    ## helper methods
    @staticmethod
    def init_dirtowrite(given=None, default_pattern="batch"):
        """ Initialisation helper: check that the directory does not exist, then create it

        If None is given, a default ("$(pwd)/{default_pattern}", "$(pwd)/default_pattern_0" etc.) is used
        """
        if given is None:
            test_dir = os.path.join(os.getcwd(), default_pattern)
            if os.path.exists(test_dir):
                i = 0
                while os.path.exists(test_dir) and i < 10:
                    test_dir = os.path.join(os.getcwd(), "{0}_{1:d}".format(default_pattern, i))
                    i += 1
        else:
            test_dir = given
        if os.path.exists(test_dir):
            raise Exception("Directory {0} exists".format(test_dir))

        os.makedirs(test_dir)

        return os.path.abspath(test_dir) ## make sure we keep absolute paths

    @staticmethod
    def setupBatchDirs(workDir):
        """ Create up the working directories (input, output, logs) under workDir """
        dirs = {
              "in"  : os.path.join(workDir, "input")
            , "out" : os.path.join(workDir, "output")
            , "log" : os.path.join(workDir, "logs")
            }
        for subdir in dirs.itervalues():
            os.mkdir(subdir)
        logger.info("Created working directories under {0}".format(workDir))
        return dirs

class SplitAggregationTask(object):
    """ Task split in commands, whose results can be merged """
    def __init__(self, commandList, finalizeAction=None):
        self._jobCluster = None
        self.commandList = commandList
        self.finalizeAction = finalizeAction
    @property
    def jobCluster(self):
        return self._jobCluster
    @jobCluster.setter
    def jobCluster(self, jobCluster):
        if self._jobCluster:
            raise Exception("SplitAggregationTask.jobCluster has already been set")
        self._jobCluster = jobCluster
        if self.finalizeAction: ## pass it on
            self.finalizeAction.jobCluster = jobCluster

    def tryFinalize(self):
        if self.jobCluster and all(self.jobCluster.commandStatus(cmd).upper() == "COMPLETED" for cmd in self.commandList):
            if self.finalizeAction:
                self.finalizeAction.perform()
            return True
        return False

class Action(object):
    """ interface for job finalization """
    def perform(self):
        """ interface method """
        return False

import subprocess

class HaddAction(Action):
    """ merge results with hadd
    """
    def __init__(self, commandList, outDir, options=None):
        self.jobCluster = None
        self.commandList = commandList
        self.outDir = outDir
        self.options = options if options is not None else []
        super(HaddAction, self).__init__()
    def perform(self):
        if len(self.commandList) == 0:   ## nothing
            return
        elif len(self.commandList) == 1: ## move
            cmd = self.commandList[0]
            for outf in self.jobCluster.commandOutFiles(cmd):
                logger.info("finalization: moving output file {0} to {1}".format(outf, self.outDir))
                subprocess.check_call(["mv", outf, self.outDir])
        else:                            ## merge
            ## collect for each output file name which jobs produced one
            filesToMerge = dict()
            for cmd in self.commandList:
                for outf in self.jobCluster.commandOutFiles(cmd):
                    outfb = os.path.basename(outf)
                    if outfb not in filesToMerge:
                        filesToMerge[outfb] = []
                    filesToMerge[outfb].append(outf)

            for outfb, outfin in filesToMerge.iteritems():
                fullout = os.path.join(self.outDir, outfb)
                logger.info("finalization: merging {0} to {1}".format(", ".join(outfin), fullout))
                subprocess.check_call(["hadd"]+self.options+[fullout]+outfin)

from itertools import izip, chain

class TasksMonitor(object):
    """ Monitor a number of tasks and the associated job clusters """
    def __init__(self, jobs=[], tasks=[], interval=120, allStatuses=None, activeStatuses=None, completedStatus=None):
        """ Constructor

        jobs: job clusters to monitor
        tasks: tasks to monitor (and finalize)
        interval: number of seconds between status checks
        """
        self.jobs = set()
        self.tasks = set()
        self.activetasks = set()
        self.add(jobs, tasks)
        self.interval = interval
        self.allStatuses = list(allStatuses) if allStatuses else []
        self.activeStatuses = list(activeStatuses) if activeStatuses else []
        self.completedStatus = completedStatus
    def add(self, jobs, tasks):
        """ add jobs and tasks """
        self.jobs.update(jobs)
        self.tasks.update(tasks)
        assert sum(len(j.commandList) for j in self.jobs) == sum(len(t.commandList) for t in self.tasks) ## assumption: same set of commands
        self.activetasks.update(tasks)
    @staticmethod
    def makeStats(statuses, allStatuses):
        histo = [ 0 for st in allStatuses ]
        for jSt in statuses:
            histo[jSt] += 1
        return histo
    @staticmethod
    def formatStats(stats, allStatuses):
        return "{0} / {1:d} Total".format(", ".join("{0:d} {1}".format(n,nm) for n,nm in izip(stats, allStatuses)), sum(stats))

    def _tryFinalize(self):
        """ try to finalize tasks """
        finalized = []
        for t in self.activetasks:
            if t.tryFinalize():
                finalized.append(t) ## don't change while iterating
        for ft in finalized:
            self.activetasks.remove(ft)
        if len(finalized) > 0:
            logger.info("Finalized {0:d} tasks, {1:d} remaining".format(len(finalized), len(self.activetasks)))

    def collect(self, wait=None):
        """ wait for the jobs to finish, then finalize tasks """
        for j in self.jobs:
            j.updateStatuses()
        self._tryFinalize()
        if len(self.activetasks) > 0:
            logger.info("Waiting for jobs to finish...")
            from datetime import datetime
            import time
            nJobs = sum( len(j.commandList) for j in self.jobs )
            if wait:
                time.sleep(wait)
            for j in self.jobs:
                j.updateStatuses()
            stats = self.makeStats(chain.from_iterable(j.statuses() for j in self.jobs), self.allStatuses)
            while len(self.activetasks) > 0 and sum(stats[sa] for sa in self.activeStatuses) > 0:
                time.sleep(self.interval)
                prevStats = stats
                for j in self.jobs:
                    j.updateStatuses()
                stats = self.makeStats(chain.from_iterable(j.statuses() for j in self.jobs), self.allStatuses)
                logger.info("[ {0} :: {1} ]".format(datetime.now().strftime("%H:%M:%S"), self.formatStats(stats, self.allStatuses)))
                if stats[self.completedStatus] > prevStats[self.completedStatus]:
                    self._tryFinalize()

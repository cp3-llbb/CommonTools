#! /usr/bin/env python

import os
import argparse
import re
import shutil

def grep(filename, *args):
    """
    Return True if any args is found somewhere in filename content
    """

    with open(filename) as f:
        for line in f.readlines():
            line = line.lower()
            for pattern in args:
                if pattern.lower() in line:
                    return True

    return False

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--directory', nargs='+', help='Condor output directory')
parser.add_argument('-f', '--finished', action='store_true', help='Check if every job has an output ROOT file. Only call this when the task is finished!')
parser.add_argument('-s', '--submit', action='store_true', help='Resubmit all failed jobs')
parser.add_argument('-c', '--clean', action='store_true', help='If everything ran fine, clean everything beside output files')

args = parser.parse_args()

for condorDir in args.directory:
    print ""

    if not os.path.isdir(condorDir):
        print("Directory {} does not exist!".format(condorDir))
        continue

    print "Checking ...{}".format(condorDir)

    if os.path.normpath(condorDir).split("/")[-1] != "condor":
        condorDir = os.path.join(condorDir, "condor")

    logDir = os.path.join(condorDir, "logs")
    failedJobIDs = []

    for file in os.listdir(logDir):
        if ".err" in file and os.stat(os.path.join(logDir, file)).st_size != 0:
            failedJobID = file.split(".err")[0].split("_")[1]
            failedJobIDs.append(failedJobID)

        if ".out" in file and grep(os.path.join(logDir, file), "warning", "error", "fail"):
            failedJobID = file.split(".out")[0].split("_")[1]
            failedJobIDs.append(failedJobID)
    
    if len(failedJobIDs):
        print("{} jobs have failed: {}".format(len(failedJobIDs), failedJobIDs))
        print("If you want to submit the jobs type: checkJobsAndResubmit.py -d 'yourCondorDir' -s")
    
    toResubmit = failedJobIDs

    if args.finished:
        noResultIDs = []
        inDir = os.path.join(condorDir, "input")
        outDir = os.path.join(condorDir, "output")
        get_number = lambda p: os.path.splitext(os.path.basename(p))[0].split('_')[-1]
        inFiles = [ get_number(f) for f in os.listdir(inDir) if re.match(R"condor_[0-9]+.sh", f) is not None ]
        outFiles = [ get_number(f) for f in os.listdir(outDir) if re.match(R".*_histos_[0-9]+.root", f) is not None ]
        for i in inFiles:
            if i not in outFiles:
                noResultIDs.append(i)
        
        if len(noResultIDs):
            print("{} jobs have no output file: {}".format(len(noResultIDs), noResultIDs))
            print("If you want to submit the jobs type: checkJobsAndResubmit.py -d 'yourCondorDir' -s -f")
            toResubmit = list(set(toResubmit + noResultIDs))

    if not len(toResubmit):
        print("All jobs succeeded ;-)")

        if args.clean:
            shutil.rmtree(os.path.join(condorDir, "input"), ignore_errors=True)
            shutil.rmtree(os.path.join(condorDir, "..", "build"), ignore_errors=True)
            shutil.rmtree(os.path.join(condorDir, "..", "cmake"), ignore_errors=True)
            shutil.rmtree(os.path.join(condorDir, "..", "common"), ignore_errors=True)

        continue

    if args.submit:
        with open(os.path.join(condorDir, "input", "condor.cmd"), "r") as cmdFile:
            cmdFileText = cmdFile.read()
            linesToPaste = cmdFileText[cmdFileText.find("arguments"):]

        resubmitFileName = os.path.join(condorDir, "input", "resubmit.cmd")

        with open(resubmitFileName, "w") as cmdFile:
            cmdFile.write(cmdFileText.replace(linesToPaste, ""))

            linesToPaste = "\n".join([ line for line in linesToPaste.split('\n') if "queue" not in line ])
         
            for id in toResubmit:
                newLines = linesToPaste.replace("$(Process)", id)
                cmdFile.write(newLines)
                cmdFile.write("\nqueue 1\n")
     
        os.system("condor_submit " + resubmitFileName)


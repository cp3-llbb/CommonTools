#! /usr/bin/env python

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--directory', help='Condor output directory', required=True)
parser.add_argument('-s', '--submit', action='store_true', required=False)

args = parser.parse_args()

condorDir = args.directory
logDir = os.path.join(condorDir, "logs")
failedJobIDs = []

for file in os.listdir(logDir):
    if ".err" in file and os.stat(os.path.join(logDir, file)).st_size != 0:
        failedJobID = file.split(".err")[0].split("_")[1]
        failedJobIDs.append(failedJobID)

if not len(failedJobIDs):
    print("All jobs succeeded ;-)")
    quit()

print("Jobs " + str(failedJobIDs) + " have failed.")

with open(os.path.join(condorDir, "input", "condor.cmd"), "r") as cmdFile:
    cmdFileText = cmdFile.read()
    linesToPaste = cmdFileText[cmdFileText.find("arguments"):]

resubmitFileName = os.path.join(condorDir, "input", "resubmit.cmd")

with open(resubmitFileName, "w") as cmdFile:
    cmdFile.write(cmdFileText.replace(linesToPaste, ""))

    linesToPaste = "\n".join([ line for line in linesToPaste.split('\n') if "queue" not in line ])
 
    for id in failedJobIDs:
        newLines = linesToPaste.replace("$(Process)", id)
        cmdFile.write(newLines)
        cmdFile.write("\nqueue {}\n".format(id))
 
if args.submit:
    os.system("condor_submit " + resubmitFileName)
else: 
    print("If you want to submit the jobs type: python resubmit.py 'yourCondorDir' --submit")


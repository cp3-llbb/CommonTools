#!/usr/bin/env python

import os, sys

# Usage: resubmit.py 'yourCondorDir' [submit]

condorDir = sys.argv[1]
logDir = condorDir+"/logs/"
failedJobIDs = []

for file in os.listdir(logDir) : 
    if ".err" in file and os.stat(logDir+file).st_size != 0 :
        failedJobID =  file.split(".err")[0].split("_")[1]
        failedJobIDs.append(failedJobID)

if failedJobIDs == [] :
    print "All jobs succeeded ;-)"
    sys.exit()

print "Jobs ", failedJobIDs, " have failed."
resubmitFileName = "%s/input/resubmit.cmd"%condorDir
os.system("cp %s/input/condor.cmd %s"%(condorDir, resubmitFileName))
cmdFile = open(resubmitFileName, "r")
cmdFileText = cmdFile.read()
lineToPaste = cmdFileText[cmdFileText.find("arguments"):]

cmdFile = open(resubmitFileName, "w")
cmdFile.write(cmdFileText.replace(lineToPaste,""))

for line in lineToPaste.split("\n") :
    if ("queue" in line):
        lineToPaste = lineToPaste.replace(line,"queue 1\n")

for id in failedJobIDs : 
    templineToPaste = lineToPaste.replace("$(Process)", id)
    cmdFile.write(templineToPaste)
cmdFile.close()

if len(sys.argv) > 2 :
    if sys.argv[2] == "submit":
        os.system("condor_submit %s"%(resubmitFileName))
else : 
    print "If you want to submit the jobs type : python resubmit.py 'yourCondorDir' submit"

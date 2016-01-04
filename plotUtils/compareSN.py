#First test
from ROOT import *
import os
script = "compareSN"
sampleDir ="/home/fynu/obondu/Higgs/CommonTools/plotUtils"
signalFiles = [f for f in os.listdir(sampleDir) if f.find("GluGluToRadionToHHT")==0]

os.system("rm *.d *.so")
print "**** COMPILING ****"
os.system("root -b -l -q %s.C+"%script)

for sourceFile in signalFiles:
    outFile=sourceFile.split("_")[1]+".png"
    print "Processing %s"%outFile
    sourceFile=sampleDir+"/"+sourceFile
    os.system("echo 'gROOT->LoadMacro(\"%s_C.so\"); %s(\"%s\",\"%s\"); gSystem->Exit(0);' | root -b -l >> log.txt 2>&1"%(script,script,sourceFile,outFile))
    os.system("echo 'gROOT->LoadMacro(\"%s_C.so\"); %s(\"%s\",\"%s\",200); gSystem->Exit(0);' | root -b -l >> log.txt 2>&1"%(script,script,sourceFile,outFile.replace(".png","_small.png")))







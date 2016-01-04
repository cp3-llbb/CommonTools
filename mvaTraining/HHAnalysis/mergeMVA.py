import os
from trainMVA import *

filesForMerging  = [file for file in os.listdir(inFileDir) if "_histos.root" in file]
xmlFileDir = "/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/CommonTools/mvaTraining/HHAnalysis/weights/"
MVAname = label
xmlFile = xmlFileDir+label+"_kBDT.weights.xml"
outFileDir = inFileDir + "/withMVAout/"
if not os.path.isdir(outFileDir):
    os.system("mkdir "+outFileDir)
print outFileDir

for file in filesForMerging :
    MVA_out_in_tree(inFileDir, file, discriList, xmlFile, MVAname, outFileDir)

import os, sys, commands
from generateTrees import cut
#usage :python HHAnalysis/skimInDB.py rootFileDir(relativePath) [SkimDescription]

# Add default ingrid storm package
sys.path.append('/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/lib/python2.7/site-packages/storm-0.20-py2.7-linux-x86_64.egg')
sys.path.append('/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/lib/python2.7/site-packages/MySQL_python-1.2.3-py2.7-linux-x86_64.egg')

CMSSW_BASE = os.environ['CMSSW_BASE']
SCRAM_ARCH = os.environ['SCRAM_ARCH']
sys.path.append(os.path.join(CMSSW_BASE,'bin', SCRAM_ARCH))

from SAMADhi import Sample, DbStore
import add_sample

def get_sample(name):
    dbstore = DbStore()
    resultset = dbstore.find(Sample, Sample.name == name)
    return resultset.one()

fileDir = sys.argv[1]
skimDescription = "_skimmed"
if len(sys.argv)>2 : 
    skimDescription += "_" + sys.argv[2]

commment = sys.argv[2]
currentDir = os.getcwd()+"/"
fileList = [file for file in os.listdir(fileDir) if "histos.root" in file and not "QCD" in file]
for file in fileList :
    fatherSample = get_sample(unicode(file.replace("_histos.root","")))
    fatherID = fatherSample.sample_id
    name = fatherSample.name+skimDescription
    sys.argv = ["add_sample.py", "SKIM", currentDir+fileDir, "--source_sample=%s"%fatherID, "--comment='%s'"%cut, "--name=%s"%name, "--weight-sum=%s"%fatherSample.event_weight_sum, "--source_dataset=%s"%fatherSample.source_dataset_id, "--files=%s"%currentDir+fileDir+file]
    add_sample.main()


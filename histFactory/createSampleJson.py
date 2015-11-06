#!/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/bin/python

import os, sys
import json

# Add default ingrid storm package
sys.path.append('/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/lib/python2.7/site-packages/storm-0.20-py2.7-linux-x86_64.egg')
sys.path.append('/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/lib/python2.7/site-packages/MySQL_python-1.2.3-py2.7-linux-x86_64.egg')

CMSSW_BASE = os.environ['CMSSW_BASE']
SCRAM_ARCH = os.environ['SCRAM_ARCH']
sys.path.append(os.path.join(CMSSW_BASE,'bin', SCRAM_ARCH))
from SAMADhi import Dataset, Sample, DbStore

def get_sample(iSample):
    dbstore = DbStore()
    resultset = dbstore.find(Sample, Sample.sample_id == iSample)
    return list(resultset.values(Sample.name, Sample.path))

def createJson(indices, write = False):
    samples = {}
    for isample in indices:
        db_name, path,  = map(str, get_sample(isample)[0])
#        print path, db_name
        d = {}
        d["path"] = path
        d["db_name"] = db_name
        d["tree_name"] = "t"
        d["sample_cut"] = "1."
        samples[db_name] = d
        print isample, d
#        print samples
    if write:
        with open('samples.json', 'w') as fp:
            json.dump(samples, fp)

    return samples

if __name__ == '__main__':
    # Indices of the SAMADhi entries you want to run on
    sampleIndices = [517]

    createJson(sampleIndices, True)

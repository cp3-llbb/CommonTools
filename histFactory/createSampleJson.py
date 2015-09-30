#!/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/bin/python

import os, sys
import json

CMSSW_BASE = os.environ['CMSSW_BASE']
SCRAM_ARCH = os.environ['SCRAM_ARCH']
sys.path.append(os.path.join(CMSSW_BASE,'bin', SCRAM_ARCH))
from SAMADhi import Dataset, Sample, DbStore

def get_sample(iSample):
    dbstore = DbStore()
    resultset = dbstore.find(Sample, Sample.sample_id == iSample)
    return list(resultset.values(Sample.name, Sample.path))

def main():
    samples = {}
    for isample in xrange(436, 462+1):
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
    with open('samples.json', 'w') as fp:
        json.dump(samples, fp) 

if __name__ == '__main__':
    main()

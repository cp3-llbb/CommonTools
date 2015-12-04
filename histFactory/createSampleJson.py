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

import argparse

def get_sample(iSample):
    dbstore = DbStore()
    resultset = dbstore.find(Sample, Sample.sample_id == iSample)
    return resultset.one()

def createJson(indices, output):
    samples = {}
    for isample in indices:
        sample = get_sample(isample)

        d = {}
        d["files"] = ["/storage/data/cms" + x.lfn for x in sample.files]
        d["db_name"] = sample.name
        d["tree_name"] = "t"
        d["sample_cut"] = "1."
        samples[sample.name] = d

    with open(output, 'w') as fp:
        json.dump(samples, fp)
        print("Output saved as %r" % output)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Create a JSON file from a set of database id.')

    parser.add_argument('ids', type=int, nargs='+', help='IDs of the samples', metavar='ID')
    parser.add_argument('-o', '--output', dest='output', default='samples.json', help='Name of output JSON file')

    options = parser.parse_args()

    createJson(options.ids, options.output)

#!/usr/bin/env python2

import sys
try:
    from cp3_llbb.CommonTools.samadhi_imports import DbStore, Sample
except ImportError, e:
    print "Problem importing necessary symbols (needs CMSSW environment, set up with `cmsenv`): {0}".format(str(e))
    sys.exit(1)

import json

import argparse

def get_sample(iSample):
    dbstore = DbStore()
    resultset = dbstore.find(Sample, Sample.sample_id == iSample)
    return resultset.one()

def createJson(indices, output, rescale):
    samples = {}
    for isample in indices:
        sample = get_sample(isample)

        rescale_sample = rescale

        is_data = False
        if sample.source_dataset.datatype == u"data":
            rescale_sample = False
            is_data = True

        if rescale_sample and sample.source_dataset.xsection == 1.0:
            print("Warning: cross-section for dataset %r not set." % sample.source_dataset.name)
            rescale_sample = False

        d = {}
        d["files"] = ["/storage/data/cms" + x.lfn for x in sample.files]
        d["db_name"] = sample.name
        d["tree_name"] = "t"
        d["sample_cut"] = "1."
        d["is-data"] = is_data

        if rescale_sample:
            d["event-weight-sum"] = sample.event_weight_sum
            d["cross-section"] = sample.source_dataset.xsection
            if sample.extras_event_weight_sum:
                d["extras-event-weight-sum"] = json.loads(sample.extras_event_weight_sum)

        samples[sample.name] = d

    with open(output, 'w') as fp:
        json.dump(samples, fp)
        print("Output saved as %r" % output)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Create a JSON file from a set of database id.')

    parser.add_argument('ids', type=int, nargs='+', help='IDs of the samples', metavar='ID')
    parser.add_argument('-o', '--output', dest='output', default='samples.json', help='Name of output JSON file')
    parser.add_argument('-s', '--rescale', dest='rescale', action='store_true', help='Store cross-section and sum of event weight in the output JSON file. These values are used to rescale histograms.')

    options = parser.parse_args()

    createJson(options.ids, options.output, options.rescale)

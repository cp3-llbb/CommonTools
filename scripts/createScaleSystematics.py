#! /usr/bin/env python

import argparse
import re
import sys

from cp3_llbb.CommonTools.HistogramTools import getEnvelopHistograms

parser = argparse.ArgumentParser(description='Create scale variation systematics histograms.')

parser.add_argument('inputs', metavar='input', nargs='+', help='The ROOT input file containing histograms')

args = parser.parse_args()

import ROOT

for input in args.inputs:

    print("Working on %r...") % input
    f = ROOT.TFile.Open(input)
    if not f or f.IsZombie():
        continue

    # List keys
    variations = {}
    for key in f.GetListOfKeys():
        if '__scale' in key.GetName() and "__scaleup" not in key.GetName() and "__scaledown" not in key.GetName():
            name = re.sub('__.*$', '', key.GetName())
            var = variations.setdefault(name, [])
            var.append(key.ReadObj())

    # Ensure we have all uncertainties
    to_remove = []
    for key, values in variations.items():
        if len(values) != 6:
            print("Warning: I was expecting 6 scale variations, but I got %d for %r" % (len(values), key))
            to_remove.append(key)

    for n in to_remove:
        del variations[n]

    envelop = {}
    for key, var in variations.items():
        nominal = f.Get(key)

        env = getEnvelopHistograms(nominal, var)
        env[0].SetName(nominal.GetName() + "__scaleup")
        env[1].SetName(nominal.GetName() + "__scaledown")

        envelop[key] = env

    # Re-open the file in write mode
    f.Close()
    f = ROOT.TFile.Open(input, "update")

    for key, env in envelop.items():
        env[0].Write('', ROOT.TObject.kOverwrite)
        env[1].Write('', ROOT.TObject.kOverwrite)

    f.Close()

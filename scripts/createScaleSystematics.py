#! /usr/bin/env python

import argparse
import re
import sys

from cp3_llbb.CommonTools.HistogramTools import getEnvelopHistograms

parser = argparse.ArgumentParser(description='Create scale variation systematics histograms.')

parser.add_argument('inputs', metavar='input', nargs='+', help='The ROOT input file containing histograms')
parser.add_argument('-s', '--syst', metavar='scale', nargs='+', help='Name of the systematics of which the envelope is needed')

args = parser.parse_args()

import ROOT

for input in args.inputs:

    print("Working on %r...") % input
    f = ROOT.TFile.Open(input)
    if not f or f.IsZombie():
        continue

    envelopes = []

    for syst in args.syst:
        # List keys
        variations = {}
        for key in f.GetListOfKeys():
            if re.match(".*__{}[0-9]$".format(syst), key.GetName()) and not re.match(".*__{}up$".format(syst), key.GetName()) and not re.match(".*__{}down$".format(syst), key.GetName()):
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
            env[0].SetName(nominal.GetName() + "__{}up".format(syst))
            env[1].SetName(nominal.GetName() + "__{}down".format(syst))

            envelop[key] = env
        envelopes.append(envelop)

    # Re-open the file in write mode
    f.Close()
    f = ROOT.TFile.Open(input, "update")

    for envelop in envelopes:
        for key, env in envelop.items():
            env[0].Write('', ROOT.TObject.kOverwrite)
            env[1].Write('', ROOT.TObject.kOverwrite)

    f.Close()

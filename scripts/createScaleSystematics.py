#! /usr/bin/env python

import argparse
import sys

parser = argparse.ArgumentParser(description='Create scale variation systematics histograms.')

parser.add_argument('input', metavar='input', nargs=1, help='The ROOT input file containing histograms')
parser.add_argument('nominal', metavar='nominal', nargs=1, help='The name of the nominal histogram')

args = parser.parse_args()

import ROOT

f = ROOT.TFile.Open(args.input[0])
if not f:
    sys.exit(1)

nominal = f.Get(args.nominal[0])
if not nominal:
    print("%r not found in input file" % args.nominal[0])
    sys.exit(1)

scale_variations = []
for x in range(0, 6):
    scale_variations.append("%s__scale%d" % (args.nominal[0], x))

# Check that all histograms are in the input root file
for v in scale_variations:
    h = f.Get(v)
    if not h:
        print("%r not found in input file" % v)
        sys.exit(2)

# All good, call the script doing the job

args = ['./getEnvelopHistogram.py', '-i', '-s', 'scale', args.input[0], args.nominal[0]]
args += scale_variations

import subprocess
subprocess.call(args)

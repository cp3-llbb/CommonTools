#! /usr/bin/env python

import argparse
import ROOT as R
from array import array

parser = argparse.ArgumentParser(description="For a given variable, find bin limits needed to build a flat distribution.")
parser.add_argument('-i', '--input', nargs='+', help='Input files containing TTrees', required=True)
parser.add_argument('-c', '--cut', help='Formula to cut on events', default="1")
parser.add_argument('-v', '--variable', help='Branch for the variable to be flattened', required=True)
parser.add_argument('-w', '--weight', help='Branch for the event weight', default="1")
parser.add_argument('-n', '--nbins', type=int, help='Number of bins desired', required=True)
parser.add_argument('-o', '--output', help='Output file containing validation histogram', default="test.root")

args = parser.parse_args()

value_list = []
weight_sum = 0.

for file in args.input:
    print("Working on " + file)

    tfile = R.TFile.Open(file)
    tree = tfile.Get("t")

    try:
        xs = tfile.Get("cross_section").GetVal()
        wgt_sum = tfile.Get("event_weight_sum").GetVal()
        print "Found XS = {}, event weight sum = {}".format(xs, wgt_sum)
    except AttributeError:
        xs = 1.
        wgt_sum = 1.
        print "Did not find XS or event weight sum info, will use 1."

    if args.cut != "1":
        cut = R.TTreeFormula("cut", args.cut, tree)
    else:
        cut = None

    for event in tree:
        if cut is not None and not cut.EvalInstance():
            continue

        weight = tree.__getattr__(args.weight) if args.weight is not "1" else 1.
        weight *= xs / wgt_sum
        var = tree.__getattr__(args.variable)
        value_list.append( [var, weight] )
        weight_sum += weight

    tfile.Close()

print "Sorting values..."
value_list.sort(key=lambda x: x[0])

# Careful to avoid having twice the same values (can happen a lot for e.g. BDTs)!
# In those cases the algorithm for bin limits will not work
# => Remove duplicates but keep their weights
print "Removing duplicates..."
new_value_list = []
for i, entry in enumerate(value_list):
    if i > 0 and new_value_list[-1][0] == entry[0]:
        new_value_list[-1][1] += entry[1]
        continue
    new_value_list.append(entry[:])
print "Found {} duplicates!".format(len(value_list) - len(new_value_list))

bin_limits = [ new_value_list[0][0] ]
current_bin = new_value_list[0][1]

weight_avg = weight_sum/len(value_list)
ratio = (weight_sum) / args.nbins
print "Finding bin edges..."
print "Target weight per bin: ", ratio
print "Avg. event weight: ", weight_avg
print "Total event weight: ", weight_sum
print "Total event count, duplicates removed: ", len(value_list)

print "Starting bin edge: ", new_value_list[0][0]
for i, entry in enumerate(new_value_list):
    if current_bin >= ratio and i != 0:
        slope = new_value_list[i-1][1] / ( entry[0] - new_value_list[i-1][0] )
        next_value = new_value_list[i-1][0] + (ratio - current_bin + new_value_list[i-1][1]) / slope
        bin_limits.append(next_value)
        print "Adding bin: {}".format(next_value)
        print "Current sum of weights: ", current_bin
        print "Previous sum of weights: ", current_bin - entry[1]
        # We have to be careful: the weight in the next bin is not the weight of the first event in it,
        # it has to be corrected for the fact that the bin limit found is between two events
        current_bin = slope*(entry[0] - next_value)
    current_bin += entry[1]
    if len(bin_limits) == args.nbins:
        print "Last bin reached."
        print "Remaining sum of weights: ", sum([ val[1] for val in new_value_list[i:-1]])
        print "Adding bin: {}".format(new_value_list[-1][0])
        bin_limits.append(new_value_list[-1][0])
        break

print "Bin limits:"
print bin_limits

print "Filling validation histograms..."
out_file = R.TFile(args.output, "recreate")

# Fill with all the actual events read
testHisto = R.TH1F(args.variable, "", len(bin_limits) - 1, array('f', bin_limits))
for entry in value_list:
    testHisto.Fill(entry[0], entry[1])
testHisto.Write()

# Fill with duplicates removed & corrected weights
testHistoDupl = R.TH1F(args.variable + "_dupl", "", len(bin_limits) - 1, array('f', bin_limits))
for entry in new_value_list:
    testHistoDupl.Fill(entry[0], entry[1])
testHistoDupl.Write()

out_file.Close()

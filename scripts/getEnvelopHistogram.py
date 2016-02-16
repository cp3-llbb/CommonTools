#! /usr/bin/env python

import ROOT
import argparse
import sys

def getEnvelopHistograms(nominal, variations):
    """
    Compute envelop histograms create by all variations histograms. The envelop is simply the maximum
    and minimum deviations from nominal for each bin of the distribution
    """

    if len(variations) < 2:
        raise TypeError("At least two variations histograms must be provided")

    n_bins = nominal.GetNbinsX()
    for v in variations:
        if v.GetNbinsX() != n_bins:
            raise RuntimeError("Variation histograms do not have the same binning as the nominal histogram")

    up = nominal.Clone()
    up.SetDirectory(ROOT.nullptr)
    up.Reset()

    down = nominal.Clone()
    down.SetDirectory(ROOT.nullptr)
    down.Reset()

    for i in range(1, n_bins + 1):
        minimum = float("inf")
        maximum = float("-inf")

        for v in variations:
            c = v.GetBinContent(i)
            minimum = min(minimum, c)
            maximum = max(maximum, c)

        up.SetBinContent(i, maximum)
        down.SetBinContent(i, minimum)

    return (up, down)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Create an envelop histogram from a set of histograms.')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-o', '--output', help='The ROOT output file')
    group.add_argument('-i', '--in-place', action='store_true', help='If set, update the input ROOT file with the envelop histograms')
    parser.add_argument('-s', '--suffix', default='', help='The suffix used to create the envelop histograms names')

    parser.add_argument('input', metavar='input', nargs=1, help='The ROOT input file containing histograms')
    parser.add_argument('nominal', metavar='nominal', nargs=1, help='The name of the nominal histogram')
    parser.add_argument('variations', metavar='variation', nargs='+', help='The name of the variation histograms')

    args = parser.parse_args()

    input = ROOT.TFile.Open(args.input[0])
    if not input:
        sys.exit(1)

    nominal = input.Get(args.nominal[0])
    if not nominal:
        sys.exit(1)
    nominal.SetDirectory(ROOT.nullptr)

    variations = []
    for x in args.variations:
        variations.append(input.Get(x))

    up, down = getEnvelopHistograms(nominal, variations)
    up.SetName(nominal.GetName() + "__%sup" % args.suffix)
    down.SetName(nominal.GetName() + "__%sdown" % args.suffix)

    if args.in_place:
        # Re-open in UPDATE mode
        input.Close()
        input = ROOT.TFile.Open(args.input[0], "update")
        up.Write('', ROOT.TObject.kOverwrite)
        down.Write('', ROOT.TObject.kOverwrite)

        print("%r and %r successfully added to %r" % (up.GetName(), down.GetName(), args.input[0]))
    else:
        output = ROOT.TFile.Open(args.output, "recreate")
        nominal.Write()
        up.Write()
        down.Write()
        output.Close()

        print("%r and %r saved to %r" % (up.GetName(), down.GetName(), args.output))

    input.Close()

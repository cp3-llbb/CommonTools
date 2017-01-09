#! /usr/bin/env python

import ROOT
import re

def getEnvelopHistograms(nominal, variations):
    """
    Compute envelop histograms create by all variations histograms. The envelop is simply the maximum
    and minimum deviations from nominal for each bin of the distribution

    Arguments:

    nominal: The nominal histogram
    variations: a list of histograms to compute the envelop from
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

def getHistogramsFromFileRegex(file, regex, veto=None):
    """
    Return all histograms found in a file whose name matches a regexp.

    Arguments:

    file: Path to the considered file
    regex: Regexp to match the histogram names
    veto: Also a regexp. If specified, will not consider histograms matching the veto.

    Returns: Dictionary with (key, value) = (name, histogram)
    """

    myRe = re.compile(regex)
    try:
        myReVeto = re.compile(veto)
    except TypeError:
        myReVeto = None

    foundHistos = {}

    r_file = ROOT.TFile.Open(file)
    if not r_file or not r_file.IsOpen():
        raise Exception("Could not open file {}".format(file))

    content = r_file.GetListOfKeys()
    
    for key in content:
        name = key.GetName()

        if myRe.match(name) is not None:
            if myReVeto is not None:
                if myReVeto.match(name) is not None:
                    continue
            
            item = key.ReadObj()
            
            if not item.InheritsFrom("TH1"):
                continue
            
            item.SetDirectory(0)
            foundHistos[name] = item

    r_file.Close()

    return foundHistos



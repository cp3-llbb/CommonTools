#!/bin/env python
# Read some trees, output an histo
# O. Bondu (September 2015)
import argparse
import os, sys
import json
import ROOT
from ROOT import TFile, TTree, TChain, TCanvas, TH1D, TLorentzVector
ROOT.gROOT.Reset()
ROOT.gROOT.SetBatch()


def get_options():
    """
    Parse and return the arguments provided by the user.
    """
    parser = argparse.ArgumentParser(description='Plotter')
    parser.add_argument('-s', '--samples', type=str, required=True, action='append', dest='samples', metavar='FILE',
                        help='samples which are to be considered for the plots')
    parser.add_argument('-p', '--plots', type=str, required=True, action='append', dest='plots', metavar='FILE',
                        help='plots which are to be done')
    options = parser.parse_args()
    return options

def main(samples, plots):
    c1 = TCanvas()
    for ksample in samples:
        print 'Treating sample', ksample
        name = str(ksample)
        dbname = samples[ksample]["db_name"]
        dirpath = samples[ksample]["path"]
        file = "output*root"
        tree = str(samples[ksample]["tree_name"])
        sample_cut = str(samples[ksample]["sample_cut"])
        outfile = ROOT.TFile(dbname + "_histos.root", "recreate")
        for kplot in plots:
            print "\tNow taking care of plot", kplot
            name2 = str(kplot)
            variable = str(plots[kplot]["variable"])
            plot_cut = str(plots[kplot]["plot_cut"])
            binning = str(plots[kplot]["binning"])
            xnbin, xlow, xhigh = map(float, binning.strip().strip("()").split(","))
            chain = TChain(tree)
            chain.Add( os.path.join(dirpath, "output*root") )
            total_cut = plot_cut
            if sample_cut == "": sample_cut = "1"
            total_cut = "(" + plot_cut + ") * event_weight * (" + sample_cut + ")"
            chain.Draw(variable + ">>h_tmp" + binning, total_cut)
            h = ROOT.gDirectory.Get("h_tmp")
            h.Sumw2()
            h.SetName(name2)
            h.Write()
        outfile.Write()
        outfile.Close()


if __name__ == '__main__':
    options = get_options()
    print "##### Read samples to be processed"
    samples = {}
    for sample in options.samples:
        print "opening sample file", sample
        with open(sample) as f:
            samples.update(json.load(f))
    print "##### Read plots to be processed"
    plots = {}
    for plot in options.plots:
        with open(plot) as f:
            plots.update(json.load(f))
    print "##### Now creating the histos"
    main(samples, plots)


import ROOT as R
import copy, sys, os, inspect 

# Usage from histFactory/plots/HHAnalysis/ : ./../../build/createHistoWithMultiDraw.exe -d ../../samples.json generatePlots.py 
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
from basePlotter import BasePlotter
from HHAnalysis import HH
from ScaleFactors import *

plots = []
basePlotter = BasePlotter()

categories = ["ElEl","MuMu","MuEl"]

# Order for llmetjj maps : lepid1, lepiso1, lepid2, lepiso2, jetid1, jetid2, btagWP1, btagWP2, pair
workingPoints = [ ["T","T","T","T","L","L","no","no","csv"], ["T","T","T","T","L","L","L","L","csv"] ]

for WP in workingPoints :
    lepid1 = getattr(HH.lepID, WP[0])
    lepiso1 = getattr(HH.lepIso, WP[1])
    lepid2 = getattr(HH.lepID, WP[2])
    lepiso2 = getattr(HH.lepIso, WP[3])
    jetid1 = getattr(HH.jetID, WP[4])
    jetid2 = getattr(HH.jetID, WP[5])
    btagWP1 = getattr(HH.btagWP, WP[6])
    btagWP2 = getattr(HH.btagWP, WP[7])
    pair = getattr(HH.jetPair, WP[8])
    basePlotter.mapWP = HH.leplepIDIsojetjetIDbtagWPPair(lepid1, lepiso1, lepid2, lepiso2, jetid1, jetid2, btagWP1, btagWP2, pair)
    basePlotter.lepMapWP = HH.lepIDIso(lepid1, lepiso1)
    basePlotter.jetMapWP = btagWP1 # To Be Updated once jet map includes jetID
    basePlotter.llIsoCat = HH.lepIso.map.at(lepiso1)+HH.lepIso.map.at(lepiso2)
    basePlotter.llIDCat = HH.lepID.map.at(lepid1)+HH.lepID.map.at(lepid2)
    basePlotter.jjIDCat = HH.jetID.map.at(jetid1)+HH.jetID.map.at(jetid2)
    basePlotter.jjBtagCat = HH.btagWP.map.at(btagWP1)+HH.btagWP.map.at(btagWP2)
    basePlotter.suffix = "_"+HH.jetPair.map.at(pair)+"Ordered"
    print basePlotter.suffix
    basePlotter.generatePlots(categories)
    plotFamilies = ["plots_lep", "plots_mu", "plots_el", "plots_jet", "plots_met", "plots_ll", "plots_jj", "plots_llmetjj","plots_evt"]
    for plotFamily in plotFamilies :
        for plot in getattr(basePlotter, plotFamily) :
            # scale factors
            plot["weight"] = "event_weight * " + get_leptons_SF(basePlotter.ll_str, lepid1, lepid2, lepiso1, lepiso2)
            print plot
            plots.append(plot)





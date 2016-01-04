import ROOT as R
import copy, sys, os, inspect 

# Usage from histFactory/plots/HHAnalysis/ : ./../../build/createHistoWithMultiDraw.exe -d ../../samples.json generatePlots.py 
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
from basePlotter import *
from HHAnalysis import HH

plots = []
basePlotter = BasePlotter()

categories = ["ElEl", "MuMu", "MuEl"]

# Order for llmetjj maps : lepid1, lepiso1, lepid2, lepiso2, jetid1, jetid2, btagWP1, btagWP2, pair
workingPoints = [ ["T","T","T","T","L","L","no","no","csv"], ["T","T","T","T","L","L","L","L","csv"] ]

for WP in workingPoints :

    basePlotter.lepid1 = getattr(HH.lepID, WP[0])
    basePlotter.lepiso1 = getattr(HH.lepIso, WP[1])
    basePlotter.lepid2 = getattr(HH.lepID, WP[2])
    basePlotter.lepiso2 = getattr(HH.lepIso, WP[3])
    basePlotter.jetid1 = getattr(HH.jetID, WP[4])
    basePlotter.jetid2 = getattr(HH.jetID, WP[5])
    basePlotter.btagWP1 = getattr(HH.btagWP, WP[6])
    basePlotter.btagWP2 = getattr(HH.btagWP, WP[7])
    basePlotter.pair = getattr(HH.jetPair, WP[8])

    basePlotter.generatePlots(categories)

    plotFamilies = ["plots_lep", "plots_jet", "plots_met", "plots_ll", "plots_jj", "plots_llmetjj","plots_evt"]
    for plotFamily in plotFamilies :
        for plot in getattr(basePlotter, plotFamily) :
            # scale factors
            plot["weight"] = "event_weight" 
            # can be uncommented as soon as we have a new prod with proper SF treatement
            #if not "scaleFactor" in plot["name"] : 
            #    plot["weight"] += " * " + get_leptons_SF(basePlotter.ll_str, basePlotter.lepid1, basePlotter.lepid2, basePlotter.lepiso1, basePlotter.lepiso2)
            #    plot["weight"] += " * " + get_csvv2_sf(basePlotter.btagWP1, basePlotter.jet1_fwkIdx)
            #    plot["weight"] += " * " + get_csvv2_sf(basePlotter.btagWP2, basePlotter.jet2_fwkIdx)
            plots.append(plot)




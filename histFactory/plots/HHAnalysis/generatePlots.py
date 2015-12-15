import ROOT as R
import copy, sys, os, inspect 

# Usage from histFactory/plots/HHAnalysis/ : ./../../build/createHistoWithMultiDraw.exe -d ../../samples.json generatePlots.py 
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
from basePlotter import BasePlotter
from mapFacilities import getIndx_llmetjj_id_iso_btagWP_pair, getIndx_ll_id_iso, getIndx_l_id_iso, getIndx_j_bTagWP
# NB: llmetjj map is lepid1, lepiso1, lepid2, lepiso2, jetid1, jetid2, btagWP1, btagWP2, pair

plots = []
basePlotter = BasePlotter()

categories = ["ElEl","MuMu","MuEl"]

#workingPoints = {"zVeto_csv_LL": ["T","T","T","T","no","no","csv"], "zVeto_pt_LL": ["T","T","T","T","no","no","pt"], "zVeto_ht_LL": ["T","T","T","T","no","no","ht"], "zVeto_mh_LL": ["T","T","T","T","no","no","mh"], "zVeto_ptOverM_LL": ["T","T","T","T","no","no","ptOverM"]}
workingPoints = [ ["T","T","T","T","L","L","no","no","csv"], ["T","T","T","T","L","L","L","L","csv"] ]
for WP in workingPoints :
    lepid1 = WP[0]
    lepiso1 = WP[1]
    lepid2 = WP[2]
    lepiso2 = WP[3]
    jetid1 = WP[4]
    jetid2 = WP[5]
    btagWP1 = WP[6]
    btagWP2 = WP[7]
    pair = WP[8]
    basePlotter.mapWP = getIndx_llmetjj_id_iso_btagWP_pair(lepid1, lepiso1, lepid2, lepiso2, btagWP1, btagWP2, pair)
    basePlotter.jetMapWP = getIndx_j_bTagWP(btagWP1)
    basePlotter.lepMapWP = getIndx_l_id_iso(lepid1, lepiso1)
    basePlotter.llIsoCat = lepiso1+lepiso2
    basePlotter.llIDCat = lepid1+lepid2
    basePlotter.jjBtagCat = btagWP1+btagWP2
    basePlotter.suffix = "_"+pair+"Ordered"
    basePlotter.generatePlots(categories)
    plotFamilies = ["plots_lep", "plots_mu", "plots_el", "plots_jet", "plots_met", "plots_ll", "plots_jj", "plots_llmetjj","plots_evt"]
    for plotFamily in plotFamilies :
        for plot in getattr(basePlotter, plotFamily) :
            plots.append(plot)





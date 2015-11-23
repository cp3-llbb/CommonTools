import ROOT as R
import copy, sys, os, inspect 

# Usage from histFactory/plots/HHAnalysis/ : ./../../build/createHistoWithMultiDraw.exe -d ../../samples.json generatePlots.py 
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
from basePlotter import BasePlotter
from mapFacilities import getIndx_llmetjj_id_iso_btagWP_pair, getIndx_ll_id_iso, getIndx_l_id_iso, getIndx_j_bTagWP

plots = []
basePlotter = BasePlotter()

categories = ["ElEl","MuMu","MuEl"]

dict_WPnames_wps = { "zVeto_nono": ["L","L","L","L","no","no","ht"], "zVeto_LL": ["L","L","L","L","L","L","ht"], "zVeto_MM": ["L","L","L","L","M","M","ht"],  "zVeto_csv_nono": ["L","L","L","L","no","no","csv"], "zVeto_csv_LL": ["L","L","L","L","L","L","csv"], "zVeto_csv_MM": ["L","L","L","L","M","M","csv"] }
for WPname in dict_WPnames_wps.keys() :
    lepid1 = dict_WPnames_wps[WPname][0]
    lepiso1 = dict_WPnames_wps[WPname][1]
    lepid2 = dict_WPnames_wps[WPname][2]
    lepiso2 = dict_WPnames_wps[WPname][3]
    btagWP1 = dict_WPnames_wps[WPname][4]
    btagWP2 = dict_WPnames_wps[WPname][5]
    pair = dict_WPnames_wps[WPname][6]
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





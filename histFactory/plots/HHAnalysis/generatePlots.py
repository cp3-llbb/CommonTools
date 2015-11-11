import ROOT as R
import copy, sys, os, inspect

# Usage from histFactory/plots/HHAnalysis/ : ./../../build/createHistoWithMultiDraw.exe -d ../../samples.json generatePlots.py 
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
from basePlotter import BasePlotter


pathCMS = os.getenv("CMSSW_BASE")
if pathCMS == "":
    raise Exception("CMS environment is not valid!")
pathHH = os.path.join(pathCMS, "src/cp3_llbb/HHAnalysis/")
R.gROOT.ProcessLine("#include <%s/interface/Enums.h>"%pathHH) 
 
def getIndx_llmetjj_id_iso_btagWP_order(lepid1, lepiso1, lepid2, lepiso2, btagWP1, btagWP2, order): 
    bitA = R.jetPair.Count 
    bitB = bitA * R.btagWP.Count 
    bitC = bitB * R.btagWP.Count 
    bitD = bitC * R.lepIso.Count 
    bitE = bitD * R.lepID.Count 
    bitF = bitE * R.lepIso.Count 
    return bitF * getattr(R.lepID,lepid1) + bitE * getattr(R.lepIso,lepiso1) + bitD * getattr(R.lepID,lepid2) + \
           bitC * getattr(R.lepIso,lepiso2) + bitB * getattr(R.btagWP,btagWP1) + bitA * getattr(R.btagWP,btagWP2) + getattr(R.jetPair,order)  
def getIndx_l_id_iso(lepid, lepiso):
    bitA = R.lepIso.Count
    return bitA * getattr(R.lepID, lepid) + getattr(R.lepIso, lepiso)
def getIndx_j_bTagWP(btagWP):
    return getattr(R.btagWP, btagWP)

plots = []
basePlotter = BasePlotter()

categories = ["ElEl","MuMu","MuEl"]

dict_WPnames_wps = { "zVeto_nono": ["L","L","L","L","no","no","ht"], "zVeto_LL": ["L","L","L","L","L","L","ht"], "zVeto_MM": ["L","L","L","L","M","M","ht"], "zVeto_TT": ["L","L","L","L","T","T","ht"] }
for WPname in dict_WPnames_wps.keys() :
    lepid1 = dict_WPnames_wps[WPname][0]
    lepiso1 = dict_WPnames_wps[WPname][1]
    lepid2 = dict_WPnames_wps[WPname][2]
    lepiso2 = dict_WPnames_wps[WPname][3]
    btagWP1 = dict_WPnames_wps[WPname][4]
    btagWP2 = dict_WPnames_wps[WPname][5]
    order = dict_WPnames_wps[WPname][6]
    basePlotter.mapWP = getIndx_llmetjj_id_iso_btagWP_order(lepid1, lepiso1, lepid2, lepiso2, btagWP1, btagWP2, order)
    basePlotter.jetMapWP = getIndx_j_bTagWP(btagWP1)
    basePlotter.lepMapWP = getIndx_l_id_iso(lepid1, lepiso1)
    basePlotter.llIsoCat = lepiso1+lepiso2
    basePlotter.llIDCat = lepid1+lepid2
    basePlotter.jjBtagCat = btagWP1+btagWP2
    basePlotter.suffix = "_"+order+"Ordered"
    basePlotter.generatePlots(categories)
    plotFamilies = ["plots_lep", "plots_mu", "plots_el", "plots_jet", "plots_met", "plots_ll", "plots_jj", "plots_llmetjj","plots_evt"]
    for plotFamily in plotFamilies :
        for plot in getattr(basePlotter, plotFamily) :
            plots.append(plot)





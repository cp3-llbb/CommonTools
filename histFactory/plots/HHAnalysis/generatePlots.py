import ROOT as R
import copy, sys, os, inspect

# Usage from histFactory/plots/HHAnalysis/ : ./../../build/createHistoWithMultiDraw.exe -d ../../samples.json generatePlots.py 
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
from basePlotter_Map import BasePlotter


pathCMS = os.getenv("CMSSW_BASE")
if pathCMS == "":
    raise Exception("CMS environment is not valid!")
pathHH = os.path.join(pathCMS, "src/cp3_llbb/HHAnalysis/")
R.gROOT.ProcessLine("#include <%s/interface/Enums.h>"%pathHH) 
 
def getIndx_llmetjj_id_iso_btagWP_pair(lepid1, lepiso1, lepid2, lepiso2, btagWP1, btagWP2, pair): 
    bitA = R.jetPair.Count 
    bitB = bitA * R.btagWP.Count 
    bitC = bitB * R.btagWP.Count 
    bitD = bitC * R.lepIso.Count 
    bitE = bitD * R.lepID.Count 
    bitF = bitE * R.lepIso.Count 
    return bitF * getattr(R.lepID,lepid1) + bitE * getattr(R.lepIso,lepiso1) + bitD * getattr(R.lepID,lepid2) + \
           bitC * getattr(R.lepIso,lepiso2) + bitB * getattr(R.btagWP,btagWP1) + bitA * getattr(R.btagWP,btagWP2) + getattr(R.jetPair,pair)  

plots = []
basePlotter = BasePlotter()

categories = ["ElEl","MuMu","MuEl"]
basePlotter.mapWP = getIndx_llmetjj_id_iso_btagWP_pair("T", "T", "T", "T", "no", "no", "ht")
basePlotter.llIsoCat = "TT"
basePlotter.llIDCat = "TT"
basePlotter.jjBtagCat = "nono"
basePlotter.suffix = "_leadingHt"

basePlotter.generatePlots(categories)
plotFamilies = ["plots_lep", "plots_mu", "plots_el", "plots_jet", "plots_met", "plots_ll", "plots_jj", "plots_llmetjj"]
for plotFamily in plotFamilies :
    for plot in getattr(basePlotter, plotFamily) :
        plots.append(plot)
# Add plots for LL btagging
myPlots_bb = copy.deepcopy(basePlotter) 
myPlots_bb.mapWP = getIndx_llmetjj_id_iso_btagWP_pair("T", "T", "T", "T", "L", "L", "ht")
myPlots_bb.jjBtagCat = "LL" 
myPlots_bb.generatePlots(categories)
for plotFamily in plotFamilies :
    for plot in getattr(myPlots_bb, plotFamily) :
        plots.append(plot)





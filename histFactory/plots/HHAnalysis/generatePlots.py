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

# Here is an example for lepton id Loose, iso Loose, with no bTag. Doing the plots only for the llmetjj candidate with leading ht
categories = ["ElEl","MuMu","MuEl"]
basePlotter.mapWP = getIndx_llmetjj_id_iso_btagWP_pair("L", "L", "L", "L", "no", "no", "ht")
basePlotter.llIsoCat = "LL"
basePlotter.llIDCat = "LL"
basePlotter.jjBtagCat = "nono"
basePlotter.suffix = "_leadingHt"

basePlotter.generatePlots(categories)
for plot in basePlotter.plots_lep:
    print plot
    plots.append(plot)
for plot in basePlotter.plots_jet:
    print plot
    plots.append(plot)
# Add plots for LL btagging
myPlots_bb = copy.deepcopy(basePlotter) 
myPlots_bb.mapWP = getIndx_llmetjj_id_iso_btagWP_pair("L", "L", "L", "L", "L", "L", "ht")
myPlots_bb.jjBtagCat = "LL" 
myPlots_bb.generatePlots(categories)
for plot in myPlots_bb.plots_lep:                                                                  
    print plot
    plots.append(plot)
for plot in myPlots_bb.plots_jet:                                                                      
    print plot
    plots.append(plot)





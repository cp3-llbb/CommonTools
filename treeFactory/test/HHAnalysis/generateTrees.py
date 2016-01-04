import sys

sys.path.append("../histFactory/plots/HHAnalysis")
from basePlotter import *
from HHAnalysis import HH
from ScaleFactors import *

basePlotter = BasePlotter()

WP = ["T","T","T","T","L","L","L","L","csv"]
basePlotter.lepid1 = getattr(HH.lepID, WP[0])
basePlotter.lepiso1 = getattr(HH.lepIso, WP[1])
basePlotter.lepid2 = getattr(HH.lepID, WP[2])
basePlotter.lepiso2 = getattr(HH.lepIso, WP[3])
basePlotter.jetid1 = getattr(HH.jetID, WP[4])
basePlotter.jetid2 = getattr(HH.jetID, WP[5])
basePlotter.btagWP1 = getattr(HH.btagWP, WP[6])
basePlotter.btagWP2 = getattr(HH.btagWP, WP[7])
basePlotter.pair = getattr(HH.jetPair, WP[8])

# Generate once the list of variables for the tree, need one flavour choice 
# It is IRRELEVANT for the skimmer
flavour = "MuEl"
basePlotter.generatePlots([flavour])

# Currently need to run the code several times for different selections. 
flavCut = "({0}.isElEl || {0}.isMuMu) && {0}.p4.M() > 12".format(basePlotter.ll_str)
#flavCut = "({0}.isElMu || {0}.isMuEl) && {0}.p4.M() > 12".format(basePlotter.ll_str)

cut = basePlotter.joinCuts(basePlotter.mapCut, flavCut, basePlotter.jetCut, basePlotter.lepCut, basePlotter.extraCut)

tree = {}
tree["name"] = "t"
tree["cut"] = cut
tree["branches"] = []

plotFamilies = ["plots_lep", "plots_jet", "plots_met", "plots_ll", "plots_jj", "plots_llmetjj", "plots_evt", "forSkimmer"]
for plotFamily in plotFamilies :
    for plot in getattr(basePlotter, plotFamily) :
        branch = {}
        branch["name"] = plot["name"].split("_"+flavour)[0]
        branch["variable"] = plot["variable"]
        tree["branches"].append(branch)



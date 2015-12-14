from ZACnC import *


def printInJsonNoVar(f, g, obj, objName, cut, cutName, binnings, isLastEntry):
    f.write( "        {\n")
    f.write( "        'name': '"+objName+"_"+cutName+"',\n")
    f.write( "        'variable': '"+obj+"',\n")
    f.write( "        'plot_cut': '"+cut+"',\n")
    f.write( "        'binning': '"+binnings[0]+"'\n")
    if (isLastEntry == False) :
        f.write( "        },\n")
    if (isLastEntry == True) :
        f.write( "        }]\n")

    g.write("'"+objName+"_"+cutName+"':\n")
    g.write("  x-axis: '"+objName+"_"+cutName+"'\n")
    g.write("  y-axis: 'Evt'\n")
    g.write("  y-axis-format: '%1% / %2$.0f GeV'\n")
    g.write("  normalized: false\n")
    g.write("  log-y: both\n")
    g.write("  save-extensions: ['png','pdf']\n")
    g.write("  show-ratio: true\n")


def printInJson(f, g, obj, objName, variables, variableNames, cut, cutName, binnings, isLastEntry):
    for i in range(0, len(variables)) :
        f.write( "        {\n")
        f.write( "        'name': '"+objName+"_"+variableNames[i]+"_"+cutName+"',\n")
        f.write( "        'variable': '"+obj+"."+variables[i]+"',\n")
        f.write( "        'plot_cut': '"+cut+"',\n")
        f.write( "        'binning': '"+binnings[i]+"'\n")
        if (isLastEntry == False or i < len(variables)-1) : 
            f.write( "        },\n")
        else : 
            f.write( "        }\n")
    if (isLastEntry == True) :
        f.write( "        ]\n")

    for i in range(0, len(variables)) :
        g.write("'"+objName+"_"+variableNames[i]+"_"+cutName+"':\n")
        g.write("  x-axis: '"+objName+"_"+variableNames[i]+"_"+cutName+"'\n")
        g.write("  y-axis: 'Evt'\n")
        g.write("  y-axis-format: '%1% / %2$.0f GeV'\n")
        g.write("  normalized: false\n")
        g.write("  log-y: both\n")
        g.write("  save-extensions: ['png','pdf','root']\n")
        g.write("  show-ratio: true\n")

def printInPy(f, g, cut, cutName, binning, isLastEntry):
    f.write( "        {\n")
    f.write( "        'name': '"+cutName+"',\n")
    f.write( "        'variable': '"+cut+"',\n")
    f.write( "        'plot_cut': '"+cut+"',\n")
    f.write( "        'binning': '"+binning+"'\n")
    if (isLastEntry == False or i < len(variables)-1) :
        f.write( "        },\n")
    else :
        f.write( "        }\n")
    if (isLastEntry == True) :
        f.write( "        ]\n")

    g.write("'"+cutName+"':\n")
    g.write("  x-axis: '"+cutName+"'\n")
    g.write("  y-axis: 'Evt'\n")
    g.write("  y-axis-format: '%1% / %2$.0f GeV'\n")
    g.write("  normalized: false\n")
    g.write("  log-y: both\n")
    g.write("  save-extensions: ['png','pdf']\n")
    g.write("  show-ratio: true\n")


# binnings

pt_binning  = "(30, 0, 600)"
eta_binning = "(30, -3, 3)"
phi_binning = "(30, -3.1416, 3.1416)"
lepiso_binning = "(30, 0, 0.3)"
mj_binning = "(30, 0, 30)"
csv_binning = "(20,0,1)"
DR_binning = "(15, 0, 6)"
DPhi_binning = "(10, 0, 3.1416)"
ptZ_binning = "80,0,800)"
MZ_binning = "(80,0,400)"
MZzoomed_binning = "(60,60,120)"
Mjj_binning = "(30,0,600)"
Mlljj_binning = "(40,0,2400)"
met_binning = "(40,0,400)"
Nj_binning = "(8,0,8)"
nPV_binning = "(50,0,50)"
fj_mass_binning = "(20,0,400)"
tau_binning = "(10,0,1)"
subjetDR_binning = "(20,0,1)"


# Leptons variables

l1 = "za_dilep_ptOrdered[0]"
l2 = "za_dilep_ptOrdered[1]"

l1Name = "lep_pt1"
l2Name = "lep_pt2"

l_var = ["p4.Pt()", "p4.Eta()", "p4.Phi()", "isoValue"]
l_varName = ["Pt", "Eta", "Phi", "isoValue"]

l_binning = [pt_binning, eta_binning, phi_binning, lepiso_binning]

# Jets variables

j1pt = "za_dijet_ptOrdered[0]"
j2pt = "za_dijet_ptOrdered[1]"
j1csv = "za_dijet_CSVv2Ordered[0]"
j2csv = "za_dijet_CSVv2Ordered[1]"

j1ptName = "jet_pt1"
j2ptName = "jet_pt2"
j1csvName = "jet_CSV1"
j2csvName = "jet_CSV2"

j_var = ["p4.Pt()", "p4.Eta()", "p4.Phi()", "p4.M()", "CSVv2", "minDRjl" ]
j_varName = ["Pt", "Eta", "Phi", "M", "CSVv2", "minDRjl"]
j_binning = [pt_binning, eta_binning, phi_binning, mj_binning, csv_binning, DR_binning]

# FAT jets

fj = "za_selFatJets[0]"
fjName = "fat-Jet"

fj_var = ["softdrop_mass","trimmed_mass","pruned_mass","filtered_mass","tau1","tau2","tau3","subjetDR"]
fj_varName = ["softdrop_mass","trimmed_mass","pruned_mass","filtered_mass","tau1","tau2","tau3","subjetDR"]

fj_binning = [fj_mass_binning,fj_mass_binning,fj_mass_binning,fj_mass_binning,tau_binning,tau_binning,tau_binning,subjetDR_binning]

# MET variables

met = "nohf_met_p4"
metName = "nohf_met"

met_var = ["Pt()"]
met_varName = ["Pt"]
met_binning = [met_binning]
# Dilep variables

dilep = "za_diLeptons[0]"
dilepName = "ll"
dilep_var = ["p4.Pt()", "p4.Eta()", "p4.Phi()", "p4.M()","p4.M()", "DR", "DEta", "DPhi"]
dilep_varName = ["Pt", "Eta", "Phi", "M", "M", "DR", "DEta", "DPhi"]
dilep_binning = [ptZ_binning, eta_binning, phi_binning, MZ_binning, MZzoomed_binning, DR_binning, DR_binning, DPhi_binning]

# Dijet variables

dijet = "za_diJets[0]"
dijetName = "jj"
dijet_var = ["p4.Pt()", "p4.Eta()", "p4.Phi()", "p4.M()", "DR", "DEta", "DPhi"]
dijet_varName = ["Pt", "Eta", "Phi", "M", "DR", "DEta", "DPhi"]
dijet_binning = [ptZ_binning, eta_binning, phi_binning, Mjj_binning, DR_binning, DR_binning, DPhi_binning]

# Dilep-Dijet variables

dijetdilep = "za_diLepDiJets[0]"
dijetdilepName = "lljj"
dijetdilep_var = ["p4.Pt()", "p4.Eta()", "p4.Phi()", "p4.M()"]
dijetdilep_varName = ["Pt", "Eta", "Phi", "M"]
dijetdilep_binning = [pt_binning, eta_binning, phi_binning, Mlljj_binning]

# (B-)Jets Counting

selJets = "za_selJets"
selJetsName = "jets"
selJets_var = ["size()"]
selJets_varName = ["N"]
selJets_binning = [Nj_binning]

selBjets = "za_selBjetsM"
selBjetsName = "BjetsM"

# PV N

nPV = "vertex_ndof.size()"
nPVName = "nVX"
nPV_binning = [nPV_binning]

# Cuts

weights = " * event_pu_weight * event_weight"

ERewID = "1" # " * (electron_sf_id_loose[za_diLeptons[0].idxLep1][0]*electron_sf_id_loose[za_diLeptons[0].idxLep2][0])"
MRewID = "1" #" * (muon_sf_id_loose[za_diLeptons[0].idxLep1][0]*muon_sf_id_loose[za_diLeptons[0].idxLep2][0])"
MRewIso = "1" #" * (muon_sf_iso_02_loose[za_diLeptons[0].idxLep1][0]*muon_sf_iso_02_loose[za_diLeptons[0].idxLep2][0])"

CSVV2_medium_SF_weight = " * (jet_sf_csvv2_medium[za_diJets[0].idxJet1][0] * jet_sf_csvv2_medium[za_diJets[0].idxJet2][0] )))"


twoLCond = []
twoLCondName = []
twoLCond.append("mumu_Mll_cut")
twoLCond.append("elel_Mll_cut")
twoLCond.append("(mumu_Mll_cut ||  elel_Mll_cut)")
twoLCond.append("(muel_Mll_cut ||  elmu_Mll_cut)")
twoLCondName.append("mm")
twoLCondName.append("ee")
twoLCondName.append("ll")
twoLCondName.append("me")

twoLtwoJCond = []
twoLtwoJCondName = []
twoLtwoBCond = []
twoLtwoBCondName = []
twoLthreeBCond = []
twoLthreeBCondName = []
twoLtwoSubJCond = []
twoLtwoSubJCondName = []
twoLOneBFatJetTCond = []
twoLOneBFatJetTCondName = []
twoLTwoBSubJetsMMCond = []
twoLTwoBSubJetsMMCondName = []
twoLTwoBHighMassCond = []
twoLTwoBHighMassCondName = []

basicJcond="(elel_TwoJets_cut || mumu_TwoJets_cut || muel_TwoJets_cut || elmu_TwoJets_cut)"
basicTwoBcond="(Length$(za_diJets) > 0 && ((elel_TwoBjets_cut || mumu_TwoBjets_cut || muel_TwoBjets_cut || elmu_TwoBjets_cut) "
basicThreeBcond="(elel_ThreeBjets_cut || mumu_ThreeBjets_cut || muel_ThreeBjets_cut || elmu_ThreeBjets_cut)"
basicSubJcond="(elel_TwoSubJets_cut || mumu_TwoSubJets_cut || muel_TwoSubJets_cut || elmu_TwoSubJets_cut)"
basicOneBFatJetTcond="(elel_OneBFatJetT_cut || mumu_OneBFatJetT_cut || muel_OneBFatJetT_cut || elmu_OneBFatJetT_cut)"
basicTwoBSubJetsMMcond="(elel_TwoSubJets_cut || mumu_TwoSubJets_cut || muel_TwoSubJets_cut || elmu_TwoSubJets_cut)"
basictwoLTwoBHighMasscond="(Length$(za_diJets) > 0 && Length$(za_diLeptons) > 0 && za_diJets[0].p4.Pt() > 200 && za_diLeptons[0].p4.Pt() > 200)"
basicJcondName="jj"
basicTwoBcondName="bb"
basicThreeBcondName="bbb"
basicSubJcondName="fj"
basicOneBFatJetTcondName="bfj"
basicTwoBSubJetsMMcondName="sbjsbj"
basictwoLTwoBHighMasscondName="highmass"
for x in range(0,4):
	twoLtwoJCond.append("("+twoLCond[x]+" && "+basicJcond+")")
	twoLtwoBCond.append("("+twoLCond[x]+" && "+basicTwoBcond+")"+CSVV2_medium_SF_weight)
	twoLthreeBCond.append("("+twoLCond[x]+" && "+basicThreeBcond+")")
	twoLtwoSubJCond.append("("+twoLCond[x]+" && "+basicSubJcond+")")
	twoLOneBFatJetTCond.append("("+twoLCond[x]+" && "+basicOneBFatJetTcond+")")
	twoLTwoBSubJetsMMCond.append("("+twoLCond[x]+" && "+basicTwoBSubJetsMMcond+")")
	twoLTwoBHighMassCond.append("("+twoLCond[x]+" && "+basictwoLTwoBHighMasscond+")")
	twoLtwoJCondName.append(twoLCondName[x]+basicJcondName)
	twoLtwoBCondName.append(twoLCondName[x]+basicTwoBcondName)
        twoLthreeBCondName.append(twoLCondName[x]+basicThreeBcondName)
	twoLtwoSubJCondName.append(twoLCondName[x]+basicSubJcondName)
	twoLOneBFatJetTCondName.append(twoLCondName[x]+basicOneBFatJetTcondName)
        twoLTwoBSubJetsMMCondName.append(twoLCondName[x]+basicTwoBcondName+basicTwoBSubJetsMMcondName)
	twoLTwoBHighMassCondName.append(twoLCondName[x]+basicTwoBcondName+basictwoLTwoBHighMasscondName)
	print twoLtwoJCond[x]


#test_highMass_cond = "(Length$(za_diJets) > 0 && Length$(za_diLeptons) > 0 && za_diJets[0].p4.Pt() > 200 && za_diLeptons[0].p4.Pt() > 200)"
#test_highMass =  twoL_cond + " * " + twoB_cond + " * " + test_highMass_cond + weights
#test_highMassName = "highPt"


# Writing the JSON

## 2 Muons 2 Jets :

fjson = open('plots_all.py', 'w')
fjson.write( "plots = [\n")
fyml = open('plots_all.yml', 'w')


## CandCount variables :

options = options_()
'''
for cutkey in options.cut :
        print 'cutkey : ', cutkey
        ### get M_A and M_H ###
        #mH[0] = float(options.mH_list[cutkey])
        #mA[0] = float(options.mA_list[cutkey])
        printInPy(fjson, fyml, options.cut[cutkey], twoLepTwoBjets+" && "+cutkey,"(2, 0, 2)", 0)
'''
## Control Plots :


# 1) 2L stage

for x in range(0,4):
	print x
	printInJson(fjson, fyml, l1, l1Name, l_var, l_varName, twoLCond[x]+weights, twoLCondName[x], l_binning, 0)
	printInJson(fjson, fyml, l2, l2Name, l_var, l_varName, twoLCond[x]+weights, twoLCondName[x], l_binning, 0)
	printInJson(fjson, fyml, dilep, dilepName, dilep_var, dilep_varName, twoLCond[x]+weights, twoLCondName[x], dilep_binning, 0)
	printInJson(fjson, fyml, selJets, selJetsName, selJets_var, selJets_varName, twoLCond[x]+weights, twoLCondName[x], selJets_binning, 0)
	printInJson(fjson, fyml, selBjets, selBjetsName, selJets_var, selJets_varName, twoLCond[x]+weights, twoLCondName[x], selJets_binning, 0)
	printInJsonNoVar(fjson, fyml, nPV, nPVName, twoLCond[x]+weights, twoLCondName[x], nPV_binning, 0)
	# 2L2J
	printInJson(fjson, fyml, l1, l1Name, l_var, l_varName, twoLtwoJCond[x]+weights, twoLtwoJCondName[x], l_binning, 0)
	printInJson(fjson, fyml, l2, l2Name, l_var, l_varName, twoLtwoJCond[x]+weights, twoLtwoJCondName[x], l_binning, 0)
	printInJson(fjson, fyml, dilep, dilepName, dilep_var, dilep_varName, twoLtwoJCond[x]+weights, twoLtwoJCondName[x], dilep_binning, 0)
	printInJson(fjson, fyml, selJets, selJetsName, selJets_var, selJets_varName, twoLtwoJCond[x]+weights, twoLtwoJCondName[x], selJets_binning, 0)
	printInJson(fjson, fyml, selBjets, selBjetsName, selJets_var, selJets_varName, twoLtwoJCond[x]+weights, twoLtwoJCondName[x], selJets_binning, 0)
	printInJson(fjson, fyml, j1pt, j1ptName, j_var, j_varName, twoLtwoJCond[x]+weights, twoLtwoJCondName[x], j_binning, 0)
	printInJson(fjson, fyml, j2pt, j2ptName, j_var, j_varName, twoLtwoJCond[x]+weights, twoLtwoJCondName[x], j_binning, 0)
	# 2L2B
	printInJson(fjson, fyml, dilep, dilepName, dilep_var, dilep_varName, twoLtwoBCond[x]+weights, twoLtwoBCondName[x], dilep_binning, 0)
	printInJson(fjson, fyml, j1pt, j1ptName, j_var, j_varName, twoLtwoBCond[x]+weights, twoLtwoBCondName[x], j_binning, 0)
	printInJson(fjson, fyml, j2pt, j2ptName, j_var, j_varName, twoLtwoBCond[x]+weights, twoLtwoBCondName[x], j_binning, 0)
	printInJson(fjson, fyml, dijet, dijetName, dijet_var, dijet_varName, twoLtwoBCond[x]+weights, twoLtwoBCondName[x], dijet_binning, 0)
	printInJson(fjson, fyml, dijetdilep, dijetdilepName, dijetdilep_var, dijetdilep_varName, twoLtwoBCond[x]+weights, twoLtwoBCondName[x], dijetdilep_binning, 0)
	# 2L3B
        printInJson(fjson, fyml, dilep, dilepName, dilep_var, dilep_varName, twoLthreeBCond[x]+weights, twoLthreeBCondName[x], dilep_binning, 0)
        printInJson(fjson, fyml, j1pt, j1ptName, j_var, j_varName, twoLthreeBCond[x]+weights, twoLthreeBCondName[x], j_binning, 0)
        printInJson(fjson, fyml, j2pt, j2ptName, j_var, j_varName, twoLthreeBCond[x]+weights, twoLthreeBCondName[x], j_binning, 0)
        printInJson(fjson, fyml, dijet, dijetName, dijet_var, dijet_varName, twoLthreeBCond[x]+weights, twoLthreeBCondName[x], dijet_binning, 0)
        printInJson(fjson, fyml, dijetdilep, dijetdilepName, dijetdilep_var, dijetdilep_varName, twoLthreeBCond[x]+weights, twoLthreeBCondName[x], dijetdilep_binning, 0)
	# 2L2SJ
	printInJson(fjson, fyml, dilep, dilepName, dilep_var, dilep_varName, twoLtwoSubJCond[x]+weights , twoLtwoSubJCondName[x], dilep_binning, 0)
	printInJson(fjson, fyml, fj, fjName, j_var, j_varName, twoLtwoSubJCond[x]+weights , twoLtwoSubJCondName[x], j_binning, 0)
	printInJson(fjson, fyml, fj, fjName, fj_var, fj_varName, twoLtwoSubJCond[x]+weights , twoLtwoSubJCondName[x], fj_binning, 0)
	# 2L1BF
	printInJson(fjson, fyml, dilep, dilepName, dilep_var, dilep_varName, twoLOneBFatJetTCond[x]+weights , twoLOneBFatJetTCondName[x], dilep_binning, 0)
	printInJson(fjson, fyml, fj, fjName, j_var, j_varName, twoLOneBFatJetTCond[x]+weights , twoLOneBFatJetTCondName[x], j_binning, 0)
	printInJson(fjson, fyml, fj, fjName, fj_var, fj_varName, twoLOneBFatJetTCond[x]+weights , twoLOneBFatJetTCondName[x], fj_binning, 0)
	# 6) 2L2BSJ
	printInJson(fjson, fyml, dilep, dilepName, dilep_var, dilep_varName, twoLTwoBSubJetsMMCond[x]+weights , twoLTwoBSubJetsMMCondName[x], dilep_binning, 0)
	printInJson(fjson, fyml, fj, fjName, j_var, j_varName, twoLTwoBSubJetsMMCond[x]+weights , twoLTwoBSubJetsMMCondName[x], j_binning, 0)
	printInJson(fjson, fyml, fj, fjName, fj_var, fj_varName, twoLTwoBSubJetsMMCond[x]+weights , twoLTwoBSubJetsMMCondName[x], fj_binning, 0)
	## test high mass
	printInJson(fjson, fyml, dijetdilep, dijetdilepName, dijetdilep_var, dijetdilep_varName, twoLTwoBHighMassCond[x]+weights,twoLTwoBHighMassCondName[x], dijetdilep_binning, 0)
	printInJson(fjson, fyml, dilep, dilepName, dilep_var, dilep_varName, twoLTwoBHighMassCond[x]+weights,twoLTwoBHighMassCondName[x], dilep_binning, 0)
	printInJson(fjson, fyml, dijet, dijetName, dijet_var, dijet_varName, twoLTwoBHighMassCond[x]+weights,twoLTwoBHighMassCondName[x], dijet_binning, 0)
	printInJson(fjson, fyml, met, metName, met_var, met_varName, twoLTwoBHighMassCond[x]+weights,twoLTwoBHighMassCondName[x], met_binning, 1 if x==3 else 0)


'''


printInJson(fjson, fyml, j1pt, j1ptName, j_var, j_varName, twoMuTwojets, twoMuTwojetsName, j_binning, 0)
printInJson(fjson, fyml, j2pt, j2ptName, j_var, j_varName, twoMuTwojets, twoMuTwojetsName, j_binning, 0)
printInJson(fjson, fyml, j1csv, j1csvName, j_var, j_varName, twoMuTwojets, twoMuTwojetsName, j_binning, 0)
printInJson(fjson, fyml, j2csv, j2csvName, j_var, j_varName, twoMuTwojets, twoMuTwojetsName, j_binning, 0)
printInJson(fjson, fyml, dilep, dilepName, dilep_var, dilep_varName, twoMuTwojets, twoMuTwojetsName, dilep_binning, 0)
printInJson(fjson, fyml, dijet, dijetName, dijet_var, dijet_varName, twoMuTwojets, twoMuTwojetsName, dijet_binning, 0)
printInJson(fjson, fyml, dijetdilep, dijetdilepName, dijetdilep_var, dijetdilep_varName, twoMuTwojets, twoMuTwojetsName, dijetdilep_binning, 0)

## 2 Electrons 2 Jets :

printInJson(fjson, fyml, l1, l1Name, l_var, l_varName, twoElTwojets, twoElTwojetsName, l_binning, 0)
printInJson(fjson, fyml, l2, l2Name, l_var, l_varName, twoElTwojets, twoElTwojetsName, l_binning, 0)
printInJson(fjson, fyml, j1pt, j1ptName, j_var, j_varName, twoElTwojets, twoElTwojetsName, j_binning, 0)
printInJson(fjson, fyml, j2pt, j2ptName, j_var, j_varName, twoElTwojets, twoElTwojetsName, j_binning, 0)
printInJson(fjson, fyml, j1csv, j1csvName, j_var, j_varName, twoElTwojets, twoElTwojetsName, j_binning, 0)
printInJson(fjson, fyml, j2csv, j2csvName, j_var, j_varName, twoElTwojets, twoElTwojetsName, j_binning, 0)
printInJson(fjson, fyml, dilep, dilepName, dilep_var, dilep_varName, twoElTwojets, twoElTwojetsName, dilep_binning, 0)
printInJson(fjson, fyml, dijet, dijetName, dijet_var, dijet_varName, twoElTwojets, twoElTwojetsName, dijet_binning, 0)
printInJson(fjson, fyml, dijetdilep, dijetdilepName, dijetdilep_var, dijetdilep_varName, twoElTwojets, twoElTwojetsName, dijetdilep_binning, 0)

## 2 leptons, 2 BJets :

printInJson(fjson, fyml, l1, l1Name, l_var, l_varName, twoLepTwoBjets, twoLepTwoBjetsName, l_binning, 0)
printInJson(fjson, fyml, l2, l2Name, l_var, l_varName, twoLepTwoBjets, twoLepTwoBjetsName, l_binning, 0)
printInJson(fjson, fyml, j1pt, j1ptName, j_var, j_varName, twoLepTwoBjets, twoLepTwoBjetsName, j_binning, 0)
printInJson(fjson, fyml, j2pt, j2ptName, j_var, j_varName, twoLepTwoBjets, twoLepTwoBjetsName, j_binning, 0)
printInJson(fjson, fyml, j1csv, j1csvName, j_var, j_varName, twoLepTwoBjets, twoLepTwoBjetsName, j_binning, 0)
printInJson(fjson, fyml, j2csv, j2csvName, j_var, j_varName, twoLepTwoBjets, twoLepTwoBjetsName, j_binning, 0)
printInJson(fjson, fyml, dilep, dilepName, dilep_var, dilep_varName, twoLepTwoBjets, twoLepTwoBjetsName, dilep_binning, 0)
printInJson(fjson, fyml, dijet, dijetName, dijet_var, dijet_varName, twoLepTwoBjets, twoLepTwoBjetsName, dijet_binning, 0)
printInJson(fjson, fyml, dijetdilep, dijetdilepName, dijetdilep_var, dijetdilep_varName, twoLepTwoBjets, twoLepTwoBjetsName, dijetdilep_binning, 0)
printInJson(fjson, fyml, met, metName, met_var, met_varName, twoLepTwoBjets, twoLepTwoBjetsName, met_binning, 0)

## test high mass
printInJson(fjson, fyml, dijetdilep, dijetdilepName, dijetdilep_var, dijetdilep_varName, test_highMass, test_highMassName, dijetdilep_binning, 0)
printInJson(fjson, fyml, dilep, dilepName, dilep_var, dilep_varName, test_highMass, test_highMassName, dilep_binning, 0)
printInJson(fjson, fyml, dijet, dijetName, dijet_var, dijet_varName, test_highMass, test_highMassName, dijet_binning, 0)
printInJson(fjson, fyml, met, metName, met_var, met_varName, test_highMass, test_highMassName, met_binning, 1)

'''

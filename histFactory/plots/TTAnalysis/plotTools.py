import copy

from TTAnalysis import TT
from ScaleFactors import *

#### Utility to join different cuts together (logical AND) ####

def joinCuts(*cuts):
    if len(cuts) == 0: 
        return ""
    elif len(cuts) == 1: 
        return cuts[0]
    else:
        totalCut = "("
        for cut in cuts:
            cut = cut.strip().strip("&")
            if cut == "":
                continue
            totalCut += "(" + cut + ")&&" 
        totalCut = totalCut.strip("&") + ")"
        return totalCut

#### The IDs/... we want to run on ####

electronID = { TT.LepID.L: "L" }
#electronID = { TT.LepID.L: "L", TT.LepID.M: "M" }
#electronID = { TT.LepID.L: "L", TT.LepID.M: "M", TT.LepID.T: "T" }
muonID = { TT.LepID.L: "L" }

electronIso = { TT.LepIso.L: "L" }
muonIso = { TT.LepIso.L: "L" }

#myBWPs = { wp.first: wp.second for wp in TT.BWP.map }
#myBWPs = { TT.BWP.L: "L", TT.BWP.M: "M" } 
myBWPs = { TT.BWP.L: "L" } 

myFlavours = [ "ElEl", "MuEl", "ElMu", "MuMu" ]
#myFlavours = [ "ElEl" ]
#myFlavours = [ "MuMu" ]
#myFlavours = [ "ElMu", "MuEl" ]

keepOnlySymmetricWP = False

#### UTILITY TO GENERATE ALL THE NEEDED CATEGORIES ####

def generateCategoryStrings(categoryStringsDico, flavourChannel):
    if flavourChannel not in [ "MuMu", "ElMu", "MuEl", "ElEl" ]:
        raise Exception("Wrong flavour passed to string generator: %r." % flavourChannel)

    lep1IDs = []
    lep2IDs = []
    lep1Isos = []
    lep2Isos = []
    catTitle = flavourChannel
    catCut = flavourChannel.lower()
    doZVeto = False

    if flavourChannel == "ElEl":
        lep1IDs = electronID.keys()
        lep2IDs = electronID.keys()
        lep1Isos = electronIso.keys()
        lep2Isos = electronIso.keys()
        doZVeto = True
    
    if flavourChannel == "ElMu":
        lep1IDs = electronID.keys()
        lep2IDs = muonID.keys()
        lep1Isos = electronIso.keys()
        lep2Isos = muonIso.keys()
    
    if flavourChannel == "MuEl":
        lep1IDs = muonID.keys()
        lep2IDs = electronID.keys()
        lep1Isos = muonIso.keys()
        lep2Isos = electronIso.keys()
    
    if flavourChannel == "MuMu":
        lep1IDs = muonID.keys()
        lep2IDs = muonID.keys()
        lep1Isos = muonIso.keys()
        lep2Isos = muonIso.keys()
        doZVeto = True
    

    for id1 in lep1IDs:
        for id2 in lep2IDs:
            for iso1 in lep1Isos:
                for iso2 in lep2Isos:

                    if keepOnlySymmetricWP and id1 != id2:
                        continue

                    if keepOnlySymmetricWP and iso1 != iso2:
                        continue

                    llSFs = [get_leptons_SF_for_dilepton(0, id1, id2, iso1, iso2)]

                    # ll categs: iterate over two leptons ID & isolation

                    lepLepIDIsoStr = TT.LepLepIDIsoStr(id1, iso1, id2, iso2)

                    elIDIso = ""
                    muIDIso = ""
                    if flavourChannel == "ElEl" or flavourChannel == "ElMu":
                        elIDIso = TT.LepIDIso(id1, iso1)
                        muIDIso = TT.LepIDIso(id2, iso2)
                    if flavourChannel == "MuMu" or flavourChannel == "MuEl":
                        muIDIso = TT.LepIDIso(id1, iso1)
                        elIDIso = TT.LepIDIso(id2, iso2)
                    
                    llStringsBase = {
                            "#CAT_TITLE#": catTitle + "_" + lepLepIDIsoStr, 
                            "#LEPLEP_IDISO#": TT.LepLepIDIso(id1, iso1, id2, iso2),
                            "#LEPLEP_CAT_CUTS#": joinCuts(
                                catCut + "_Category_" + lepLepIDIsoStr + "_cut", 
                                catCut + "_Mll_" + lepLepIDIsoStr + "_cut", 
                                catCut + "_DiLeptonTriggerMatch_" + lepLepIDIsoStr + "_cut", 
                                catCut + "_DiLeptonIsOS_" + lepLepIDIsoStr + "_cut"
                                ),
                            "#MIN_LEP_IDISO#": TT.LepIDIso(min(id1, id2), min(iso1, iso2)),
                            "#EL_IDISO#": elIDIso,
                            "#MU_IDISO#": muIDIso,
                            "#JET_CAT_CUTS#": "1",
                            "#LEP1_SF#": get_lepton_SF_for_dilepton(0, 0, id1, id2, iso1, iso2),
                            "#LEP2_SF#": get_lepton_SF_for_dilepton(1, 0, id1, id2, iso1, iso2)
                        }
                    llStrings = [ copy.deepcopy(llStringsBase) ]
                    
                    if doZVeto:
                        m_llStrings = copy.deepcopy(llStringsBase)
                        m_llStrings["#CAT_TITLE#"] = catTitle + "_ZVeto_" + lepLepIDIsoStr
                        m_llStrings["#LEPLEP_CAT_CUTS#"] = joinCuts(
                                    catCut + "_Category_" + lepLepIDIsoStr + "_cut", 
                                    catCut + "_Mll_" + lepLepIDIsoStr + "_cut", 
                                    catCut + "_DiLeptonTriggerMatch_" + lepLepIDIsoStr + "_cut", 
                                    catCut + "_DiLeptonIsOS_" + lepLepIDIsoStr + "_cut", 
                                    catCut + "_MllZVeto_" + lepLepIDIsoStr + "_cut"
                                    )
                        llStrings.append(m_llStrings)

                    if "llCategs" in categoryStringsDico.keys():
                        categoryStringsDico["llCategs"]["strings"] += llStrings
                        categoryStringsDico["llCategs"]["weights"] += [llSFs]

                        if doZVeto:
                            categoryStringsDico["llCategs"]["weights"] += [llSFs]
    
                    # lljj categs: two jets; minDRjl > cut using loosest of the two IDs & isolations

                    if "lljjCategs" in categoryStringsDico.keys():
                    
                        lljjStrings = copy.deepcopy(llStrings)
                        weights = []
                        for categ in lljjStrings:
                            categ["#CAT_TITLE#"] += "_jj"
                            categ["#JET_CAT_CUTS#"] = "Length$(tt_diLepDiJets_DRCut[" + str(TT.LepLepIDIso(id1, iso1, id2, iso2)) + "]) >= 1"
                            weights += [llSFs]
                        categoryStringsDico["lljjCategs"]["strings"] += lljjStrings
                        categoryStringsDico["lljjCategs"]["weights"] += weights
    
                    # lljj_b_categs: two jets, but iterate over one b-jet working point

                    if "lljj_b_Categs" in categoryStringsDico.keys():
                    
                        for wp in myBWPs.items():
                            lljj_b_Strings = copy.deepcopy(llStrings)
                            weights = [] 

                            for categ in lljj_b_Strings:
                                categ["#CAT_TITLE#"] += "_jj_b_" + wp[1]
                                categ["#BWP#"] = wp[1]
                                categ["#MIN_LEP_IDISO_BWP#"] = TT.LepIDIsoJetBWP(min(id1, id2), min(iso1, iso2), wp[0])
                                categ["#JET_CAT_CUTS#"] = "Length$(tt_diLepDiJets_DRCut[" + str(TT.LepLepIDIso(id1, iso1, id2, iso2)) + "]) >= 1"
                                weights += [llSFs]
                            
                            categoryStringsDico["lljj_b_Categs"]["strings"] += lljj_b_Strings
                            categoryStringsDico["lljj_b_Categs"]["weights"] += weights

                    # llbj_categs: two jets, one b-jet, iterate over one b-jet working point

                    if "llbjCategs" in categoryStringsDico.keys():
                    
                        for wp in myBWPs.items():
                            llbjStrings = copy.deepcopy(llStrings)
                            # FIXME
                            #llbSFs = [get_leptons_SF_for_dilepton(0, id1, id2, iso1, iso2), get_at_least_one_b_SF(0, wp, id1, id2, iso1, iso2)]
                            llbSFs = [get_leptons_SF_for_dilepton(0, id1, id2, iso1, iso2)]
                            weights = []
                            
                            for categ in llbjStrings:
                                categ["#CAT_TITLE#"] += "_bj_" + wp[1]
                                categ["#BWP#"] = wp[1]
                                categ["#MIN_LEP_IDISO_BWP#"] = TT.LepIDIsoJetBWP(min(id1, id2), min(iso1, iso2), wp[0])
                                categ["#JET_CAT_CUTS#"] = joinCuts(
                                        "Length$(tt_diLepDiJets_DRCut[" + str(TT.LepLepIDIso(id1, iso1, id2, iso2)) + "]) >= 1"
                                        "Length$(tt_selBJets_DRCut_BWP_CSVv2Ordered[" + str(TT.LepIDIsoJetBWP(min(id1, id2), min(iso1, iso2), wp[0])) + "]) >= 1"
                                        )
                                weights += [llbSFs]
                            
                            categoryStringsDico["llbjCategs"]["strings"] += llbjStrings
                            categoryStringsDico["llbjCategs"]["weights"] += weights

                    # llbb categs: two b-jets, iterate over both b-jet working points
    
                    if "llbbCategs" in categoryStringsDico.keys():
                    
                        for wp1 in myBWPs.keys():
                            for wp2 in myBWPs.keys():
                                llbbSFs = [get_leptons_SF_for_dilepton(0, id1, id2, iso1, iso2), get_at_least_two_b_SF_for_dijet(0, wp1, wp2, id1, id2, iso1, iso2)]

                                llbbStrings = copy.deepcopy(llStrings)
                                weights = []
                                
                                for categ in llbbStrings:
                                    categ["#CAT_TITLE#"] += "_bb_" + TT.JetJetBWPStr(wp1, wp2)
                                    categ["#LEPLEP_IDISO_BBWP#"] = TT.LepLepIDIsoJetJetBWP(id1, iso1, id2, iso2, wp1, wp2)
                                    categ["#JET_CAT_CUTS#"] = "Length$(tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[" + str(TT.LepLepIDIsoJetJetBWP(id1, iso1, id2, iso2, wp1, wp2)) + "]) >= 1"
                                    categ["#BJET1_SF#"] = get_at_least_two_b_SF_one_b_for_dijet(0, 0, wp1, wp2, id1, id2, iso1, iso2)
                                    categ["#BJET2_SF#"] = get_at_least_two_b_SF_one_b_for_dijet(1, 0, wp1, wp2, id1, id2, iso1, iso2)
                                    weights += [llbbSFs]
                                
                                categoryStringsDico["llbbCategs"]["strings"] += llbbStrings
                                categoryStringsDico["llbbCategs"]["weights"] += weights


    # Duplicate everything and ask for MET if we are same-flavour
    if flavourChannel in ["ElEl", "MuMu"]:
        for categName, categGroup in categoryStringsDico.items():
            metStrings = []
            weights = []
            for index, categ in enumerate(categGroup["strings"]):
                thisCateg = copy.deepcopy(categ)
                thisCateg["#CAT_TITLE#"] += "_Met"
                thisCateg["#JET_CAT_CUTS#"] = joinCuts(thisCateg["#JET_CAT_CUTS#"], "met_p4.Pt() > 40")
                metStrings.append(thisCateg)
                weights.append(categGroup["weights"][index])
            categGroup["strings"] += metStrings
            categGroup["weights"] += weights

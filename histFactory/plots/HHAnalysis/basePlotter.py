import copy
from HHAnalysis import HH
from ScaleFactors import *


class BasePlotter:
    def __init__(self):
        # This list shows what are the free parameters to generate the plots
        self.baseObjectName = "hh_llmetjj"# will eventually be used with index(s) from the map
        self.map = "hh_map_llmetjj_id_iso_btagWP_pair"
        self.lepMap = "hh_map_l_id_iso"
        self.jetMap = "hh_map_j_btagWP"
        # The following working points HAVE to be defined by the user in generatePlots.py (must be e.g. HH.lepID.L)
        self.lepid1 = "" 
        self.lepiso1 = ""
        self.lepid2 = ""
        self.lepiso2 = ""
        self.jetid1 = ""
        self.jetid2 = ""
        self.btagWP1 = ""
        self.btagWP2 = ""
        self.pair = ""
        # The following will be instantiated in generatePlots function below
        self.llFlav = ""
        self.catCut = ""  
        self.jetCut = ""
        self.lepCut = ""     
        self.extraCut = ""
        self.totalCut = ""

    def generatePlots(self, categories = ["ElEl", "MuMu", "MuEl"]):

        self.mapWP = HH.leplepIDIsojetjetIDbtagWPPair(self.lepid1, self.lepiso1, self.lepid2, self.lepiso2, self.jetid1, self.jetid2, self.btagWP1, self.btagWP2, self.pair)
        self.lepMapWP = HH.lepIDIso(self.lepid1, self.lepiso1)
        self.jetMapWP = self.btagWP1 # To Be Updated once jet map includes jetID
        self.llIsoCat = HH.lepIso.map.at(self.lepiso1)+HH.lepIso.map.at(self.lepiso2) # This is to extract string from WP
        self.llIDCat = HH.lepID.map.at(self.lepid1)+HH.lepID.map.at(self.lepid2)
        self.jjIDCat = HH.jetID.map.at(self.jetid1)+HH.jetID.map.at(self.jetid2)
        self.jjBtagCat = HH.btagWP.map.at(self.btagWP1)+HH.btagWP.map.at(self.btagWP2)
        self.suffix = "_"+HH.jetPair.map.at(self.pair)+"Ordered"
         
        self.mapIndices = "%s[%s]"%(self.map, self.mapWP)
        self.lepMapIndices = "%s[%s]"%(self.lepMap, self.lepMapWP)
        self.jetMapIndices = "%s[%s]"%(self.jetMap, self.jetMapWP)
        self.baseObject = "%s[%s[0]]"%(self.baseObjectName, self.mapIndices)     # NB : make plots only for one llmetjj candidate (can be made configurable)
        self.mapCut = "Length$(%s)>0"%self.mapIndices # ensure to have an entry in the map
        self.lep1_str = "hh_leptons[%s.ilep1]"%self.baseObject
        self.lep2_str = "hh_leptons[%s.ilep2]"%self.baseObject
        self.jet1_str = "hh_jets[%s.ijet1]"%self.baseObject
        self.jet2_str = "hh_jets[%s.ijet2]"%self.baseObject
        self.ll_str = "hh_ll[%s.ill]"%self.baseObject 
        self.jj_str = "hh_jj[%s.ijj]"%self.baseObject

        self.lep1_fwkIdx = self.lep1_str+".idx"
        self.lep2_fwkIdx = self.lep2_str+".idx"
        self.jet1_fwkIdx = self.jet1_str+".idx"
        self.jet2_fwkIdx = self.jet2_str+".idx"

        self.lepCut = "%s.hlt_DR_matchedObject < 0.3 && %s.hlt_DR_matchedObject < 0.3 && (%s.charge != %s.charge)"%(self.lep1_str, self.lep2_str, self.lep1_str, self.lep2_str)
        self.jetCut = ""#"%s.p4.Pt() > 30 && %s.p4.Pt() > 30"%(self.jet1_str, self.jet2_str) 

        self.plots_el = []
        self.plots_mu = []
        self.plots_lep = []
        self.plots_jet = []
        self.plots_met = []
        self.plots_ll = []
        self.plots_jj = []
        self.plots_llmetjj = []
        self.plots_gen = []
        self.plots_evt = []


        zMass = 91.1876 
        dict_cat_cut =  {
                            "ElEl" : "%s.isElEl && %s.p4.M() > 12 && (91.1876 - %s.p4.M()) > 15"%(self.ll_str, self.ll_str, self.ll_str),
                            "MuMu" : "%s.isMuMu && %s.p4.M() > 12 && (91.1876 - %s.p4.M()) > 15"%(self.ll_str, self.ll_str, self.ll_str),
                            "MuEl" : "((%s.isElMu)||(%s.isMuEl)) && %s.p4.M() > 12 && (91.1876 - %s.p4.M()) > 15"%(self.ll_str, self.ll_str, self.ll_str, self.ll_str)
                        }

        for cat in categories :

            self.catCut = dict_cat_cut[cat]
            self.totalCut = self.joinCuts(self.mapCut, self.catCut, self.jetCut, self.lepCut, self.extraCut)
            self.llFlav = cat

            self.plots_lep.extend([
                {
                    'name':  'lep1_pt_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                    'variable': self.lep1_str+".p4.Pt()",
                    'plot_cut': self.totalCut,
                    'binning': '(50, 0, 300)'
                },
                {
                    'name':  'lep1_eta_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                    'variable': self.lep1_str+".p4.Eta()",
                    'plot_cut': self.totalCut,
                    'binning': '(25, -2.5, 2.5)'
                },
                {
                    'name':  'lep1_phi_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                    'variable': self.lep1_str+".p4.Phi()",
                    'plot_cut': self.totalCut,
                    'binning': '(25, -3.1416, 3.1416)'
                },
                {
                    'name':  'lep2_pt_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                    'variable': self.lep2_str+".p4.Pt()",
                    'plot_cut': self.totalCut,
                    'binning': '(50, 0, 150)'
                },
                {
                    'name':  'lep2_eta_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                    'variable': self.lep2_str+".p4.Eta()",
                    'plot_cut': self.totalCut,
                    'binning': '(25, -2.5, 2.5)'
                },
                {
                    'name':  'lep2_phi_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                    'variable': self.lep2_str+".p4.Phi()",
                    'plot_cut': self.totalCut,
                    'binning': '(25, -3.1416, 3.1416)'
                }
            ])
            if cat == "ElEl" :
                self.plots_el.extend([
                    {
                        'name':  'el1_RelIso03WithEA_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "electron_relativeIsoR03_withEA[%s]"%self.lep1_fwkIdx,
                        'plot_cut': self.totalCut,
                        'binning': '(100, 0, 0.4)'
                    },
                    {
                        'name':  'el1_RelIso03WithDeltaBeta_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "electron_relativeIsoR03_deltaBeta[%s]"%self.lep1_fwkIdx,
                        'plot_cut': self.totalCut,
                        'binning': '(100, 0, 0.4)'
                    },
                    {
                        'name':  'el2_RelIso03WithEA_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "electron_relativeIsoR03_withEA[%s]"%self.lep2_fwkIdx,
                        'plot_cut': self.totalCut,
                        'binning': '(100, 0, 0.4)'
                    },
                    {
                        'name':  'el2_RelIso03WithDeltaBeta_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "electron_relativeIsoR03_deltaBeta[%s]"%self.lep2_fwkIdx,
                        'plot_cut': self.totalCut,
                        'binning': '(100, 0, 0.4)'
                    }
                ])
            if cat == "MuMu" :
                self.plots_mu.extend([
                    {
                        'name':  'mu1_RelIso04WithEA_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "muon_relativeIsoR04_withEA[%s]"%self.lep1_fwkIdx,
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 0.4)'
                    },
                    {
                        'name':  'mu1_RelIso04WithDeltaBeta_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "muon_relativeIsoR04_deltaBeta[%s]"%self.lep1_fwkIdx,
                        'plot_cut': self.totalCut,
                        'binning': '(100, 0, 0.4)'
                    },
                    {
                        'name':  'mu2_RelIso04WithEA_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "muon_relativeIsoR04_withEA[%s]"%self.lep2_fwkIdx,
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 0.4)'
                    },
                    {
                        'name':  'mu2_RelIso04WithDeltaBeta_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "muon_relativeIsoR04_deltaBeta[%s]"%self.lep2_fwkIdx,
                        'plot_cut': self.totalCut,
                        'binning': '(100, 0, 0.4)'
                    },
                    {
                        'name':  'mumu_scaleFactor_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': '({0} * {1} * {2} * {3})'.format(get_muon_id_sf(self.lepid1, self.lep1_fwkIdx), get_muon_iso_sf(self.lepiso1, self.lepid1, self.lep1_fwkIdx), get_muon_id_sf(self.lepid2, self.lep2_fwkIdx), get_muon_iso_sf(self.lepiso2, self.lepid2, self.lep2_fwkIdx)),
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 2)'
                    },
                    {
                        'name':  'mu1_scaleFactor_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': '({0} * {1})'.format(get_muon_id_sf(self.lepid1, self.lep1_fwkIdx), get_muon_iso_sf(self.lepiso1, self.lepid1, self.lep1_fwkIdx)),
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 2)'
                    },
                    {
                        'name':  'mu2_scaleFactor_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': '({0} * {1})'.format(get_muon_id_sf(self.lepid2, self.lep2_fwkIdx), get_muon_iso_sf(self.lepiso2, self.lepid2, self.lep2_fwkIdx)),
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 2)'
                    }
                ])
            
            self.plots_jet.extend([ 
                {
                        'name':  'jet1_pt_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.jet1_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 300)'
                },
                {
                        'name':  'jet1_eta_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.jet1_str+".p4.Eta()",
                        'plot_cut': self.totalCut,
                        'binning': '(25, -2.5, 2.5)'
                },
                {
                        'name':  'jet1_phi_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.jet1_str+".p4.Phi()",
                        'plot_cut': self.totalCut,
                        'binning': '(25, -3.1416, 3.1416)'
                },
                {
                        'name':  'jet1_JP_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.jet1_str+".JP",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.5)'
                },
                {
                        'name':  'jet1_CSV_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.jet1_str+".CSV",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 1)'
                },
                {
                        'name':  'jet2_pt_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.jet2_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 300)'
                },
                {
                        'name':  'jet2_eta_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.jet2_str+".p4.Eta()",
                        'plot_cut': self.totalCut,
                        'binning': '(25, -2.5, 2.5)'
                },
                {
                        'name':  'jet2_phi_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.jet2_str+".p4.Phi()",
                        'plot_cut': self.totalCut,
                        'binning': '(25, -3.1416, 3.1416)'
                },
                {
                        'name':  'jet2_JP_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.jet2_str+".JP",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.5)'
                },
                {
                        'name':  'jet2_CSV_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.jet2_str+".CSV",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 1)'
                },
                {
                        'name':  'jet1_scaleFactor_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': get_csvv2_sf(self.btagWP1, self.jet1_fwkIdx),
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 2)'
                },
                {
                        'name':  'jet2_scaleFactor_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': get_csvv2_sf(self.btagWP2, self.jet2_fwkIdx),
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 2)'
                }
            ])

            self.plots_met.extend([ 
                {
                        'name':  'met_pt_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "met_p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 400)'
                },
                {
                        'name':  'met_phi_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "met_p4.Phi()",
                        'plot_cut': self.totalCut,
                        'binning': '(25, -3.1416, 3.1416)'
                }
            ])

            self.plots_ll.extend([ 
                {
                        'name':  'll_M_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.ll_str+".p4.M()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 250)'
                },
                {
                        'name':  'll_pt_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.ll_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 400)'
                },
                {
                        'name':  'll_DR_l_l_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.ll_str+".DR_l_l",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name':  'll_DPhi_l_l_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "abs("+self.ll_str+".DPhi_l_l)",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                }
            ])

            self.plots_jj.extend([ 
                {
                        'name':  'jj_M_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.jj_str+".p4.M()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 600)'
                },
                {
                        'name':  'jj_pt_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.jj_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 400)'
                },
                {
                        'name':  'jj_DR_j_j_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.jj_str+".DR_j_j",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name':  'jj_DPhi_j_j_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "abs("+self.jj_str+".DPhi_j_j)",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                },
                {
                        'name':  'jj_scaleFactor_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "{0} * {1}".format(get_csvv2_sf(self.btagWP1, self.jet1_fwkIdx), get_csvv2_sf(self.btagWP2, self.jet2_fwkIdx)),
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 2)'
                }, 
            ])

            self.plots_llmetjj.extend([ 
                {
                        'name':  'llmetjj_n_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "Length$(%s)"%self.mapIndices,
                        'plot_cut': self.totalCut,
                        'binning': '(18, 0, 18)'
                },
                {
                        'name':  'llmetjj_pt_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 250)'
                },
                {
                        'name':  'llmetjj_M_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".p4.M()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 1000)'
                },
                {
                        'name':  'llmetjj_DPhi_ll_met_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "abs("+self.baseObject+".DPhi_ll_met)",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 3.1416)'
                },
                {
                        'name':  'llmetjj_minDPhi_l_met_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".minDPhi_l_met",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                },
                {
                        'name':  'llmetjj_maxDPhi_l_met_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".maxDPhi_l_met",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                },
                {
                        'name':  'llmetjj_MT_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".MT", # ll[ill].p4 + met[imet].p4).M()
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 600)'
                },
                {
                        'name':  'llmetjj_MTformula_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".MT_formula", # std::sqrt(2 * ll[ill].p4.Pt() * met[imet].p4.Pt() * (1-std::cos(dphi)));
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 500)'
                },
                {
                        'name':  'llmetjj_projMET_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "abs("+self.baseObject+".projectedMet)",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 400)'
                },
                {
                        'name':  'llmetjj_DPhi_jj_met_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "abs("+self.baseObject+".DPhi_jj_met)",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 3.1416)'
                },
                {
                        'name':  'llmetjj_minDPhi_j_met_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".minDPhi_j_met",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                },
                {
                        'name':  'llmetjj_maxDPhi_j_met_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".maxDPhi_j_met",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                },
                {
                        'name':  'llmetjj_maxDR_l_j_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".maxDR_l_j",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name':  'llmetjj_minDR_l_j_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".minDR_l_j",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name':  'llmetjj_DR_ll_jj_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".DR_ll_jj",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name':  'llmetjj_DR_llmet_jj_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".DR_llmet_jj",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name':  'llmetjj_DPhi_ll_jj_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "abs("+self.baseObject+".DPhi_ll_jj)",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 3.1416)'
                },
                {
                        'name':  'llmetjj_DPhi_llmet_jj_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "abs("+self.baseObject+".DPhi_llmet_jj)",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 3.1416)'
                },
                {
                        'name':  'llmetjj_cosThetaStar_CS_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "abs("+self.baseObject+".cosThetaStar_CS)",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 1)'
                },
                {
                        'name':  'lljj_pt_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".lljj_p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 500)'
                },
                {
                        'name':  'lljj_M_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".lljj_p4.M()",
                        'plot_cut': self.totalCut,
                        'binning': '(75, 0, 1000)'
                }
            ])
            for elt in self.plots_jj : 
                tempPlot = copy.deepcopy(elt)
                if "p4" in tempPlot["variable"] :
                    tempPlot["variable"] = tempPlot["variable"].replace(self.jj_str,"hh_gen_BB")
                    tempPlot["name"] = "gen"+tempPlot["name"]
                    self.plots_gen.append(tempPlot)
            self.plots_evt.extend([
                {
                    'name':  'nLep_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                    'variable': "Length$(%s)"%self.lepMapIndices,
                    'plot_cut': self.totalCut,
                    'binning': '(4, 2, 6)'
                },
                {
                    'name':  'nLepAll_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.jjIDCat, self.jjBtagCat, self.suffix),
                    'variable': "hh_nLeptons",
                    'plot_cut': self.totalCut,
                    'binning': '(5, 2, 7)'
                },
                {
                    'name':  'nElAll_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.jjIDCat, self.jjBtagCat, self.suffix),
                    'variable': "hh_nElectrons",
                    'plot_cut': self.totalCut,
                    'binning': '(6, 0, 6)'
                },
                {
                    'name':  'nMuAll_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.jjIDCat, self.jjBtagCat, self.suffix),
                    'variable': "hh_nMuons",
                    'plot_cut': self.totalCut,
                    'binning': '(6, 0, 6)'
                },
                {
                    'name':  'nJet_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                    'variable': "Length$(%s)"%self.jetMapIndices,
                    'plot_cut': self.totalCut,
                    'binning': '(5, 2, 7)'
                },
                {
                    'name':  'nJetAll_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.jjIDCat, self.jjBtagCat, self.suffix),
                    'variable': "hh_nJets",
                    'plot_cut': self.totalCut,
                    'binning': '(10, 2, 12)'
                },
                {
                    'name':  'nBJetLooseCSV_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.jjIDCat, self.jjBtagCat, self.suffix),
                    'variable': "hh_nBJetsL",
                    'plot_cut': self.totalCut,
                    'binning': '(6, 0, 6)'
                }
            ])


    def joinCuts(self, *cuts):
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



class BasePlotter:
    def __init__(self):
        # This list shows what are the free parameters to generate the plots
        self.baseObjectName = "hh_llmetjj"# will eventually be used with index(s) from the map
        self.map = "hh_map_llmetjj_id_iso_btagWP_pair"
        self.mapWP = "0"
        self.lepMap = "hh_map_l_id_iso"
        self.lepMapWP = "0"
        self.jetMap = "hh_map_j_btagWP"
        self.jetMapWP = "0"
        self.llIsoCat = "LL"
        self.llIDCat = "LL"
        self.jjIDCat = "TT"
        self.jjBtagCat = "nono"
        self.order = "htOrdered"
        self.suffix = ""
        self.llFlav = "ElEl"
        self.catCut = ""  
        self.jetCut = ""
        self.lepCut = ""     
        self.extraCut = ""
        self.totalCut = ""

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

    def generatePlots(self, categories = ["ElEl", "MuMu", "MuEl"]):
         
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

        self.lepCut = "%s.hlt_DR_matchedObject < 0.3 && %s.hlt_DR_matchedObject < 0.3"%(self.lep1_str, self.lep2_str)

        self.jetCut = "%s.id_L && %s.id_L && %s.p4.Pt() > 30 && %s.p4.Pt() > 30"%(self.jet1_str, self.jet2_str, self.jet1_str, self.jet2_str)  # So far, jet ID is not in the map
        self.jjIDCat = "LL"

        self.plots_lep = []
        self.plots_el = []
        self.plots_mu = []
        self.plots_jet = []
        self.plots_met = []
        self.plots_ll = []
        self.plots_jj = []
        self.plots_llmetjj = []
        self.plots_evt = []


        zMass = 91.1876 
        dict_cat_cut =  {
                            "ElEl" : "%s.isElEl && %s.p4.M() > 12 && (91.1876 - %s.p4.M()) > 15"%(self.ll_str, self.ll_str, self.ll_str),
                            "MuMu" : "%s.isMuMu && %s.p4.M() > 12 && (91.1876 - %s.p4.M()) > 15"%(self.ll_str, self.ll_str, self.ll_str),
                            "MuEl" : "((%s.isElMu)||(%s.isMuEl))"%(self.ll_str, self.ll_str)
                        }

        for cat in categories :

            self.catCut = dict_cat_cut[cat]
            self.totalCut = self.joinCuts(self.mapCut, self.catCut, self.jetCut, self.lepCut, self.extraCut) + "*event_weight"
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
                    'binning': '(50, 0, 300)'
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
                        'variable': "electron_relativeIsoR03_withEA[%s.idx]"%self.lep1_str,
                        'plot_cut': self.totalCut,
                        'binning': '(100, 0, 0.4)'
                    },
                    {
                        'name':  'el1_RelIso03WithDeltaBeta_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "electron_relativeIsoR03_deltaBeta[%s.idx]"%self.lep1_str,
                        'plot_cut': self.totalCut,
                        'binning': '(100, 0, 0.4)'
                    },
                    {
                        'name':  'el2_RelIso03WithEA_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "electron_relativeIsoR03_withEA[%s.idx]"%self.lep2_str,
                        'plot_cut': self.totalCut,
                        'binning': '(100, 0, 0.4)'
                    },
                    {
                        'name':  'el2_RelIso03WithDeltaBeta_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "electron_relativeIsoR03_deltaBeta[%s.idx]"%self.lep2_str,
                        'plot_cut': self.totalCut,
                        'binning': '(100, 0, 0.4)'
                    }
                ])
            if cat == "MuMu" :
                self.plots_mu.extend([
                    {
                        'name':  'mu1_RelIso04WithEA_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "muon_relativeIsoR04_withEA[%s.idx]"%self.lep1_str,
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 0.4)'
                    },
                    {
                        'name':  'mu1_RelIso04WithDeltaBeta_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "muon_relativeIsoR04_deltaBeta[%s.idx]"%self.lep1_str,
                        'plot_cut': self.totalCut,
                        'binning': '(100, 0, 0.4)'
                    },
                    {
                        'name':  'mu2_RelIso04WithEA_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "muon_relativeIsoR04_withEA[%s.idx]"%self.lep2_str,
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 0.4)'
                    },
                    {
                        'name':  'mu2_RelIso04WithDeltaBeta_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "muon_relativeIsoR04_deltaBeta[%s.idx]"%self.lep2_str,
                        'plot_cut': self.totalCut,
                        'binning': '(100, 0, 0.4)'
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
                        'name':  'jet1_csv_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
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
                        'name':  'jet2_csv_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.jet2_str+".CSV",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 1)'
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
                        'name':  'Mll_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.ll_str+".p4.M()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 250)'
                },
                {
                        'name':  'PTll_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.ll_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 400)'
                },
                {
                        'name':  'DRll_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.ll_str+".DR_l_l",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name':  'DPhill_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "abs("+self.ll_str+".DPhi_l_l)",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                }
            ])

            self.plots_jj.extend([ 
                {
                        'name':  'Mjj_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.jj_str+".p4.M()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 1000)'
                },
                {
                        'name':  'PTjj_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.jj_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 400)'
                },
                {
                        'name':  'DRjj_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.jj_str+".DR_j_j",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name':  'DPhijj_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "abs("+self.jj_str+".DPhi_j_j)",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                }
            ])

            self.plots_llmetjj.extend([ 
                {
                        'name':  'nllmetjj_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "Length$(%s)"%self.mapIndices,
                        'plot_cut': self.totalCut,
                        'binning': '(18, 0, 18)'
                },
                {
                        'name':  'PTllmetjj_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 250)'
                },
                {
                        'name':  'Mllmetjj_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".p4.M()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 1000)'
                },
                {
                        'name':  'DPhi_ll_met_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "abs("+self.baseObject+".DPhi_ll_met)",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 3.1416)'
                },
                {
                        'name':  'MinDPhi_l_met_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".minDPhi_l_met",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                },
                {
                        'name':  'MaxDPhi_l_met_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".maxDPhi_l_met",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                },
                {
                        'name':  'MT_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".MT", # ll[ill].p4 + met[imet].p4).M()
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 600)'
                },
                {
                        'name':  'MTformula_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".MT_formula", # std::sqrt(2 * ll[ill].p4.Pt() * met[imet].p4.Pt() * (1-std::cos(dphi)));
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 500)'
                },
                {
                        'name':  'projMET_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "abs("+self.baseObject+".projectedMet)",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 400)'
                },
                {
                        'name':  'DPhi_jj_met_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "abs("+self.baseObject+".DPhi_jj_met)",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 3.1416)'
                },
                {
                        'name':  'MinDPhi_j_met_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".minDPhi_j_met",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                },
                {
                        'name':  'MaxDPhi_j_met_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".maxDPhi_j_met",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                },
                {
                        'name':  'MaxDR_l_j_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".maxDR_l_j",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name':  'MinDR_l_j_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".minDR_l_j",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name':  'DR_ll_jj_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".DR_ll_jj",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name':  'DR_llmet_jj_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.baseObject+".DR_llmet_jj",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name':  'DPhi_ll_jj_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "abs("+self.baseObject+".DPhi_ll_jj)",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 3.1416)'
                },
                {
                        'name':  'DPhi_llmet_jj_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': "abs("+self.baseObject+".DPhi_llmet_jj)",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 3.1416)'
                }
            ])
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
                    'name':  'nBJetMediumCSV_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.jjIDCat, self.jjBtagCat, self.suffix),
                    'variable': "hh_nBJets",
                    'plot_cut': self.totalCut,
                    'binning': '(6, 0, 6)'
                }
            ])



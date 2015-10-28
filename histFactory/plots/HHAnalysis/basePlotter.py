
class BasePlotter:
    def __init__(self):
        # This list shows what are the free parameters to generate the plots
        self.baseObjectName = "hh_llmetjj"# will eventually be used with index(s) from the map
        self.map = "hh_map_llmetjj_id_iso_btagWP_pair"
        self.mapWP = "0"
        self.llIsoCat = "LL"
        self.llIDCat = "LL"
        self.jjIDCat = "TT"
        self.jjBtagCat = "nono"
        self.suffix = "_leadingHt"
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
        self.baseObject = "%s[%s][0]"%(self.baseObjectName, self.mapIndices)     # NB : make plots only for one llmetjj candidate (can be made configurable)
        self.mapCut = "Length$(%s)>0"%self.mapIndices # ensure to have an entry in the map
        self.lep1_str = "hh_leptons[%s.ilep1]"%self.baseObject
        self.lep2_str = "hh_leptons[%s.ilep2]"%self.baseObject
        self.jet1_str = "hh_jets[%s.ijet1]"%self.baseObject
        self.jet2_str = "hh_jets[%s.ijet2]"%self.baseObject
        self.ll_str = "hh_ll[%s.ill]"%self.baseObject 

        self.jetCut = "%s.id_L && %s.id_L"%(self.jet1_str, self.jet2_str)  # So far, jet ID is not in the map
        self.jjIDCat = "LL"

        dict_cat_cut =  {
                            "ElEl" : "elel_category && elel_ll_mass_cut && %s.isElEl"%(self.ll_str),
                            "MuMu" : "mumu_category && mumu_ll_mass_cut && %s.isMuMu"%(self.ll_str),
                            "MuEl" : "((elmu_category && %s.isElMu  && elmu_ll_mass_cut)||(muel_category && %s.isMuEl && muel_ll_mass_cut))"%(self.ll_str, self.ll_str)
                        }
        self.plots_lep = []
        self.plots_jet = []
        for cat in categories :
            self.catCut = dict_cat_cut[cat]
            self.totalCut = self.joinCuts(self.mapCut, self.catCut, self.jetCut, self.lepCut, self.extraCut) + "*event_weight"
            self.llFlav = cat
            self.plots_lep.extend([
                {
                    'name':  'lep1_pt_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                    'variable': self.lep1_str+".p4.Pt()",
                    'plot_cut': self.totalCut,
                    'binning': '(50, 0,300)'
                }
            ])
            
            self.plots_jet.extend([ 
                    {
                        'name':  'jet1_pt_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.llIsoCat, self.llIDCat, self.jjIDCat, self.jjBtagCat, self.suffix),
                        'variable': self.jet1_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0,300)'
                    }
                ])



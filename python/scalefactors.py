"""
Helpers for configuring scale factors, fake rates etc.

The basic configuration parameter is the json file path for a set of factors.
There two basic types are
- lepton scale factors (dependent on a number of object variables, e.g. PT and ETA), 
- jet (b-tagging) scale factors (grouped set for different flavours, for convenience)

Different values (depending on the data-taking period)
can be taken into account by weighting or by randomly sampling.
"""
"""
Common definitions of scale factors
"""
__all__ = ("get_scalefactors",)

import os.path
from itertools import chain, ifilter

from . import pathCP3llbb
def localize_llbbFwk(aPath, cp3llbbBase=pathCP3llbb):
    return os.path.join(cp3llbbBase, "Framework", "data", "ScaleFactors", aPath)


lumiPerPeriod_2016 = {
      "B" : 5785.152 ## averaged 5783.740 (DoubleMuon), 5787.976 (DoubleEG) and 5783.740 (MuonEG) - max dev. from average is 5.e-4 << lumi syst
    , "C" : 2573.399
    , "D" : 4248.384
    , "E" : 4009.132
    , "F" : 3101.618
    , "G" : 7540.488
    , "H" : 8605.689
    ##
    , "Run271036to275783" : 6274.191
    , "Run275784to276500" : 3426.131
    , "Run276501to276811" : 3191.207
    }

hwwMuonPeriods_2016 = [ "Run271036to275783", "Run275784to276500", "Run276501to276811" ]
hwwElePeriods_2016 = [] ## TODO

all_scalefactors = {
      "electron_2015_76"  : dict((k,localize_llbbFwk(v)) for k, v in chain(
          dict(("id_{wp}".format(wp=wp.lower()), ("Electron_CutBasedID_{wp}WP_fromTemplates_withSyst_76X.json".format(wp=wp)))
         for wp in ("Veto", "Loose", "Medium", "Tight")).iteritems()
        , { "hww_wp" : "Electrons_HWW_CutBasedID_TightWP_76X_forHWW_Final.json" }.iteritems()
        ))
    , "muon_2015_76" : dict((k, localize_llbbFwk(v)) for k, v in chain(
          dict(("id_{wp}".format(wp=wp.lower()), "Muon_{wp}ID_genTracks_id.json".format(wp=wp)) for wp in ("Soft", "Loose", "Medium")).iteritems()
        , { "id_tight" : "Muon_TightIDandIPCut_genTracks_id.json" }.iteritems()
        , dict(("iso_{isowp}_id_{idwp}".format(isowp=isowp.lower(), idwp=idwp.lower()), "Muon_{isowp}RelIso_{idwp}ID_iso.json".format(isowp=isowp, idwp=idwp))
            for (idwp,isowp) in (("Loose", "Loose"), ("Loose", "Medium"), ("Loose", "Tight"), ("Tight", "Medium"), ("Tight", "Tight")) ).iteritems()
        , { "id_hww"   : "Muon_MediumID_Data_MC_25ns_PTvsETA_HWW_76.json"
          , "iso_tight_id_hww" : "Muon_ISOTight_Data_MC_25ns_PTvsETA_HWW.json" }.iteritems()
        ))
    , "btag_2015_76" : dict() ## TODO
    ## 2016 CMSSW_8_0_...
    , "muon_2016_80" : dict((k,( localize_llbbFwk(v) if isinstance(v, str)
                               else [ (eras, localize_llbbFwk(path)) for eras,path in v ]))
                           for k, v in chain(
        ## https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffsRun2#Tracking_efficiency_provided_by
          { "tracking" : "Muon_tracking_BCDEFGH.json" }.iteritems()
        ## https://twiki.cern.ch/twiki/bin/viewauth/CMS/MuonWorkInProgressAndPagResults
        , dict(("id_{wp}".format(wp=wp.lower()), [ (eras, "Muon_{wp}ID_genTracks_id_{era}.json".format(wp=wp, era=eras)) for eras in ("BCDEF", "GH") ]) for wp in ("Loose", "Medium", "Tight")).iteritems()
        , { "id_medium2016" : [ (eras, "Muon_MediumID2016_genTracks_id_{era}.json".format(era=eras)) for eras in ("BCDEF", "GH") ] }.iteritems()
        , dict(("iso_{isowp}_id_{idwp}".format(isowp=isowp.lower(), idwp=idwp.lower())
               , [ (eras, "Muon_{isowp}ISO_{idwp}ID_iso_{era}.json".format(isowp=isowp, idwp=idwp, era=eras)) for eras in ("BCDEF", "GH") ])
            for (isowp, idwp) in [("Loose", "Loose"), ("Loose", "Medium"), ("Loose", "Tight"), ("Tight", "Medium"), ("Tight", "Tight")]).iteritems()
        ## https://twiki.cern.ch/twiki/bin/view/CMS/HWW2016TriggerAndIdIsoScaleFactorsResults
        , { "iso_tight_hww" : [ ((era,), "Muon_data_mc_ISOTight_Run2016_{era}_PTvsETA_HWW.json".format(era=era)) for era in hwwMuonPeriods_2016 ] }.iteritems()
        , { "id_tight_hww"  : [ ((era,), "Muon_data_mc_TightID_Run2016_{era}_PTvsETA_HWW.json".format(era=era)) for era in hwwMuonPeriods_2016 ] }.iteritems()
        ))
    ## https://twiki.cern.ch/twiki/bin/view/CMS/EgammaIDRecipesRun2#Efficiencies_and_scale_factors
    , "electron_2016_ichep2016" : dict((k,( localize_llbbFwk(v) if isinstance(v, str)
                               else [ (eras, localize_llbbFwk(path)) for eras,path in v ]))
                           for k, v in chain(
          { "gsf_tracking"  : "Electron_EGamma_SF2D_gsfTracking.json" }.iteritems()
        , dict(("id_{wp}".format(wp=wp), "Electron_EGamma_SF2D_{wp}.json".format(wp=wp)) for wp in ("veto", "loose", "medium", "tight")).iteritems()
        , { "hww_wp"        : [ ((era,), "Electron_Tight_Run2016_{era}_HWW.json".format(era=era)) for era in hwwElePeriods_2016 ] }.iteritems()
        ))
    , "electron_2016_moriond2017" : dict((k,( localize_llbbFwk(v) if isinstance(v, str)
                               else [ (eras, localize_llbbFwk(path)) for eras,path in v ]))
                           for k, v in chain(
          { "gsf_tracking"  : "Electron_EGamma_SF2D_reco_moriond17.json" }.iteritems()
        , dict(("id_{wp}".format(wp=wp), "Electron_EGamma_SF2D_{wp}_moriond17.json".format(wp=wp)) for wp in ("veto", "loose", "medium", "tight")).iteritems()
        ))
    , "eleltrig_2016_HHMoriond17" : tuple(os.path.join(pathCP3llbb, "ZAAnalysis", "data", "Efficiencies", "{0}.json".format(nm)) for nm in ("Electron_IsoEle23Leg", "Electron_IsoEle12Leg", "Electron_IsoEle23Leg", "Electron_IsoEle12Leg"))
    , "elmutrig_2016_HHMoriond17" : tuple(os.path.join(pathCP3llbb, "ZAAnalysis", "data", "Efficiencies", "{0}.json".format(nm)) for nm in ("Electron_IsoEle23Leg", "Electron_IsoEle12Leg", "Muon_XPathIsoMu23leg", "Muon_XPathIsoMu8leg"))
    , "mueltrig_2016_HHMoriond17" : tuple(os.path.join(pathCP3llbb, "ZAAnalysis", "data", "Efficiencies", "{0}.json".format(nm)) for nm in ("Muon_XPathIsoMu23leg", "Muon_XPathIsoMu8leg", "Electron_IsoEle23Leg", "Electron_IsoEle12Leg"))
    , "mumutrig_2016_HHMoriond17" : tuple(os.path.join(pathCP3llbb, "ZAAnalysis", "data", "Efficiencies", "{0}.json".format(nm)) for nm in ("Muon_DoubleIsoMu17Mu8_IsoMu17leg", "Muon_DoubleIsoMu17TkMu8_IsoMu8legORTkMu8leg", "Muon_DoubleIsoMu17Mu8_IsoMu17leg", "Muon_DoubleIsoMu17TkMu8_IsoMu8legORTkMu8leg"))
    ## https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation80XReReco
    , "btag_2016_moriond2017" : dict((k,( tuple(localize_llbbFwk(fv) for fv in v) if isinstance(v,tuple) and all(isinstance(fv, str) for fv in v)
                               else [ (eras, tuple(localize_llbbFwk(fpath) for fpath in paths)) for eras,paths in v ]))
                           for k, v in 
          dict(("cMVAv2_{wp}".format(wp=wp), tuple("BTagging_{wp}_{flav}_{calib}_cmvav2_BtoH_moriond17.json".format(wp=wp, flav=flav, calib=calib) for (flav, calib) in (("lightjets", "incl"), ("cjets", "ttbar"), ("bjets", "ttbar")))) for wp in ("loose", "medium", "tight")).iteritems()
        )
    }

from .treedecorators import op
binningVariablesByName = {
      "Eta"       : lambda obj : obj.p4.Eta()
    , "ClusEta"   : lambda obj : obj.clusterEta
    , "AbsEta"    : lambda obj : op.abs(obj.p4.Eta())
    , "AbsClusEta": lambda obj : op.abs(obj.clusterEta)
    , "Pt"        : lambda obj : obj.p4.Pt()
    } ## TODO add more?

from collections import OrderedDict as odict
def getBinningVarNames(jsonpath):
    import json
    with open(jsonpath, "r") as jsf:
        cont = json.load(jsf)
    return tuple(cont["variables"])

class BinningParameters(object):
    def __init__(self, binningVars):
        self.binningVars = binningVars
    def __call__(self, obj):
        return op.construct("Parameters",
                       (op.initList("std::initializer_list<Parameters::value_type::value_type>", "Parameters::value_type::value_type", (
                           op.initList("Parameters::value_type::value_type", "float", (op.extVar("int", "BinningVariable::{0}".format(bvNm.replace("Clus", ""))), bv(obj)))
                           for bvNm,bv in self.binningVars.iteritems())),)
                   )

def getBinningParameters(bVarNames, isElectron=False, moreVars=dict()):
    if isElectron:
        bVarNames = [ k.replace("Eta", "ClusEta") for k in bVarNames ]
    theDict = dict(binningVariablesByName)
    theDict.update(moreVars)
    return BinningParameters(odict((k,theDict[k]) for k in bVarNames))

import ROOT
ROOT.gROOT.ProcessLine(".I {0}".format(os.path.join(pathCP3llbb, "Framework", "interface")))
ROOT.gROOT.ProcessLine("#define STANDALONE_SCALEFACTORS")
ROOT.gROOT.ProcessLine('#include "BinnedValues.h"')

class ScaleFactor(object):
    def __init__(self, name, initLines=None, args=None):
        self._name = name
        self._initLines = initLines if initLines is not None else []
        self._args      = args      if args      is not None else []
    @property
    def cpp_initCode(self):
        return tuple(self._initLines)
    def __call__(self, obj, variation="Nominal", withMCCheck=True, precalc=True, check=None):
        from .treedecorators import makeConst, boolType
        expr = op.extMethod("{0}.get".format(self._name))(*tuple(chain(
                   list(a(obj) for a in self._args)
                 , (op.extVar("int", variation),)
               )))
        if check:
            expr = op.switch(check, expr, makeConst(1., "Float_t"))
        if withMCCheck:
            expr = op.switch(op.extVar(boolType, "runOnMC"), expr, makeConst(1., "Float_t"))
        if precalc:
            import uuid ## caching
            expr._parent.uname = "sf_{0}".format(str(uuid.uuid4()).replace("-", "_"))
        return expr

def lepton_scalefactor(elSF, muSF, obj):
    pass

def get_scalefactors(name, objType, key, periods=None, combine=None, additionalVariables=dict()):
    ## get the right config
    if isinstance(key, tuple):
        # interpret key=("a", "b") as ...["a"]["b"]
        mainKey = key[0]
        config = all_scalefactors[key[0]]
        for idx in xrange(1,len(key)):
            config = config[key[idx]]
    else:
        mainKey = key
        config = all_scalefactors[key]

    if periods is None:
        if "2016" in mainKey:
            periods = "BCDEFGH"
        else:
            periods = []
    periods = set(periods)

    combPrefix = ""
    objStr = ""
    initLines = tuple()
    sfArgs = []

    if combine is not None:
        combPrefix = { "weight" : "W"
                     , "sample" : "Smp" }.get(combine, "W")

    def doubleQuote(aStr):
        return '"{0}"'.format(aStr)
    def initList(elms):
        return "{{ {0} }}".format(", ".join(elms))
    def mapInitList(items):
        return initList(initList((k,v)) for k,v in items)

    if objType == "lepton":
        if isinstance(config, str):
            initLines = ("{obj}ScaleFactor {nm}{{{pth}}};".format(nm=name, obj=objStr, pth=doubleQuote(config)),)
            sfArgs = [ getBinningParameters(getBinningVarNames(config), isElectron=(key[0].split("_")[0] == "electron"), moreVars=additionalVariables) ]
        else:
            if combPrefix == "":
                raise ValueError("A combination mode needs to be specified for this scale factor")
            selConfigs = list(ifilter(lambda (w,v) : w != 0.,
                ((sum(lumiPerPeriod_2016[ier] for ier in eras if ier in periods),path)
                    for eras,path in config if any(ier in periods for ier in eras))))
            if len(selConfigs) > 1:
                initLines = tuple(["std::vector<std::unique_ptr<ILeptonScaleFactor>> __tmp_{nm};".format(nm=name)]
                                 +[ "__tmp_{nm}.emplace_back(std::unique_ptr<ILeptonScaleFactor>{{new {obj}ScaleFactor{{{0}}}}});".format(doubleQuote(path), obj=objStr, nm=name) for wgt,path in selConfigs ]
                                 +["{cmb}{obj}ScaleFactor {nm}{{{{ {0} }}, std::move(__tmp_{nm}) }};".format(", ".join("{0:e}".format(wgt) for wgt,path in selConfigs), nm=name, obj=objStr, cmb=combPrefix)]
                                 )
            else:
                initLines = ("{obj}ScaleFactor {nm}{{{pth}}};".format(nm=name, obj=objStr, pth=doubleQuote(selConfigs[0][1])),)
            bVarNames = set(chain.from_iterable(getBinningVarNames(iPth) for iWgt,iPth in selConfigs))
            sfArgs = [ getBinningParameters(bVarNames, isElectron=(key[0].split("_")[0] == "electron"), moreVars=additionalVariables) ]

    elif objType == "dilepton":
        objStr = "DiLeptonFromLegs"
        if isinstance(config, tuple) and len(config) == 4:
            if not all(isinstance(iCfg, str) for iCfg in config):
                raise TypeError("Config for dilepton scale factor should be quadruplet of paths or list f weights and triplets, found {0}".format(config))
            else:
                initLines = ("{obj}ScaleFactor {nm}{{{args}}};".format(nm=name, obj=objStr, args=", ".join("std::unique_ptr<ILeptonScaleFactor>(new ScaleFactor({0}))".format(doubleQuote(leplegCfg)) for leplegCfg in config)),)
            sfArgs = [ (lambda bp : (lambda ll : bp(ll.l1)))(getBinningParameters(set(chain(getBinningVarNames(config[0]), getBinningVarNames(config[1]))), moreVars=additionalVariables))
                     , (lambda bp : (lambda ll : bp(ll.l2)))(getBinningParameters(set(chain(getBinningVarNames(config[2]), getBinningVarNames(config[3]))), moreVars=additionalVariables))
                     ]
        else:
            raise NotImplementedError("Still to do this part")

    elif objType == "jet":
        objStr = "BTagging"
        if isinstance(config, tuple) and len(config) == 3:
            if not all(isinstance(iCfg, str) for iCfg in config):
                raise TypeError("Config for b-tagging should be triplet of paths or list of weights and triplets, found {0}".format(config))
            else:
                initLines = ("{obj}ScaleFactor {nm}{{{0}}};".format(", ".join(doubleQuote(iCfg) for iCfg in config), obj=objStr, nm=name),)

                bVarNames = set(chain.from_iterable(getBinningVarNames(iCfg) for iCfg in config))
                sfArgs = [ getBinningParameters(bVarNames, moreVars=additionalVariables) ]
        else:
            if not ( all((isinstance(iCfg, tuple) and len(iCfg) == 3 and all(isinstance(iPth, str) for iPth in iCfg) ) for iCfg in config) ):
                raise TypeError("Config for b-tagging should be triplet of paths or list of weights and triplets, found {0}".format(config))
            else:
                if combPrefix == "":
                    raise ValueError("A combination mode needs to be specified for this scale factor")
                selConfigs = list(ifilter(lambda (w,v) : w != 0.,
                    ((sum(lumiPerPeriod_2016[ier] for ier in eras if ier in periods),paths)
                        for eras,paths in config if any(ier in periods for ier in eras))))
                if len(selConfigs) > 1:
                    initLines = tuple(["std::vector<std::unique_ptr<IJetScaleFactor>> __tmp_{nm};".format(obj=objStr, nm=name)]
                                     +[ "__tmp_{nm}.emplace_back(std::unique_ptr<IJetScaleFactor>{{new {obj}ScaleFactor{{{0}}}}});".format(", ".join(doubleQuote(iPth) for iPth in paths), obj=objStr, nm=name) for wgt,paths in selConfigs ]
                                     +["{cmb}{obj}ScaleFactor {nm}{{ {{ {0} }}, std::move(__tmp_{nm}) }};".format(", ".join("{0:e}".format(wgt) for wgt,paths in selConfigs), nm=name, obj=objStr, cmb=combPrefix)]
                                     )
                else:
                    initLines = ("{obj}ScaleFactor {nm}{{{0}}};".format(", ".join(doubleQuote(iCfg) for iCfg in config[0][1]), obj=objStr, nm=name),)

                bVarNames = set(chain.from_iterable(getBinningVarNames(iPth) for iWgt,paths in selConfigs for iPth in paths))
                sfArgs = [ getBinningParameters(bVarNames, moreVars=additionalVariables) ]
        sfArgs.append(lambda j : op.extMethod("IJetScaleFactor::get_flavour")(j.hadronFlavor))
    else:
        raise ValueError("Unknown object type: {0}".format(objType))

    ### cpp_initCode
        return ("{typ} {name}{{{0}}};".format(
                  ", ".join(self._initArgs)
                , typ=self._cppType, name=self._name
                ),) ## combPrefix objStr
    ###

    return ScaleFactor(name, initLines, args=sfArgs)


if __name__ == "__main__":
    #aSF = get_scalefactors("test_mu", "lepton", ("muon_2015_76", "iso_loose_id_loose"))
    lSF = get_scalefactors("test", "lepton", ("muon_2016_80", "iso_loose_id_loose"), combine="weight")
    jSF = get_scalefactors("testb", "jet", ("btag_2016_moriond2017", "cMVAv2_loose"), combine="weight")
    llSF = get_scalefactors("testTrig", "dilepton", "eleltrig_2016_HHMoriond17")

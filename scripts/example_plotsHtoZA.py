#!/usr/bin/env python2
"""
Example: H->ZA tree decoration, interactive exploration based on that, and a plotter
"""
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True # let python do option parsing
## logging
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
"""
za decoration

This part would go into a zadeco.py module and used as 'from cp3_llbb.ZATools.zadeco import decoratedZATree
"""
from cp3_llbb.CommonTools.lldeco import LeptonRef
from cp3_llbb.CommonTools.treedecorators import levelsAbove, addIntoHierarchy, TreeStub, BranchGroupStub, SmartTupleStub, SmartObjectStub, LeafFacade

import ROOT
## Load the library
ROOT.gSystem.Load("libcp3_llbbZAAnalysis.so")

hZAObjectStubMap = SmartObjectStub.Map({
      "HtoZA::Lepton" : [
          LeptonRef("L")
        , SmartTupleStub._RefToOther("hlt", lambda l : l.record.hlt.object[l.hlt_idx])
        ]
    , "HtoZA::Dilepton" : [
          SmartTupleStub._RefToOther("l1", lambda ll : ll.hZA.leptons[ll.ilep1])
        , SmartTupleStub._RefToOther("l2", lambda ll : ll.hZA.leptons[ll.ilep2])
        , SmartTupleStub._RefToOther("hlt1", lambda ll : ll.record.hlt.object[ll.hlt_idxs.first])
        , SmartTupleStub._RefToOther("hlt2", lambda ll : ll.record.hlt.object[ll.hlt_idxs.second])
        ]
    , "HtoZA::Met" : []
    , "HtoZA::Jet" : [
        ## Framework jet ref
          SmartTupleStub._RefToOther("J", lambda j : (
                getattr(j.record, "jets_{}".format(j.systVar._prefix.strip("_")))[j.idx]
                  if hasattr(j, "systVar") else j.record.jets[j.idx]
                ) )
        ]
    , "HtoZA::Dijet" : [
        ## HtoZA::Jet refs
          SmartTupleStub._RefToOther("j1", lambda jj : (jj.systVar.jets[jj.ijet1] if hasattr(jj, "systVar") else jj.hZA.jets[jj.ijet1]))
        , SmartTupleStub._RefToOther("j2", lambda jj : (jj.systVar.jets[jj.ijet2] if hasattr(jj, "systVar") else jj.hZA.jets[jj.ijet2]))
        ## Framework jet refs
        , SmartTupleStub._RefToOther("J1", lambda jj : jj.j1.J)
        , SmartTupleStub._RefToOther("J2", lambda jj : jj.j2.J)
        ]
    , "HtoZA::MELAAngles" : []
    })
hZAObjectStubMap["HtoZA::DileptonDijet"] = hZAObjectStubMap.get("HtoZA::Dilepton")+hZAObjectStubMap.get("HtoZA::Dijet")

def decoratedZATree(someTree):
    tree = TreeStub(someTree)
    recHierarchy = levelsAbove([], "record")
    #
    evt = BranchGroupStub("event_")
    addIntoHierarchy("event", evt, tree, recHierarchy)
    evtHierarchy = levelsAbove(recHierarchy, "event")
    # > event
    addIntoHierarchy("pdf", BranchGroupStub("pdf_"), evt, evtHierarchy)
    # < event
    hlt = BranchGroupStub("hlt_")
    addIntoHierarchy("hlt", hlt, tree, recHierarchy)
    # > hlt
    hltHierarchy = levelsAbove(recHierarchy, "hlt")
    addIntoHierarchy("object", BranchGroupStub("object_"), hlt, hltHierarchy,
        capabilities=[ SmartTupleStub._SmartIterable(lambda objs : objs.record.hlt.object_p4.size()) ] )
    # < hlt
    ## objects
    addIntoHierarchy("muons", BranchGroupStub("muon_"), tree, recHierarchy,
        capabilities=[ SmartTupleStub._SmartIterable(lambda muons : muons.record.muon_charge.size()) ] )
    addIntoHierarchy("electrons", BranchGroupStub("electron_"), tree, recHierarchy,
        capabilities=[ SmartTupleStub._SmartIterable(lambda electrons : electrons.record.electron_charge.size()) ] )
    addIntoHierarchy("jets", BranchGroupStub("jet_"), tree, recHierarchy,
        capabilities=[ SmartTupleStub._SmartIterable(lambda jets : jets.record.jet_gen_charge.size()) ] )
    for systVar in ("jecdown", "jecup", "jerdown", "jerup"):
        cNm = "jets_{}".format(systVar)
        addIntoHierarchy("jets_{}".format(systVar), BranchGroupStub("jet_{}_".format(systVar)), tree, recHierarchy,
                capabilities=[ SmartTupleStub._SmartIterable(( lambda sv : ( lambda jets : getattr(jets.record, "jet_{}_gen_p4".format(sv)).size() ) )(systVar)) ])
    met = BranchGroupStub("met_")
    addIntoHierarchy("met", met, tree, recHierarchy)
    cand = BranchGroupStub("hZA_")
    addIntoHierarchy("hZA", cand, tree, recHierarchy)
    hZAHierarchy = levelsAbove(recHierarchy, "hZA")
    # > hZA
    gen = BranchGroupStub("gen_")
    addIntoHierarchy("gen", gen, cand, hZAHierarchy)
    #
    for systVar in (None, "jecdown", "jecup", "jerdown", "jerup"):
        if systVar:
            cand_sv = BranchGroupStub("{}_".format(systVar))
            addIntoHierarchy(systVar, cand_sv, cand, hZAHierarchy)
            svHierarchy = levelsAbove(hZAHierarchy, "systVar") ## used by jet refs
            svJetColl = getattr(tree, "jets_{}".format(systVar))
        else:
            cand_sv = cand
            svHierarchy = hZAHierarchy
            svJetColl = tree.jets

        addIntoHierarchy("leptons", LeafFacade("leptons", cand_sv), cand_sv, svHierarchy,
                capabilities=[SmartTupleStub._WrappedIterable(cand_sv.leptons, hZAObjectStubMap)])
        addIntoHierarchy("ll", LeafFacade("ll", cand_sv), cand_sv, svHierarchy,
                capabilities=[SmartTupleStub._WrappedIterable(cand_sv.ll, hZAObjectStubMap)])

        addIntoHierarchy("jets", LeafFacade("jets", cand_sv), cand_sv, svHierarchy,
                capabilities=[SmartTupleStub._WrappedIterable(cand_sv.jets, hZAObjectStubMap)])
        addIntoHierarchy("jj", LeafFacade("jj", cand_sv), cand_sv, svHierarchy,
                capabilities=[SmartTupleStub._WrappedIterable(cand_sv.jj, hZAObjectStubMap)])

        addIntoHierarchy("lljj_cmva", LeafFacade("lljj_cmva", cand_sv), cand_sv, svHierarchy,
                capabilities=[SmartTupleStub._WrappedIterable(cand_sv.lljj_cmva, hZAObjectStubMap)])
        addIntoHierarchy("lljj_deepCSV", LeafFacade("lljj_deepCSV", cand_sv), cand_sv, svHierarchy,
                capabilities=[SmartTupleStub._WrappedIterable(cand_sv.lljj_deepCSV, hZAObjectStubMap)])

    return tree

"""
Interactive
"""
def doInteractive():
    from cp3_llbb.CommonTools.treedecorators import adaptArg, op

    tChain = ROOT.TChain("t")
    tChain.Add("/storage/data/cms/store/user/asaggio/DYToLL_2J_13TeV-amcatnloFXFX-pythia8/DYToLL_2J_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_Summer16MiniAODv2/180219_144051/0000/output_mc_271.root")
    tChain.GetEntries() ## force load
    tup = decoratedZATree(tChain)

    def toDraw(sth):
        return adaptArg(sth).get_TTreeDrawStr()
    def leafDeps(expr):
        return list(expr._parent.leafDeps)

    import IPython; IPython.embed()

"""
Plotter demo: generate plots
"""
from cp3_llbb.CommonTools.plots import Plot, EquidistantBinning, Selection

jetVars = {
          "PT"          : (lambda j : j.p4.Pt() , EquidistantBinning(50, 0., 350.), "transverse momentum", "p_{T} (GeV/c)")
        , "ETA"         : (lambda j : j.p4.Eta(), EquidistantBinning(50, -2.5, 2.5), "pseudorapidity"     , "#eta")
        ## flavour taggers
        , "CSVv2"       : (lambda j : j.pfCombinedInclusiveSecondaryVertexV2BJetTags, EquidistantBinning(50, 0., 1.), "CSVv2 classifier output", "CSVv2")
        , "cMVAv2"      : (lambda j : j.pfCombinedMVAV2BJetTags, EquidistantBinning(50, -1., 1.), "cMVAv2 classifier output", "cMVAv2")
        , "deepCSV"     : (lambda j : j.pfDeepCSVJetTags_probb+j.pfDeepCSVJetTags_probbb, EquidistantBinning(50, 0., 1.), "DeepCSV classifier output: probb+probbb", "probb+probbb")
        }

lepVars = {
          "PT"          : (lambda l : l.p4.Pt() , EquidistantBinning(50, 0., 300.), "transverse momentum", "p_{T} (GeV/c)")
        , "ETA"         : (lambda l : l.p4.Eta(), EquidistantBinning(50, -2.5, 2.5), "pseudorapidity"     , "#eta")
        }

lepVars_split = {
          "IsoEA"       : (lambda l : l.relativeIsoR03_withEA, -1., EquidistantBinning(50, 0., 1.), "PFRelIsoR03 with EA", "RelIsoR03_withEA")
        }

## Get scale factors
scale_factors = set()
from cp3_llbb.CommonTools.scalefactors import get_scalefactors
from cp3_llbb.CommonTools.lldeco import LeptonScaleFactor, DiLeptonScaleFactor
sf_ele_trk = get_scalefactors("sf_ele_2016_trk" , "lepton", ("electron_2016_moriond2017", "gsf_tracking"), combine="weight")
sf_ele_IDL = get_scalefactors("sf_ele_2016_IDLtrk" , "lepton", ("electron_2016_moriond2017", "id_loose"), combine="weight")
sf_mu_trk = get_scalefactors("sf_muon_2016_trk", "lepton", ("muon_2016_80", "tracking"), combine="weight")
sf_mu_IDL = get_scalefactors("sf_muon_2016_IDLtrk", "lepton", ("muon_2016_80", "id_loose"), combine="weight")
lepton_sf_IDL = LeptonScaleFactor((sf_ele_trk, sf_ele_IDL), (sf_mu_trk, sf_mu_IDL))
sf_elel_trig = get_scalefactors("sf_elel_2016_trig", "dilepton", "eleltrig_2016_HHMoriond17")
sf_elmu_trig = get_scalefactors("sf_elmu_2016_trig", "dilepton", "elmutrig_2016_HHMoriond17")
sf_muel_trig = get_scalefactors("sf_muel_2016_trig", "dilepton", "mueltrig_2016_HHMoriond17")
sf_mumu_trig = get_scalefactors("sf_mumu_2016_trig", "dilepton", "mumutrig_2016_HHMoriond17")
dilepton_sf_trig = DiLeptonScaleFactor(elelSF=sf_elel_trig, elmuSF=sf_elmu_trig, muelSF=sf_muel_trig, mumuSF=sf_mumu_trig)
cmva_discriVar = {"BTagDiscri":lambda j : j.pfCombinedMVAV2BJetTags}
sf_jet_btag_cmvaLoose  = get_scalefactors("sf_jet_2016_btag_cmvaLoose", "jet", ("btag_2016_moriond2017", "cMVAv2_loose"), additionalVariables=cmva_discriVar)
sf_jet_btag_cmvaMedium = get_scalefactors("sf_jet_2016_btag_cmvaMedium", "jet", ("btag_2016_moriond2017", "cMVAv2_medium"), additionalVariables=cmva_discriVar)
for aSF in ( sf_ele_trk, sf_ele_IDL, sf_mu_trk, sf_mu_IDL
           , sf_elel_trig, sf_elmu_trig, sf_muel_trig, sf_mumu_trig
           , sf_jet_btag_cmvaLoose, sf_jet_btag_cmvaMedium
           ):
    scale_factors.add(aSF)
## FIXME temporary hack for ZA (no cluster eta in trees)
from cp3_llbb.CommonTools.scalefactors import BinningParameters, binningVariablesByName
for sf in scale_factors:
    for bv in sf._args:
        if isinstance(bv, BinningParameters):
            new_bv = dict()
            for bvNm in bv.binningVars.iterkeys():
                if bvNm.endswith("ClusEta"):
                    new_bv[bvNm] = binningVariablesByName[bvNm.replace("ClusEta", "Eta")]
            for bvNm, bvFun in new_bv.iteritems():
                bv.binningVars[bvNm] = bvFun
## FIXME END

def make1DPlot(name, variable, selection, binning, **kwargs):
    """ 1D plot (allows to select categories, combined plot or both without duplication) """
    out = []
    doCombined = kwargs.pop("combined", True)
    categories = kwargs.pop("categories", None)
    if doCombined:
        out.append(Plot.make1D(name, variable, selection, binning, **kwargs))
    if categories:
        out += [ Plot.make1D("{0}_{cat}".format(name, cat=catNm), variable, Selection.addTo(selection, cut=catCut), binning, **kwargs) for catNm, catCut in categories.iteritems() ]
    return out

def makeControlPlots(record, hza):
    from cp3_llbb.CommonTools.treedecorators import op, makeConst, boolType
    from cp3_llbb.CommonTools.lldeco import onlyElectron, onlyMuon

    ## Define selections (this part would go into a shared python module in ZATools)
    from collections import OrderedDict as odict
    selDict = odict()

    evtSel_all = Selection([], [ record.event.weight, record.event.pu_weight ], None)

    llSel_loose = lambda ll : (
              ll.isOS
            #, onlyElectron(lambda el : el.POGIDHLTPre, muonValue=makeConst("true", boolType))(ll.l1)
            #, onlyElectron(lambda el : el.POGIDHLTPre, muonValue=makeConst("true", boolType))(ll.l2)
            )
    llCand = op.rng_find(hza.ll, llSel_loose)
    selDict["ll"] = Selection.addTo(evtSel_all,
            weight=[ lepton_sf_IDL(llCand.l1), lepton_sf_IDL(llCand.l2), dilepton_sf_trig(llCand) ],
            cut=[ ( op.rng_min(hza.ll, lambda ll : op.invariant_mass(ll.l1.L.p4, ll.l2.L.p4) ) > 12. )
                , op.rng_any(hza.ll, llSel_loose) ],
            candidate=llCand)
    lljjCand = op.rng_find(hza.lljj_deepCSV, lambda lljj : llSel_loose(lljj))
    selDict["lljj"] = Selection.addTo(evtSel_all,
            weight=[ lepton_sf_IDL(lljjCand.l1), lepton_sf_IDL(lljjCand.l2), dilepton_sf_trig(lljjCand) ],
            cut=[ ( op.rng_min(hza.ll, lambda ll : op.invariant_mass(ll.l1.L.p4, ll.l2.L.p4) ) > 12. )
                , op.rng_any(hza.lljj_deepCSV, lambda lljj : llSel_loose(lljj)) ],
            candidate=lljjCand)

    from itertools import product, tee
    allFlavCats = list("".join((f1,f2)) for f1,f2 in product(*tee(("El", "Mu"),2)))
    flavCats_ll = dict((fc, getattr(llCand, "is{0}".format(fc))) for fc in allFlavCats)
    flavCats_lljj = dict((fc, getattr(lljjCand, "is{0}".format(fc))) for fc in allFlavCats)

    from itertools import izip, count, chain
    ## Define plots
    plots = []
    for psName, presel in selDict.iteritems():
        cand = presel.candidate
        flavCats = dict()
        if psName.startswith("lljj") or psName.startswith("llbb"):
            flavCats = flavCats_lljj
        elif psName.startswith("ll"):
            flavCats = flavCats_ll
        plots += make1DPlot("{0}_llMZ".format(psName)
                    , op.invariant_mass(cand.l1.L.p4, cand.l2.L.p4), presel
                    , EquidistantBinning(50, 0., 200.), categories=flavCats
                    , title="Dilepton invariant mass", xTitle="Invariant Mass (GeV/c^{2})")

        plots += chain.from_iterable(make1DPlot("{0}_L{1:d}_{2}".format(psName, iL, varName)
                      , fun(lep.L), presel, binning
                      , title=title, xTitle=xTitle)
                    for varName, (fun, binning, title, xTitle) in lepVars.iteritems()
                    for iL, lep in izip(count(1), (cand.l1, cand.l2)))

        plots += chain(
                  chain.from_iterable(make1DPlot("{0}_L{1:d}_mu_{2}".format(psName, iL, varName)
                      , onlyMuon(fun, electronValue=elVal)(lep), presel, binning
                      , title=title, xTitle=xTitle)
                    for varName, (fun, elVal, binning, title, xTitle) in lepVars_split.iteritems()
                    for iL, lep in izip(count(1), (cand.l1, cand.l2)))
                , chain.from_iterable(make1DPlot("{0}_L{1:d}_el_{2}".format(psName, iL, varName)
                      , onlyElectron(fun, muonValue=muVal)(lep), presel, binning
                      , title=title, xTitle=xTitle)
                    for varName, (fun, muVal, binning, title, xTitle) in lepVars_split.iteritems()
                    for iL, lep in izip(count(1), (cand.l1, cand.l2)))
                )

        if psName.startswith("lljj"):
            plots += chain.from_iterable(
                    make1DPlot("{0}_J{1:d}_{2}".format(psName, iJ, varName)
                        , fun(jet), presel, binning
                        , title=title, xTitle=xTitle)
                      for varName, (fun, binning, title, xTitle) in jetVars.iteritems()
                      for iJ, jet in izip(count(1), (cand.J1, cand.J2))
                    )

    return plots

if __name__ == "__main__":
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-i", "--interactive", action="store_true", help="Launch an IPython shell to inspect the tree")
    argparser.add_argument("--reuseplotter", action="store_true", help="Don't write and compile the plotter(s), but reuse from a previous run")
    argparser.add_argument("--reusehistos", action="store_true", help="Don't create or run the plotters")
    argparser.add_argument("--skipplotit", action="store_true", help="Don't produce PDF plots")
    args = argparser.parse_args()

    if args.interactive:
        doInteractive()
    else: ## make and run a plotter
        logger.info("Loading and decorating skeleton tree")
        skelF = ROOT.TFile.Open("/storage/data/cms/store/user/asaggio/DYToLL_2J_13TeV-amcatnloFXFX-pythia8/DYToLL_2J_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_Summer16MiniAODv2/180219_144051/0000/output_mc_271.root")
        tup = decoratedZATree(skelF.Get("t"))

        controlPlots = makeControlPlots(tup, tup.hZA)

        import os.path
        from cp3_llbb.SAMADhi.SAMADhi import DbStore, Sample
        db = DbStore()
        ctrl_samples = dict((smpName, {
              "tree_name"  : "t"
            , "sample_cut" : "1."
            , "files"      : [ u"/storage/data/cms{}".format(f.lfn) for f in db.find(Sample, Sample.name.like(smpName)).one().files ]
            }) for smpName in [
                  u"DoubleEG_Run2016H-03Feb2017-v3_v6.2.0+80X_ZAAnalysis_2018-02-16"
                , u"DYToLL_2J_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_Summer16MiniAODv2_v6.2.0+80X_ZAAnalysis_2018-02-16"
                ])

        from cp3_llbb.CommonTools.histfactory import createPlotter, compilePlotter, runPlotterOnSamples, prepareWorkdir
        import os
        workdir = os.path.join(os.getcwd(), "latest_zaplots")
        if not args.reusehistos:
            if not args.reuseplotter:
                plotterdir, histosdir, plotsdir = prepareWorkdir(workdir)

                includes = [ "Math/VectorUtil.h", "ScaleFactors.h" ]
                from itertools import chain
                sf_init_lines = list(chain.from_iterable(sf.cpp_initCode for sf in scale_factors))

                createPlotter(controlPlots, tup, includes=includes, outdir=plotterdir,
                        user_initialisation=sf_init_lines, addScaleFactorsLib=True)
                plotterName = compilePlotter(plotterdir)
            else:
                plotterdir = os.path.join(workdir, "plotter")
                histosdir = os.path.join(workdir, "histos")
                plotterName = os.path.join(plotterdir, "plotter.exe")
                if not os.path.exists(plotterName):
                    raise Exception("No such file {}".format(plotterName))
                logger.info("Reusing with-MC plotter {}".format(plotterName))
                plotsdir = os.path.join(workdir, "plots")

            ## run the plotter
            from cp3_llbb.CommonTools.slurmhelpers import makeSlurmTasksMonitor as makeTasksMonitor
            clusMon = makeTasksMonitor()
            runPlotterOnSamples(plotterName, ctrl_samples, outdir=histosdir, useCluster=True, clusterworkdir=os.path.join(workdir, "slurm_histos"), taskMon=clusMon)
            clusMon.collect(wait=60) ## wait for the jobs to finish

        ## prepare plotting
        from cp3_llbb.CommonTools.plotithelpers import writePlotIt
        with open(os.path.join(workdir, "plots.yml"), "w") as plotsFile:
            writePlotIt(controlPlots, plotsFile)

        ### Example: run plotIt in one go
        ##import subprocess
        ##plotIt = os.path.join(os.path.dirname(pathCommonTools), "plotIt", "plotIt")
        ##if not args.skipplotit:
        ##    logger.info("Running plotIt")
        ##    try:
        ##        with open(os.path.join(plotsdir, "out.log"), "w") as logFile:
        ##            subprocess.check_call([plotIt, "-i", workdir, "-o", plotsdir, os.path.join(pathCommonTools, "plotit", "")], stdout=logFile, cwd=pathCommonTools)
        ##    except subprocess.CalledProcessError, e:
        ##        logger.error("Command {0} failed with exit code {1}\n{2}".format(" ".join(e.cmd), e.returncode, e.output))

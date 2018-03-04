#!/usr/bin/env python2
"""
Example: H->ZA tree decoration, interactive exploration based on that, and a plotter
"""
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True # let python do option parsing

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
Plotter demo: a method to generate plots
"""

if __name__ == "__main__":
    doInteractive() ## FIXME only with -i

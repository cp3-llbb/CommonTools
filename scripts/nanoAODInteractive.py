#!/usr/bin/env python2
import ROOT
from cp3_llbb.CommonTools.nanoaoddeco import decoratedNanoAOD
from cp3_llbb.CommonTools.treedecorators import adaptArg, op

tChain = ROOT.TChain("Events")
tChain.Add("root://xrootd-cms.infn.it//store/data/Run2016E/SingleMuon/NANOAOD/05Jan2018-v1/00000/1CC58832-C5F5-E711-BBC2-0CC47A13D3B2.root")
tChain.GetEntries() ## force load
tup = decoratedNanoAOD(tChain)

def toDraw(sth):
    return adaptArg(sth).get_TTreeDrawStr()
def leafDeps(expr):
    return list(expr._parent.leafDeps)

import IPython; IPython.embed()

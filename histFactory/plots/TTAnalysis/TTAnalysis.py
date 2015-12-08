import os
import ROOT as R

#### Get all the indices and functions definitions needed to retrieve the IDs/... ROOT can be awesome at times :) ####

pathCMS = os.getenv("CMSSW_BASE")
if pathCMS == "":
    raise Exception("CMS environment is not valid!")
pathTT = os.path.join(pathCMS, "src/cp3_llbb/TTAnalysis/")
pathTTdefs = os.path.join(pathTT, "plugins/Indices.cc")

R.gROOT.ProcessLine(".L " + pathTTdefs + "+")
TT =  R.TTAnalysis

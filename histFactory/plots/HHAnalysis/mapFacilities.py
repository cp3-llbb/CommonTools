import ROOT as R
import os

pathCMS = os.getenv("CMSSW_BASE")
if pathCMS == "":
    raise Exception("CMS environment is not valid!")
pathHH = os.path.join(pathCMS, "src/cp3_llbb/HHAnalysis/")
R.gROOT.ProcessLine("#include <%s/interface/Enums.h>"%pathHH) 
 
def getIndx_llmetjj_id_iso_btagWP_pair(lepid1, lepiso1, lepid2, lepiso2, btagWP1, btagWP2, pair): 
    bitA = R.jetPair.Count 
    bitB = bitA * R.btagWP.Count 
    bitC = bitB * R.btagWP.Count 
    bitD = bitC * R.lepIso.Count 
    bitE = bitD * R.lepID.Count 
    bitF = bitE * R.lepIso.Count 
    return bitF * getattr(R.lepID,lepid1) + bitE * getattr(R.lepIso,lepiso1) + bitD * getattr(R.lepID,lepid2) + \
           bitC * getattr(R.lepIso,lepiso2) + bitB * getattr(R.btagWP,btagWP1) + bitA * getattr(R.btagWP,btagWP2) + getattr(R.jetPair,pair)  

def getIndx_ll_id_iso(lepid1, lepiso1, lepid2, lepiso2):
    bitA = R.lepIso.Count
    bitB = bitA * R.lepID.Count
    bitC = bitB * R.lepIso.Count
    return bitC * getattr(R.lepID, lepid1) + bitB * getattr(R.lepIso, lepiso1) + bitA * getattr(R.lepID, lepid2) + getattr(R.lepIso, lepiso2) 

def getIndx_l_id_iso(lepid, lepiso):
    bitA = R.lepIso.Count
    return bitA * getattr(R.lepID, lepid) + getattr(R.lepIso, lepiso)

def getIndx_j_bTagWP(btagWP):
    return getattr(R.btagWP, btagWP)

import sys
sys.path.append("../")
from tmvaTools import * 

inFileDir = "/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/CommonTools/treeFactory/firstSkim/condor/output/"
bkgFiles = ["TT_TuneCUETP8M1_13TeV-powheg-pythia8_MiniAODv2_v1.1.0+7415_HHAnalysis_2015-11-19.v1_histos_176.root"]
sigFiles = ["GluGluToRadionToHHTo2B2VTo2L2Nu_M-500_narrow_MiniAODv2_v1.1.0+7415_HHAnalysis_2015-11-19.v1_histos_728.root"]
discriList = [
        "jj_pt",
        "ll_M",
        "ll_DR_l_l",
        "jj_DR_j_j",
        "llmetjj_DPhi_ll_jj",
        "llmetjj_minDR_l_j"
        ]
weightExpr = ""
MVAmethods = ["kBDT"]
label = "BDT_X0500vsTT_6var"

if __name__ == '__main__':
    trainMVA(inFileDir, bkgFiles, sigFiles, discriList, weightExpr, MVAmethods, label)



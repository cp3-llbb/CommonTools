import ROOT as R
from array import array
import sys
import os

def trainMVA(bkgs, sigs, discriList, trainCut, weightExpr, MVAmethods, spectatorVariables = [], label = "BDT", sigWeightExpr=None, bkgWeightExpr=None, nSignal=0, nBkg=0):
    ''' Train a MVA and write xml files for possibly different MVA methods (kBDT etc)'''

    MVA_fileName = "TMVA_"+label+".root"
    file_MVA = R.TFile(MVA_fileName,"recreate")
    print "Will write MVA info in ", MVA_fileName 

    factory = R.TMVA.Factory(label, file_MVA)

    # This will be overridden if signal or background have specific weights
    factory.SetWeightExpression(weightExpr)
    
    for discriVar in discriList :
        factory.AddVariable(discriVar)
    for spectatorVar in spectatorVariables :
        factory.AddSpectator(spectatorVar)

    bkgChain = {}
    for bkg in bkgs.keys():
        bkgChain[bkg] = R.TChain("t")
        for bkgFile in bkgs[bkg]["files"]:
            bkgChain[bkg].Add(bkgFile)
        factory.AddBackgroundTree(bkgChain[bkg], bkgs[bkg]["relativeWeight"])
    if bkgWeightExpr is not None:
        factory.SetBackgroundWeightExpression("(({})*({}))".format(weightExpr, bkgWeightExpr))

    sigChain = {}
    for sig in sigs.keys():
        sigChain[sig] = R.TChain("t")
        for sigFile in sigs[sig]["files"]:
            sigChain[sig].Add(sigFile)
        factory.AddSignalTree(sigChain[sig], sigs[sig]["relativeWeight"])
    if sigWeightExpr is not None:
        factory.SetSignalWeightExpression("(({})*({}))".format(weightExpr, sigWeightExpr))

    factory.PrepareTrainingAndTestTree(R.TCut(trainCut), "nTrain_Signal={0}:nTest_Signal={0}:nTrain_Background={1}:nTest_Background={1}".format(nSignal, nBkg))
    for MVAmethod in MVAmethods:
        factory.BookMethod(getattr(R.TMVA.Types, MVAmethod), MVAmethod, "")

    factory.TrainAllMethods()
    factory.TestAllMethods()
    factory.EvaluateAllMethods()
    file_MVA.Close()

def MVA_out_in_tree(args):
    ''' Merge MVA output(s) in trees '''
    try: 
        inFileDir = args[0]
        inFileName = args[1]
        outFileDir = args[2]
        list_dict_mva = args[3]
    except IndexError:
        print "Error: args must be a tuple with [inFileDir, inFileName, outFileDir, list_dict_mva]"
        return 
    inputFile = R.TFile.Open(os.path.join(inFileDir, inFileName))
    chain = inputFile.Get("t")
    tp_xs = inputFile.Get("cross_section").Clone()
    tp_wgt_sum = inputFile.Get("event_weight_sum").Clone()
    
    outFileName = os.path.join(outFileDir, inFileName)
    file_withBDTout = R.TFile(outFileName, "recreate")
    tree_withBDTout = chain.CloneTree(0)
    print "Merging MVA output in %s with %s entries."%(inFileName, chain.GetEntries())
    if chain.GetEntries() == 0:
        print "Skip %s because 0 entries..."%inFileName
        sys.exit()

    # list all discriminative variables needed (removing overlap)
    fullDiscrList = []
    fullSpectList = []
    for dict_mva in list_dict_mva:
        for var in dict_mva["discriList"]:
            fullDiscrList.append(var)
        for var in dict_mva["spectatorList"]:
            fullSpectList.append(var)
    seen = set()
    discrList_unique = [ var for var in fullDiscrList if var not in seen and not seen.add(var) ] # allow preserving the order
    seen = set()
    spectList_unique = [ var for var in fullSpectList if var not in seen and not seen.add(var) ] # allow preserving the order

    BDT_out = {}
    reader = {}
    dict_variableName_Array = { variable: array('f', [0]) for variable in discrList_unique }
    dict_spectatorName_Array = { spectator: array('f', [0]) for spectator in spectList_unique }
    for dict_mva in list_dict_mva :
        label = dict_mva["label"]
        xmlFile = dict_mva["xmlFile"]
        discriList = dict_mva["discriList"]
        spectatorList = dict_mva["spectatorList"]
        reader[label] = R.TMVA.Reader("Silent=1")
        for var in discriList :
            reader[label].AddVariable(var, dict_variableName_Array[var])
        for var in spectatorList :
            reader[label].AddSpectator(var, dict_spectatorName_Array[var])
        leave_BDTout = "MVA_" + label
        BDT_out[label] = array('d',[0])
        tree_withBDTout.Branch(leave_BDTout, BDT_out[label], leave_BDTout + "/D")
        reader[label].BookMVA(label, xmlFile)

    for entry in xrange(chain.GetEntries()):
        chain.GetEntry(entry)
        for dict_mva in list_dict_mva:
            discriList = dict_mva["discriList"]
            spectatorList = dict_mva["spectatorList"]
            label = dict_mva["label"]
            xmlFile = dict_mva["xmlFile"]
            for var in discriList:
                dict_variableName_Array[var][0] = getattr(chain, var)
            for var in spectatorList:
                dict_spectatorName_Array[var][0] = getattr(chain, var)
            BDT_out[label][0] = reader[label].EvaluateMVA(label)
        tree_withBDTout.Fill()

    print "Number of output tree entries: ", tree_withBDTout.GetEntries()
    tree_withBDTout.Write()
    tp_xs.Write()
    tp_wgt_sum.Write()
    file_withBDTout.Close()
    inputFile.Close()
    print "Output file : ", outFileName, " written.\n\n"


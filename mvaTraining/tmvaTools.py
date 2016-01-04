import ROOT as R
from array import array

def trainMVA(inFileDir, bkgFiles, sigFiles, discriList, weightExpr, MVAmethods, label = "TMVA"):

    bkgChain  =  R.TChain("t")
    for bkgFile in bkgFiles : 
        bkgChain.Add(inFileDir+bkgFile)

    sigChain  =  R.TChain("t")
    for sigFile in sigFiles : 
        sigChain.Add(inFileDir+sigFile)

    Nbkg = float(bkgChain.GetEntries())
    Nsig = float(sigChain.GetEntries())

    bkg_weight = 1/Nbkg
    sig_weight = 1/Nsig

    MVA_fileName = "TMVA_"+label+".root"
    file_MVA = R.TFile(MVA_fileName,"recreate")
    print "Will write MVA info in ", MVA_fileName 

    factory = R.TMVA.Factory(label, file_MVA)
    factory.SetWeightExpression(weightExpr)
    for discriVar in discriList :
        factory.AddVariable(discriVar)
    factory.AddBackgroundTree(bkgChain, bkg_weight)
    factory.AddSignalTree(sigChain, sig_weight)
    for MVAmethod in MVAmethods :
        factory.BookMethod(getattr(R.TMVA.Types, MVAmethod), MVAmethod, "")

    factory.TrainAllMethods()
    factory.TestAllMethods()
    factory.EvaluateAllMethods()
    file_MVA.Close()

def MVA_out_in_tree(inFileDir, file, discriList, xmlFile, label, outFileDir):   

    print "Merging MVA output in " + file +"."
    chain = R.TChain("t")
    chain.Add(inFileDir + file)
    
    outFileName = outFileDir+file.replace(".root",label+".root")
    file_withBDTout = R.TFile(outFileName, "create")
    tree_withBDTout = chain.CloneTree(0)
    print "Number of input tree entries : ", chain.GetEntries()
    
    leave_BDTout = "MVA_"+label
    BDT_out = array('d',[0])
    tree_withBDTout.Branch(leave_BDTout, BDT_out, leave_BDTout+"/D")    

    reader = R.TMVA.Reader()

    dict_variableName_Array = {variable : array('f', [0]) for variable in discriList}
    for var in discriList :
        reader.AddVariable(var, dict_variableName_Array[var])

    reader.BookMVA(label, xmlFile)

    for entry in xrange(chain.GetEntries()):
        chain.GetEntry(entry)
        for var in discriList :
            dict_variableName_Array[var][0] = getattr(chain, var)
        BDT_out[0] = reader.EvaluateMVA(label)
        tree_withBDTout.Fill()
    print "Number of output tree entries : ",tree_withBDTout.GetEntries()
    tree_withBDTout.Write()
    file_withBDTout.Close()
    print "Output file : ", outFileName, " written."


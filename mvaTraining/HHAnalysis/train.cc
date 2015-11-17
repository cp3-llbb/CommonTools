// ROOT HEADERS
#include "TFile.h"
#include "TTree.h"
// TMVA HEADERS
#include "TMVA/Factory.h"
#include "TMVA/Tools.h"

//int train()
int main(int argc, char *argv[])
{
    // SAMADhi: 657, graviton m500 
    TFile *infile_sig = TFile::Open("/home/fynu/obondu/Higgs/CMSSW_7_4_15/src/cp3_llbb/CommonTools/treeFactory/test/v04/GluGluToBulkGravitonToHHTo2B2VTo2L2Nu_M-500_narrow_MiniAODv2_v1.1.0+7415_HHAnalysis_2015-11-19.v1_skim.root");
    TTree *intree_sig = (TTree*)infile_sig->Get("t");
    // SAMADhi: 670, TTbar inclusive
    TFile *infile_bkg = TFile::Open("/home/fynu/obondu/Higgs/CMSSW_7_4_15/src/cp3_llbb/CommonTools/treeFactory/test/v04/TT_TuneCUETP8M1_13TeV-powheg-pythia8_MiniAODv2_v1.1.0+7415_HHAnalysis_2015-11-19.v1_skim.root");
    TTree *intree_bkg = (TTree*)infile_bkg->Get("t");
    TFile *outfile = new TFile("test.root", "RECREATE");

    double w_sig = 1./(intree_sig->GetEntries());
    double w_bkg = 1./(intree_bkg->GetEntries());
    TMVA::Factory* factory = new TMVA::Factory("test.xml",outfile,"!V:!Silent:Color:DrawProgressBar:AnalysisType=Classification");
    factory->AddSignalTree(intree_sig, w_sig);
    factory->AddBackgroundTree(intree_bkg, w_bkg);

//    factory->AddVariable("jj_m", "m_{jj}", "GeV", 'F');
//    factory->AddVariable("jj_pt", "p_{T}^{jj}", "GeV", 'F');
//    factory->AddVariable("ll_m", "m_{ll}", "GeV", 'F');
//    factory->AddVariable("ll_pt", "p_{T}^{ll}", "GeV", 'F');
//    factory->AddVariable("ll_dr", "#Delta R(l,l)", "", 'F');
//    factory->AddVariable("jj_dr", "#Delta R(j,j)", "", 'F');
//    factory->AddVariable("lljj_dphi", "#Delta#phi(ll,jj)", "", 'F');
//    factory->AddVariable("lj_mindr", "min(#Delta R(l,j))", "", 'F');
    factory->AddVariable("jj_pt", "p_{T}^{jj}", "GeV", 'F');
    factory->AddVariable("ll_m", "m_{ll}", "GeV", 'F');
    factory->AddVariable("ll_pt", "p_{T}^{ll}", "GeV", 'F');
    factory->AddVariable("DR_l_l", "#Delta R(l,l)", "", 'F');
    factory->AddVariable("DR_j_j", "#Delta R(j,j)", "", 'F');
    factory->AddVariable("DPhi_ll_jj", "#Delta#phi(ll,jj)", "", 'F');
    factory->AddVariable("MinDR_l_j", "min(#Delta R(l,j))", "", 'F');
    factory->SetWeightExpression("w");
    int nsig_train, nsig_test, nbkg_train, nbkg_test;
    nsig_train = 0;
    nsig_test = 0;
    nbkg_train = 0;
    nbkg_test = 0;
    factory->PrepareTrainingAndTestTree("", Form("nTrain_Signal=%i:nTest_Signal=%i:nTrain_Background=%i:nTest_Background=%i:SplitMode=Alternate", nsig_train, nsig_test, nbkg_train, nbkg_test) );
    // Out of the box
    factory->BookMethod(TMVA::Types::kLikelihood, "Likelihood","" );
    factory->BookMethod(TMVA::Types::kKNN, "k-NN","" );
    factory->BookMethod(TMVA::Types::kBDT, "BDT","" );

    std::cout << "##### TRAIN #####" << std::endl;
    factory->TrainAllMethods();
    std::cout << "##### TEST #####" << std::endl;
    factory->TestAllMethods();
    std::cout << "##### EVALUATE #####" << std::endl;
    factory->EvaluateAllMethods();

    std::cout << "##### CLEANING #####" << std::endl;
    outfile->Close();

    std::cout << "##### EXITING #####" << std::endl;
    return 0;
}

#include "TH1.h"
#include "TH2.h"
#include "TCanvas.h"
#include "TFile.h"
#include <iostream>
#include <cmath>
#include <cstdlib>
using namespace std;


string sampleDir="/home/fynu/obondu/Higgs/CommonTools/plotUtils";
string TTFile = sampleDir+"/TTJets_TuneCUETP8M1_amcatnloFXFX_25ns_15c5fa1_c106444_histos.root";
string DYFile = sampleDir+"/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX_Asympt25ns_15c5fa1_c106444_histos.root";

double L_exp = 1. ; //Expected lumi

double X_signal = 1. ; //Xsection in fb
double X_TT = 6025.2;
double w_TT = 90547676992.0;
double X_DY = 831.76;
double w_DY = 454248904133.0;


double FigOfMerit(double sig, double noise){
    if ((sig+noise<0) ||(noise<0) || sig<0)return(0);
    if (sig == 0) return(0);
    double toReturn = 2*(sqrt(sig+noise)-sqrt(noise));
//    double toReturn = sqrt(2*(sig+noise)*log(1+sig/noise)-2*sig);
    if (toReturn==toReturn)return(toReturn);
    else return(0);
}



int compareSN(string sigFile="",string name = "auto.png", double lmax=-1, string collection = "dielectron_mass", double w_signal=300000.0){
    TFile *fSig;
    if (sigFile!=""){
        fSig = new TFile(sigFile.c_str());
    }
    else{
        return(0);
    }
    TFile * fTT = new TFile(TTFile.c_str());
    TFile * fDY = new TFile(DYFile.c_str());

    TH1D * hSig = (TH1D*) fSig->Get(collection.c_str());
    TH1D * hTT = (TH1D*) fTT->Get(collection.c_str());
    TH1D * hDY = (TH1D*) fDY->Get(collection.c_str());

    int l = hSig->GetSize()-2;
    if (lmax>0 and l>lmax)l=lmax;

    TH2 * h2 = new TH2D("FOM","FOM",l,0,l,l,0,l);
    for (int chigh=0; chigh<l; chigh++){
        for(int clow=0; clow<chigh; clow++){
            double s = hSig->Integral(clow,chigh)*L_exp*X_signal*1./w_signal;
            double n = hTT->Integral(clow,chigh)*L_exp*X_TT*1./w_TT;
            n += hDY->Integral(clow,chigh)*X_DY*1./w_DY*L_exp;
            h2->Fill(hSig->GetBinCenter(clow),hSig->GetBinCenter(chigh),FigOfMerit(s,n)); 
        }
    }
    TCanvas * c = new TCanvas;

    h2->SetTitle(name.c_str());
    h2->GetXaxis()->SetTitle("cut Low (GeV)");
    h2->GetYaxis()->SetTitle("cut High (GeV)");
    h2->Draw("colz");
    h2->SetStats(0);
    c->Print(name.c_str());
    return(1);
}



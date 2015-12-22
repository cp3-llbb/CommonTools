#! /usr/bin/env python

import ROOT as R
import argparse

def parseArguments():
    parser = argparse.ArgumentParser(description='Build transfer functions out of 2D histogram created by plotter.')
    parser.add_argument('-i', '--input', type=str, dest='input', help='Input file', required=True)
    parser.add_argument('-o', '--output', type=str, dest='output', help='Output file', required=True)
    return parser.parse_args()

def normalizeDeltaE(hist):
    xAxis = hist.GetXaxis()
    yAxis = hist.GetYaxis()

    for i in range(1, xAxis.GetNbins()+1):
        binWidths = []
        for j in range(1, yAxis.GetNbins()+1):
            width = yAxis.GetBinWidth(j)
            if width not in binWidths:
                binWidths.append(width)

        binWidths.sort()
        minWidth = binWidths[0]

        for j in range(1, yAxis.GetNbins()+1):
            oldContent = hist.GetBinContent(i, j)
            widthRatio = yAxis.GetBinWidth(j)/minWidth
            hist.SetBinContent(i, j, oldContent/widthRatio)

    hist.Smooth(1)
    hist.Smooth(1)
    
    for i in range(1, xAxis.GetNbins()+1):
        
        for j in range(1, yAxis.GetNbins()+1):
            if xAxis.GetBinUpEdge(i) + yAxis.GetBinUpEdge(j) < 30:
                hist.SetBinContent(i, j, 0)

        integral = hist.Integral(i, i, 1, yAxis.GetNbins())

        for j in range(1, yAxis.GetNbins()+1):
            oldContent = hist.GetBinContent(i, j)

            if integral > 0:
                hist.SetBinContent(i, j, oldContent/integral)
            else:
                hist.SetBinContent(i, j, 0)

def normAndSmooth(TFset, inFile, outFile):
    inFile = R.TFile.Open(inFile)
    outFile = R.TFile(outFile, "recreate")
   
    for TF in TFset:
        inputHists = []
        for hist in TF["histNames"]:
            inputHists.append( inFile.Get(hist) )
        
        DeltaEvsE = inputHists[0].Clone( TF["base"] )
        for hist in inputHists[1:]:
            DeltaEvsE.Add(hist)

        DeltaEvsE.GetXaxis().SetTitle("E_{gen}")
        DeltaEvsE.GetYaxis().SetTitle("E_{rec} - E_{gen}")
        
        DeltaEvsE_Smoothed = DeltaEvsE.Clone( TF["smooth"] )
        #DeltaEvsE_Smoothed.Smooth(1)
        
        DeltaEvsE_Norm = DeltaEvsE_Smoothed.Clone( TF["norm"] )
        normalizeDeltaE(DeltaEvsE_Norm)
        
        DeltaEvsE.Write()
        DeltaEvsE_Smoothed.Write()
        DeltaEvsE_Norm.Write()
    
    outFile.Close()
    inFile.Close()

if __name__ == "__main__":
    options = parseArguments()

    TFset = [
        {
            "histNames":
                [
                    "TF_b_E_CAT_MuMu_IDLL_IsoLL_bb_LL",
                    "TF_bbar_E_CAT_MuMu_IDLL_IsoLL_bb_LL",
                    "TF_b_E_CAT_ElEl_IDLL_IsoLL_bb_LL",
                    "TF_bbar_E_CAT_ElEl_IDLL_IsoLL_bb_LL",
                    "TF_b_E_CAT_ElMu_IDLL_IsoLL_bb_LL",
                    "TF_bbar_E_CAT_ElMu_IDLL_IsoLL_bb_LL",
                    "TF_b_E_CAT_MuEl_IDLL_IsoLL_bb_LL",
                    "TF_bbar_E_CAT_MuEl_IDLL_IsoLL_bb_LL",
                ],
            "base": "bJet_bParton_DeltaEvsE",
            "smooth": "bJet_bParton_DeltaEvsE_Smoothed",
            "norm": "bJet_bParton_DeltaEvsE_Norm"
        },
        {
            "histNames":
                [
                    "TF_BA_b_E_CAT_MuMu_IDLL_IsoLL_bb_LL",
                    "TF_BA_bbar_E_CAT_MuMu_IDLL_IsoLL_bb_LL",
                    "TF_BA_b_E_CAT_ElEl_IDLL_IsoLL_bb_LL",
                    "TF_BA_bbar_E_CAT_ElEl_IDLL_IsoLL_bb_LL",
                    "TF_BA_b_E_CAT_ElMu_IDLL_IsoLL_bb_LL",
                    "TF_BA_bbar_E_CAT_ElMu_IDLL_IsoLL_bb_LL",
                    "TF_BA_b_E_CAT_MuEl_IDLL_IsoLL_bb_LL",
                    "TF_BA_bbar_E_CAT_MuEl_IDLL_IsoLL_bb_LL",
                ],
            "base": "bJet_BA_bParton_DeltaEvsE",
            "smooth": "bJet_BA_bParton_DeltaEvsE_Smoothed",
            "norm": "bJet_BA_bParton_DeltaEvsE_Norm"
        },
        {
            "histNames":
                [
                    "TF_EC_b_E_CAT_MuMu_IDLL_IsoLL_bb_LL",
                    "TF_EC_bbar_E_CAT_MuMu_IDLL_IsoLL_bb_LL",
                    "TF_EC_b_E_CAT_ElEl_IDLL_IsoLL_bb_LL",
                    "TF_EC_bbar_E_CAT_ElEl_IDLL_IsoLL_bb_LL",
                    "TF_EC_b_E_CAT_ElMu_IDLL_IsoLL_bb_LL",
                    "TF_EC_bbar_E_CAT_ElMu_IDLL_IsoLL_bb_LL",
                    "TF_EC_b_E_CAT_MuEl_IDLL_IsoLL_bb_LL",
                    "TF_EC_bbar_E_CAT_MuEl_IDLL_IsoLL_bb_LL",
                ],
            "base": "bJet_EC_bParton_DeltaEvsE",
            "smooth": "bJet_EC_bParton_DeltaEvsE_Smoothed",
            "norm": "bJet_EC_bParton_DeltaEvsE_Norm"
        }
    ]

    normAndSmooth(TFset, options.input, options.output)


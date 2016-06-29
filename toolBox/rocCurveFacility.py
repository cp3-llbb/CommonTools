import ROOT
import numpy as np
import math

def drawEffVsCutCurve(myTH1, total = 0):
    """ Create and return eff. vs. cut TGraph, from a one-dimensional histogram.
    The efficiencies are computed relative to the histogram's integral,
    or relative to 'total' if it is given. """

    discrV = [ myTH1.GetBinLowEdge(1) ]
    integral = myTH1.Integral()
    totintegral = myTH1.Integral()
    effV = [ integral/totintegral ]

    for i in xrange(2, myTH1.GetNbinsX()):
        discrV.append(myTH1.GetBinLowEdge(i))
        integral -= myTH1.GetBinContent(i-1)
        effV.append(integral/totintegral)

    # We may want the max. efficiency to be correctly normalised,
    # if the TH1 passed as argument doesn't cover the whole range.
    if total is not 0:
        if total < integral:
            print "Warning in createEffVsCutCurve: total number specified to be *smaller* than the histograms's integral. Something might be wrong."
        integral = total
    #if integral != 0 :
    #    effV = [ x/integral for x in effV ]
    #print len(discrV), discrV, effV
    return ROOT.TGraph(len(discrV), np.array(discrV), np.array(effV))

def drawROCfromEffVsCutCurves(sigGraph, bkgGraph):
    """ Return ROC curve drawn from the "efficiency vs. discriminant" cut curves of signal and background. 
    For now, assume the range and binning of the discriminants is the same for both signal and background.
    This might have to be refined. """

    nPoints = sigGraph.GetN() 

    if nPoints != bkgGraph.GetN():
        print "Background and signal curves must have the same number of entries!"
        print "Entries signal:     {}".format(nPoints) 
        print "Entries background: {}".format(bkgGraph.GetN())
        sys.exit(1)

    sigEff = []
    sigEffErrXLow = []
    sigEffErrXUp = []
    bkgEff = []
    bkgEffErrYLow = []
    bkgEffErrYUp = []

    for i in range(nPoints):
        sigValX = ROOT.Double()
        sigValY = ROOT.Double()
        bkgValX = ROOT.Double()
        bkgValY = ROOT.Double()

        sigGraph.GetPoint(i, sigValX, sigValY)
        bkgGraph.GetPoint(i, bkgValX, bkgValY)

        sigEff.append(sigValY)
        sigEffErrXLow.append(sigGraph.GetErrorXlow(i))
        sigEffErrXUp.append(sigGraph.GetErrorXhigh(i))

        bkgEff.append(bkgValY)
        bkgEffErrYLow.append(bkgGraph.GetErrorYlow(i))
        bkgEffErrYUp.append(bkgGraph.GetErrorYhigh(i))

    #return ROOT.TGraphAsymmErrors(nPoints, np.array(sigEff), np.array(bkgEff), np.array(sigEffErrXLow), np.array(sigEffErrXUp), np.array(bkgEffErrYLow), np.array(bkgEffErrYUp))
    return ROOT.TGraphAsymmErrors(nPoints, np.array(bkgEff), np.array(sigEff), np.array(bkgEffErrYLow), np.array(bkgEffErrYUp), np.array(sigEffErrXLow), np.array(sigEffErrXUp))

def drawFigMeritVsCutCurve(bkgTH1, sigTH1, total = 0): # Not implemented
    """ Create and return 2 x (sqrt(S+B)-sqrt(B)) vs. cut TGraph, from two one-dimensional histograms. """

    discrV = [ ]
    effV = [ ]

    for i in xrange(1, bkgTH1.GetNbinsX() + 1):
        discrV.append(bkgTH1.GetBinLowEdge(i))
        nBkg = bkgTH1.Integral(i, bkgTH1.GetNbinsX() + 1)
        nSig = sigTH1.Integral(i, sigTH1.GetNbinsX() + 1)
        effV.append(2*(math.sqrt(nSig+nBkg) - math.sqrt(nBkg)))

    return ROOT.TGraph(len(discrV), np.array(discrV), np.array(effV))



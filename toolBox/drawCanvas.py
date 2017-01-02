import ROOT
import os
from math import sqrt

def printCanvas(canvas, name, formats, directory):
    for format in formats:
        outFile = os.path.join(directory, name + "." + format)
        canvas.Print(outFile)


def createRatioFromGraph(num, denom):
    """Build and return a ratio graph from two TGraphError objects.
    Assumes the two objects have points at the same abscissas."""

    n = num.GetN()
    assert(n == denom.GetN())

    x_list = []
    ratio_list = []
    ratio_list_err = []
    
    th1_num = ROOT.TH1F("temp_num", "temp", n+1, 0, 1)
    th1_num.SetDirectory(0)
    th1_num.Sumw2()
    th1_denom = ROOT.TH1F("temp_denom", "temp", n+1, 0, 1)
    th1_denom.SetDirectory(0)
    th1_denom.Sumw2()
    
    for i in xrange(n):
        x = ROOT.Double()
        
        num_y = ROOT.Double()
        num.GetPoint(i, x, num_y)
        num_err = num.GetErrorY(i)
        th1_num.SetBinContent(i+1, num_y)
        th1_num.SetBinError(i+1, num_err)
        
        denom_y = ROOT.Double()
        denom.GetPoint(i, x, denom_y)
        denom_err = denom.GetErrorY(i)
        th1_denom.SetBinContent(i+1, denom_y)
        th1_denom.SetBinError(i+1, denom_err)

    th1_num.Divide(th1_denom)

    ratio = ROOT.TGraphAsymmErrors(n)

    for i in xrange(n):
        x = ROOT.Double()
        y = ROOT.Double()
        num.GetPoint(i, x, num_y)
        
        ratio.SetPoint(i, x, th1_num.GetBinContent(i+1))
        ratio.SetPointError(i, 0, 0, th1_num.GetBinErrorLow(i+1), th1_num.GetBinErrorUp(i+1))

    ratio.SetMarkerColor(1)
    ratio.SetMarkerSize(0.6)
    ratio.SetMarkerStyle(20)

    return ratio


def getGraphMinMax(graph):
    """Return the mininmum and maximum ordinate values of a TGraph."""

    x = ROOT.Double()
    y = ROOT.Double()
    graph.GetPoint(0, x, y)
    min = float(y)
    max = float(y)
    for i in xrange(1, graph.GetN()):
        graph.GetPoint(i, x, y)
        if y > max:
            max = float(y)
        if y < min:
            min = float(y)
    return min, max        


def drawTGraph(graphs, name, xLabel="", yLabel="", legend=None, leftText="", rightText="", formats=["pdf"], dir=".", style="P", range=None, doLogX=False, logRange=None, ratio=None):
    """Draw and print a set of TGraphs on a canvas."""

    gStyle()

    pads = {}

    if ratio is not None:
        pads["canvas"] = ROOT.TCanvas(name, name, 550, 450)
        pads["base"] = ROOT.TPad("base", "", 0, 0, 1, 1)
        pads["base"].Draw()
        pads["base"].cd()
        pads["hist"] = ROOT.TPad("hist", name, 0, 0.2, 1, 1)
    else:
        pads["canvas"] = ROOT.TCanvas(name, name, 550, 400)
        pads["base"] = ROOT.TPad("base", "", 0, 0, 1, 1)
        pads["base"].Draw()
        pads["base"].cd()
        pads["hist"] = ROOT.TPad("hist", name, 0, 0, 1, 1)
    pads["hist"].SetGrid()
    pads["hist"].Draw()
    pads["hist"].cd()
    
    Tleft = ROOT.TLatex(0.125, 0.92, leftText)
    Tleft.SetNDC(ROOT.kTRUE) 
    Tleft.SetTextSize(0.048)
    font = Tleft.GetTextFont() 
    Tright = ROOT.TLatex(0.8, 0.85, rightText) 
    Tright.SetNDC(ROOT.kTRUE) 
    Tright.SetTextSize(0.048)
    Tright.SetTextFont(font) 

    mg = ROOT.TMultiGraph()
    colors = [ ROOT.kRed, ROOT.kBlue, ROOT.kMagenta, ROOT.kCyan+1, ROOT.kGreen+2, ROOT.kOrange+1 ]
    markers = [20, 21, 22, 23, 29, 33, 34]
    
    for i, graph in enumerate(graphs):
        graph.SetMarkerColor(colors[i])
        graph.SetLineColor(colors[i])
        graph.SetLineWidth(2)
        graph.SetMarkerStyle(markers[i])
        mg.Add(graph)
    
    mg.Draw("A" + style)
    mg.GetXaxis().SetTitle(xLabel)
    mg.GetXaxis().SetTitleFont(font)
    if range:
        mg.GetXaxis().SetRangeUser(range[0][0], range[0][1])
        mg.GetYaxis().SetRangeUser(range[1][0], range[1][1])
    mg.GetYaxis().SetTitle(yLabel)
    mg.GetYaxis().SetTitleFont(font)
    mg.SetTitle("")
    
    if legend is not None:
        legend.SetTextFont(font) 
        legend.SetFillColor(10)
        legend.SetFillStyle(0)
        legend.SetLineColor(0)
        legend.SetTextSize(0.035)
        legend.Draw() 

    Tleft.Draw() 
    Tright.Draw() 
    
    pads["base"].cd()

    if ratio is not None:
        pads["ratio"] = ROOT.TPad("ratio", "", 0, 0, 1, 0.2)
        pads["ratio"].Draw()
        pads["ratio"].cd()
        pads["ratio"].SetGrid()
        
        tmp_h = ROOT.TH1F(name + "tmp_ratio", "", 1, mg.GetXaxis().GetXmin(), mg.GetXaxis().GetXmax())
        tmp_h.GetYaxis().SetTitleSize(0.2)
        tmp_h.GetYaxis().SetTitleOffset(0.2)
        tmp_h.GetYaxis().CenterTitle()
        tmp_h.GetYaxis().SetNdivisions(6, 2, 0)
        tmp_h.GetYaxis().SetLabelSize(0.15)
        tmp_h.GetXaxis().SetNdivisions(5, 5, 0, 0)
        tmp_h.GetXaxis().SetLabelSize(0.0)
        tmp_h.SetDirectory(0)
        
        ratio = createRatioFromGraph(graphs[ratio[0]], graphs[ratio[1]])
        min, max = getGraphMinMax(ratio)
        tmp_h.GetYaxis().SetRangeUser(0.9*min, 1.1*max)
        tmp_h.Draw()
        ratio.Draw(style)
        
        unity = ROOT.TF1("unity", "1", -1000, 1000)
        unity.SetLineColor(8)
        unity.SetLineWidth(1)
        unity.SetLineStyle(1)
        unity.Draw("same")

    printCanvas(pads["canvas"], name, formats, dir) 

    if doLogX:
        if logRange:
            mg.GetXaxis().SetRangeUser(logRange[0][0], logRange[0][1])
            mg.GetYaxis().SetRangeUser(logRange[1][0], logRange[1][1])
        pads["hist"].SetLogx()
        printCanvas(pads["canvas"], name + "_logX", formats, dir) 


def gStyle():
    #ROOT.gROOT.SetStyle("Plain")
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)
    # Fonts
    ROOT.gStyle.SetTextFont(42)
    ROOT.gStyle.SetTextSize(0.06)
    #ROOT.gStyle.SetLegendTextSize(0.05)
    ROOT.gStyle.SetLabelFont(42,"xyz")
    ROOT.gStyle.SetLabelSize(0.035,"xyx")
    ROOT.gStyle.SetTitleOffset(1.4,"xyz")
    ROOT.gStyle.SetTitleSize(0.035,"xyz")
    ROOT.gStyle.SetHistLineWidth(2)
    ROOT.gStyle.SetHistLineColor(1)

    ROOT.gStyle.SetPadBorderMode(0)
    ROOT.gStyle.SetPadColor(0)

    ROOT.gStyle.SetPaperSize(20,26)
    ROOT.gStyle.SetPadTopMargin(0.10)  #055)
    ROOT.gStyle.SetPadRightMargin(0.055)
    ROOT.gStyle.SetPadBottomMargin(0.15)
    ROOT.gStyle.SetPadLeftMargin(0.125)

    ROOT.gStyle.SetFrameBorderMode(0) 

    ROOT.TGaxis.SetExponentOffset(-0.06, 0., "y")

    #ROOT.gStyle.SetPadTickX(1) # To get tick marks on the opposite side of the frame
    #ROOT.gStyle.SetPadTickY(1) 


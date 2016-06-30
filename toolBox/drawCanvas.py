import ROOT

def printCanvas(canvas, name, formats, directory):
    for format in formats : 
        outFile=directory+"/"+name+"."+format
        canvas.Print(outFile)

def drawTGraph(graphs, name, xlabel, ylabel, legend, leftText, rightText, formats, directory, range=None, log_range=None):
    canvas=ROOT.TCanvas(name,name, 550, 400)
    canvas.SetGridx()
    canvas.SetGridy()
    Tleft=ROOT.TLatex(0.125,0.92,leftText)
    Tleft.SetNDC(ROOT.kTRUE) 
    Tleft.SetTextSize(0.048)
    #font = Tleft.GetTextFont() 
    #TPaveText* Tright=new TPaveText(0.8,0.85,0.945,0.90,"NDC") 
    #Tright.SetTextFont(font) 
    #Tright.AddText(rightText) 
    #Tright.SetFillColor(0)

    mg = ROOT.TMultiGraph()
    colors = [ ROOT.kRed, ROOT.kMagenta, ROOT.kBlue, ROOT.kCyan+1, ROOT.kGreen+2, ROOT.kOrange+1 ]
    markers = [20, 21, 22, 23, 29, 33, 34]
    for i,graph in enumerate(graphs):
        graph.SetMarkerColor(colors[i])
        graph.SetLineColor(colors[i])
        graph.SetLineWidth(2)
        graph.SetMarkerStyle(markers[i])
        mg.Add(graph)
    mg.Draw("AL")
    mg.GetXaxis().SetTitle(xlabel)
    #mg.GetXaxis().SetTitleFont(font)
    if range:
        mg.GetXaxis().SetRangeUser(range[0][0], range[0][1])
        mg.GetYaxis().SetRangeUser(range[1][0], range[1][1])
    mg.GetYaxis().SetTitle(ylabel)
    #mg.GetYaxis().SetTitleFont(font)
    mg.SetTitle("")
    #legend.SetTextFont(font) 
    legend.SetFillColor(10)
    legend.SetFillStyle(0)
    legend.SetLineColor(0)
    legend.SetTextSize(0.035)
    legend.Draw() 
    Tleft.Draw() 
    #Tright.Draw() 
    #canvas.Write() 
    printCanvas(canvas, name, formats, directory) 
    if log_range:
        mg.GetXaxis().SetRangeUser(log_range[0][0], log_range[0][1])
        mg.GetYaxis().SetRangeUser(log_range[1][0], log_range[1][1])

    canvas.SetLogx()
    printCanvas(canvas, name+"_logX", formats, directory) 


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


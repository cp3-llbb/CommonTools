import ROOT

def printCanvas(canvas, name, formats, directory):
    for format in formats : 
        outFile=directory+"/"+name+"."+format
        canvas.Print(outFile)

def drawTGraph(graphs, name, xlabel, ylabel, legend, leftText, rightText, formats, directory):
    canvas=ROOT.TCanvas(name,name)
    #canvas.SetGridx()
    #canvas.SetGridy()
    Tleft=ROOT.TLatex(0.125,0.91,leftText)
    Tleft.SetNDC(ROOT.kTRUE) 
    Tleft.SetTextSize(0.048) 
    font = Tleft.GetTextFont() 
    #TPaveText* Tright=new TPaveText(0.8,0.85,0.945,0.90,"NDC") 
    #Tright.SetTextFont(font) 
    #Tright.AddText(rightText) 
    #Tright.SetFillColor(0)
    mg = ROOT.TMultiGraph()
    colors = [1, 100, 12, 28, 89, 8, 74]
    color = 0
    markers = [20, 21, 22, 23, 29, 33, 34]
    marker = 0
    for graph in graphs:
        graph.SetMarkerColor(colors[color])
        graph.SetMarkerStyle(markers[marker])
        mg.Add(graph)
        color += 1
        marker += 1 
        if color == 7 :
            print "If you want to avoid same colors, add some in drawCanvas.py"
    mg.Draw("AP")
    mg.GetXaxis().SetTitle(xlabel)
    mg.GetXaxis().SetTitleFont(font)
    #mg.GetYaxis().SetRangeUser(0.7,1.3)
    mg.GetYaxis().SetTitle(ylabel)
    mg.GetYaxis().SetTitleFont(font)
    mg.GetYaxis().SetTitleOffset(0.87)
    mg.SetTitle("")
    legend.SetTextFont(font) 
    legend.SetFillColor(0)
    legend.SetLineColor(0)
    legend.Draw() 
    Tleft.Draw() 
    #Tright.Draw() 
    #canvas.Write() 
    printCanvas(canvas, name, formats, directory) 
    canvas.SetLogx()
    printCanvas(canvas, name+"_logX", formats, directory) 
    #lepPosMiddle[4]={0.4,0.4,0.6,0.6} 


def gStyle():
    ROOT.gROOT.SetStyle("Plain")
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)
    # Fonts
    ROOT.gStyle.SetTextFont(132)
    ROOT.gStyle.SetTextSize(0.08)
    ROOT.gStyle.SetLabelFont(132,"x")
    ROOT.gStyle.SetLabelFont(132,"y")
    ROOT.gStyle.SetTitleOffset(1,"x")
    ROOT.gStyle.SetTitleOffset(1,"y")
    ROOT.gStyle.SetLabelFont(132,"z")
    ROOT.gStyle.SetLabelSize(0.05,"x")
    ROOT.gStyle.SetTitleSize(0.06,"x")
    ROOT.gStyle.SetLabelSize(0.05,"y")
    ROOT.gStyle.SetTitleSize(0.06,"y")
    ROOT.gStyle.SetLabelSize(0.05,"z")
    ROOT.gStyle.SetTitleSize(0.06,"z")
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

    #ROOT.gStyle.SetPadTickX(1) # To get tick marks on the opposite side of the frame
    #ROOT.gStyle.SetPadTickY(1) 


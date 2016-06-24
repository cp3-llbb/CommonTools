#! /usr/bin/env python

import argparse
import re
import sys

parser = argparse.ArgumentParser(description='Flatten TH2s to TH1s.')

parser.add_argument('inputs', metavar='input', nargs='+', help='The ROOT input file containing histograms')
parser.add_argument('-r', '--regex', metavar='myHist_.*', nargs='+', help='Regexp to search histos to be flattened', required=True)
parser.add_argument('-a', '--axis', metavar='x', choices = ['x', 'y'], help='Remove x or y axis', required=True)
parser.add_argument('-p', '--prefix', metavar='flat_', default="flat_", help='Prefix to the name of the histogram')

args = parser.parse_args()

import ROOT

for input in args.inputs:
    
    print("Working on %r...") % input
    f = ROOT.TFile.Open(input)
    if not f or f.IsZombie():
        continue

    # List keys, retrieve TH2s to be flattened

    selectedTH2Names = set()
    selectedTH2s = []

    for key in f.GetListOfKeys():
        
        for histo in args.regex:
            
            if re.match(histo, key.GetName()):
                m_th2 = f.Get(key.GetName())
                
                if not m_th2.InheritsFrom("TH2"):
                    print "Warning: histogram {} matches a regexp, but is not a TH2!".format(m_th2.GetName())
                    continue

                if m_th2.GetName() in selectedTH2Names: 
                    continue
                
                selectedTH2Names.add(m_th2.GetName())
                selectedTH2s.append(m_th2)

    # Flatten!

    outputTH1s = []

    for m_th2 in selectedTH2s:
        if args.axis == 'x':
            m_axis = m_th2.GetYaxis()
            m_otherAxis = m_th2.GetXaxis()
        if args.axis == 'y':
            m_axis = m_th2.GetXaxis()
            m_otherAaxis = m_th2.GetYaxis()
        
        nBinsX = m_th2.GetXaxis().GetNbins()
        nBinsY = m_th2.GetYaxis().GetNbins()
        nBins = nBinsX * nBinsY 
        start = m_axis.GetXmin()
        end = m_otherAxis.GetNbins() * (m_axis.GetXmax() - start) + start
        
        m_th1 = ROOT.TH1F(args.prefix + m_th2.GetName(), args.prefix + m_th2.GetTitle(), nBins, start, end)
        m_th1.Sumw2()
        m_th1.SetDirectory(0)

        for x in range(1, m_th2.GetXaxis().GetNbins() + 1):
            for y in range(1, m_th2.GetYaxis().GetNbins() + 1):
                
                content = m_th2.GetBinContent(x, y)
                error = m_th2.GetBinError(x, y)
                
                if args.axis == 'x':
                    m_th1.SetBinContent(y + (x - 1)*nBinsY, content)
                    m_th1.SetBinError(y + (x - 1)*nBinsY, error)
                
                if args.axis == 'y':
                    m_th1.SetBinContent(x + (y - 1)*nBinsX, content)
                    m_th1.SetBinError(x + (y - 1)*nBinsX, error)

        outputTH1s.append(m_th1)

    # Re-open the file in write mode
    f.Close()
    f = ROOT.TFile.Open(input, "update")

    for m_th1 in outputTH1s: 
        m_th1.Write('', ROOT.TObject.kOverwrite)

    f.Close()





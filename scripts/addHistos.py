#! /usr/bin/env python

import ROOT as R
import argparse
import imp
import os.path as op
import re


def parseArguments():
    parser = argparse.ArgumentParser(description="Add all histograms matching a regexp.")
    parser.add_argument("-i", "--input", type=str, dest="input", help="Input file", required=True)
    parser.add_argument("-o", "--output", type=str, dest="output", help="Output file", required=True)
    parser.add_argument("-c", "--config", type=str, dest="config", help="Config file", required=True)
    return parser.parse_args()


def checkUserInput(path):
    if not op.isfile(path):
        raise Exception("File {} does not exist.".format(path))

def checkUserOutput(path):
    dir = op.dirname(path)
    if not op.isdir(dir) and dir != "":
        raise Exception("Directory {} does not exist.".format(dir))
    if op.isfile(path):
        raise Exception("File {} already exists.".format(path))


if __name__ == "__main__":
    options = parseArguments()

    checkUserInput(options.input)
    checkUserOutput(options.output)
    checkUserInput(options.config)
    
    cfgMod = imp.load_source("cfgMod", options.config)

    inFile = R.TFile.Open(options.input)
    if inFile.IsOpen():
        print "Successfully opened {}.\n".format(options.input)
    else:
        raise Exception("Could not open {}.".format(options.input))
    
    # Retrieve all histograms from file
   
    print "Retrieving file content.\n"
    
    content = inFile.GetListOfKeys()
    listHistos = {}
    for item in content:
        gotItem = item.ReadObj()
        if gotItem.InheritsFrom("TH1"):
            listHistos[gotItem.GetName()] = gotItem
   
    # Match and add the histograms
    
    addedHistos = []
   
    print "Parsing regular expressions.\n"

    for item in cfgMod.toJoin:
        myRe = re.compile(item["match"])
        try:
            myReVeto = re.compile(item["veto"])
        except KeyError:
            myReVeto = None
        
        toAdd = []
        
        # Retrieve matching histograms
        
        for name, histo in listHistos.items():
            if myRe.match(name) is not None:
                if myReVeto is not None:
                    if myReVeto.match(name) is not None:
                        continue
                toAdd.append(histo)
        
        if not len(toAdd):
            print "Warning: regexp {} with veto {} could not be matched to any histogram inside the file.\n".format(item["match"], item["veto"])
            continue

        print "Histograms:"
        for histo in toAdd:
            print "\t- " + histo.GetName()
        print "Will be added to give {}.\n".format(item["newName"])

        # Add all selected histograms
        
        newHist = toAdd[0].Clone(item["newName"])
        for histo in toAdd[1:]:
            newHist.Add(histo)
        
        # Normalise if asked
        
        try:
            if item["normalise"]:
                newHist.Scale(1/newHist.Integral())
        except (KeyError, ZeroDivisionError) as exc:
            pass
        
        addedHistos.append(newHist)

    # Write resulting histograms to file
   
    print "Writing combined histograms to {}.\n".format(options.output)
    outFile = R.TFile(options.output, "recreate")
    for histo in addedHistos:
        histo.Write()
    outFile.Close()

    inFile.Close()

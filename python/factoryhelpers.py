"""
Helper methods shared between histFactory and treeFactory
"""

import logging
logger = logging.getLogger(__name__)

import os.path

from . import pathCommonTools
TEMPLATE_DIR = os.path.join(pathCommonTools, "templates")
def getTemplate(templName):
    return os.path.join(TEMPLATE_DIR, "{0}.tpl".format(templName))
COMMON_DIR = os.path.join(pathCommonTools, "common")
COMMON_INCLUDE_DIR = os.path.join(COMMON_DIR, "include")
COMMON_SRC_DIR = os.path.join(COMMON_DIR, "src")

################################################################################
## TEMPLATE EXPANSION                                                         ##
################################################################################

def expandTemplateLines(inFileName, **replacements):
    """ Generator: lines with replacements """
    fmtReplacements = dict(("{{{{{0}}}}}".format(fro), to) for fro,to in replacements.iteritems())
    with open(inFileName, "r") as inFile:
        for line in inFile:
            myLn = line
            for fro,to in fmtReplacements.iteritems():
                myLn = myLn.replace(fro, to)
                if "{{" not in myLn:
                    break ## stop searching
            yield myLn ## could also split by "\n" again
def expandTemplate(inFileName, **replacements):
    """ expand as a single string """
    return "".join(expandTemplateLines(inFileName, **replacements))
def expandTemplateAndWrite(outFileName, inFileName, **replacements):
    """ expand and write to file """
    with open(outFileName, "w") as outFile:
        outFile.writelines(expandTemplateLines(inFileName, **replacements))


## other helpers
def getBranchType(name, skeleton):
    ## TODO plots should contain expressions not callables, and leafDeps should return the type as well
    ## then this method disappears (code is in ttWdeco already), expressions compiled when creating the plot
    ## and createPlotter does not even need a skeleton any more
    ibr = next(br for br in skeleton.GetListOfBranches() if br.GetName() == name)
    clNm = ibr.GetClassName()
    if len(clNm) > 0:
        return clNm
    else:
        lf = skeleton.GetLeaf(ibr.GetName())
        if not lf:
            logger.error("Can't deduce type for branch '{0}'".format(ibr.GetName()))
        else:
            return lf.GetTypeName()

import os
from contextlib import contextmanager

@contextmanager
def insideOtherDirectory(path):
    prevDir = os.getcwd()
    os.chdir(path)
    assert os.getcwd() != prevDir
    yield
    os.chdir(prevDir)

def getARootFileName(jsonName):
    """
    Get any file from the json files field
    """
    return next(fn for sampDict in loadSamples(jsonName).itervalues() for fn in sampDict["files"])

def loadSamples(jsonName):
    """
    Load all samples from the json file

    """
    import json
    with open(jsonName, "r") as sampFile:
        samples = json.load(sampFile)
    return samples

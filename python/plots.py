"""
Helper classes describing histograms, binnings etc.
"""
__all__ = ("Plot", "EquidistantBinning", "VariableBinning")

import numpy as np
from itertools import chain

class EquidistantBinning(object):
    """ Equidistant binning
    """
    __slots__ = ("__weakref__", "N", "mn", "mx")
    def __init__(self, N, mn, mx):
        self.N = N
        self.mn = mn
        self.mx = mx
    @property
    def minimum(self):
        return self.mn
    @property
    def maximum(self):
        return self.mx

class VariableBinning(object):
    """ Variable-sized bins
    """
    __slots__ = ("__weakref__", "binEdges")
    def __init__(self, binEdges):
        self.binEdges = np.array(binEdges)
    @property
    def N(self):
        return len(self.binEdges)-1
    @property
    def minimum(self):
        return self.binEdges[0]
    @property
    def maximum(self):
        return self.binEdges[-1]

from .treedecorators import adaptArg

class Plot(object):
    """ Plot representation (specifications for making a 1,2,3,...-dimensional histogram)
    """
    __slots__ = ("__weakref__", "name", "variables", "selection", "binnings", "title", "axisTitles", "axisBinLabels", "plotopts")
    def __init__(self, name, variables, selection, binnings, title="", axisTitles=tuple(), axisBinLabels=tuple(), plotopts=None):
        self.name = name
        self.variables = variables
        self.selection = selection
        self.binnings = binnings
        self.title = title
        self.axisTitles = axisTitles
        self.axisBinLabels = axisBinLabels
        self.plotopts = plotopts if plotopts else dict()
    def clone(self, name=None, variables=None, selection=None, binnings=None, title=None, axisTitles=None, axisBinLabels=None, plotopts=None):
        """ Low-level helper method: copy with optional re-setting of attributes
        """
        return Plot( (name if name is not None else self.name)
                   , (variables if variables is not None else self.variables)
                   , (selection if selection is not None else self.selection)
                   , (binnings if binnings is not None else self.binnings)
                   , title=(title if title is not None else self.title)
                   , axisTitles=(axisTitles if axisTitles is not None else self.axisTitles)
                   , axisBinLabels=(axisBinLabels if axisBinLabels is not None else self.axisBinLabels)
                   , plotopts=(plotopts if plotopts is not None else self.plotopts)
                   )

    @property
    def cut(self):
        return self.selection.cut
    @property
    def weight(self):
        return self.selection.weight

    @property
    def longTitle(self):
        return ";".join(chain([self.title], self.axisTitles))

    def __repr__(self):
        return "Plot({0!r}, {1!r}, {2!r}, {3!r}, title={4!r}, axisTitles={5!r})".format(self.name, self.variables, self.selection, self.binnings, self.title, self.axisTitles)

    @staticmethod
    def make1D(name, variable, selection, binning, **kwargs):
        kwargs["axisTitles"] = (kwargs.pop("xTitle", ""),)
        kwargs["axisBinLabels"] = (kwargs.pop("xBinLabels", None),)
        return Plot(name, (adaptArg(variable),), selection, (binning,), **kwargs)
    @staticmethod
    def make2D(name, variables, selection, binnings, **kwargs):
        kwargs["axisTitles"] = (kwargs.pop("xTitle", ""), kwargs.pop("yTitle", ""))
        kwargs["axisBinLabels"] = (kwargs.pop("xBinLabels", None), kwargs.pop("yBinLabels", None))
        return Plot(name, tuple(adaptArg(v) for v in variables), selection, binnings, **kwargs)
    @staticmethod
    def make3D(name, variables, selection, binnings, **kwargs):
        kwargs["axisTitles"] = (kwargs.pop("xTitle", ""), kwargs.pop("yTitle", ""), kwargs.pop("zTitle", ""))
        kwargs["axisBinLabels"] = (kwargs.pop("xBinLabels", None), kwargs.pop("yBinLabels", None), kwargs.pop("zBinLabels", None))
        return Plot(name, tuple(adaptArg(v) for v in variables), selection, binnings, **kwargs)

class Selection(object):
    """ Group of selection requirements, weight factors and a handle on the candidate (they logically belong together)
    """
    __slots__ = ("__weakref__", "cuts", "weights", "candidate", "systVars")
    def __init__(self, cuts, weights, candidate):
        self.cuts      = [ adaptArg(cut, "Bool_t") for cut in list(cuts) ]
        self.weights   = [ adaptArg(wgt, "Float_t") for wgt in list(weights) ]
        self.candidate = candidate
        self.systVars  = dict()
    def clone(self, cuts=None, weights=None, candidate=None):
        """ Low-level helper method: copy with optional re-setting of attributes
        """
        return Selection( (cuts if cuts is not None else self.cuts)
                        , (weights if weights is not None else self.weights)
                        , (candidate if candidate is not None else self.candidate)
                        )
    @property
    def cut(self):
        from .treedecorators import makeExprAnd
        return makeExprAnd(self.cuts)
    @property
    def weight(self):
        from .treedecorators import makeExprProduct
        return makeExprProduct(self.weights)
    def __repr__(self):
        return "Selection({0!r}, {1!r}, {2!r})".format(self.cut, self.weight, self.candidate)
    def __eq__(self, other):
        return ( ( len(self.cuts) == len(other.cuts) ) and all( sc == oc for sc,oc in izip(self.cuts, other.cuts) )
             and ( len(self.weights) == len(other.weights) ) and all( sw == ow for sw,ow in izip(self.weights, other.weights) )
             and ( self.candidate == other.candidate ) )

    @staticmethod
    def addTo(prev, cut=None, weight=None, candidate=None):
        """
        Create a new selection by adding a cut and/or weight, and possibly replacing the candidate
        """
        newCuts = list(prev.cuts)
        if cut is not None:
            if hasattr(cut, "__len__"):
                newCuts += list(adaptArg(ct, "Bool_t") for ct in cut)
            else:
                newCuts.append(adaptArg(cut, "Bool_t"))
        newWeights = list(prev.weights)
        if weight is not None:
            if hasattr(weight, "__len__"):
                newWeights += list(adaptArg(wgt, "Float_t") for wgt in weight)
            else:
                newWeights.append(adaptArg(weight, "Float_t"))
        return Selection(newCuts, newWeights, candidate if candidate is not None else prev.candidate)

    ## TODO add more helpers for manipulation

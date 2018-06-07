"""
histfactory opt2v2 (complete tree of cuts, precalculation etc.) helper code
"""

from .treedecorators import allArgsOfOp, opDependsOn

class NodeTreeNeedsOpCache(object):
    """ Store nodes that depend on the operator to save time
    """
    def __init__(self, op):
        self.depends = set()
        self.notDepends = set()
        self.op = op
    def __call__(self, aNode):
        if aNode in self.depends:
            return True
        elif aNode in self.notDepends:
            return False
        else:
            ret = aNode.treeNeedsOp_cache(self)
            if ret:
                self.depends.add(aNode)
            else:
                self.notDepends.add(aNode)
            return ret

class IDTNode(object):
    """ Interface for a node in the dependency tree
    """
    __slots__ = ("__weakref__", "_parent")
    def __init__(self, parent=None):
        self._parent = parent
    @property
    def depNodes(self):
        pass
    @property
    def isTerminal(self):
        return False
    @property
    def parent(self):
        return self._parent
    @parent.setter
    def parent(self, parent):
        self._parent = parent
    def clone(self):
        """
        Clone this node (without dependencies)
        """
        pass
    def ownDbgStr(self):
        pass
    def treeNeedsOp(self, op):
        pass
    def treeNeedsOp_cache(self, cache):
        return self.treeNeedsOp(cache.op) ## default: don't use the cache

class PlotNode(IDTNode):
    """ Plot (terminal) node
    """
    __slots__ = ("plot",)
    def __init__(self, plot, parent=None):
        self.plot = plot
        super(PlotNode, self).__init__(parent=parent)
    @property
    def isTerminal(self):
        return True
    @property
    def depNodes(self):
        return tuple()
    def clone(self):
        return PlotNode(self.plot, parent=self.parent)
    def ownDbgStr(self): ## for reasonably compact debug printing
        return "PlotNode(( {0} ), {1})".format(", ".join(v.get_TTreeDrawStr() for v in self.plot.variables), self.plot.selection.weight.get_TTreeDrawStr())
    def treeNeedsOp(self, op):
        return opDependsOn(self.plot.weight, op) or any(opDependsOn(var, op) for var in self.plot.variables)

class DTNode(IDTNode):
    """ Selection or reduce (non-terminal) node
    """
    __slots__ = ("_deps",)
    def __init__(self, parent=None, deps=None):
        if deps is None:
            deps = []
        self._deps = deps
        super(DTNode, self).__init__(parent=parent)
    def addDependentNode(self, nd):
        self._deps.append(nd)
    def removeDependentNode(self, nd):
        self._deps.remove(nd)
    @property
    def depNodes(self):
        return self._deps
    @property
    def isTerminal(self):
        return False
    def treeNeedsOp(self, op):
        return any( nd.treeNeedsOp(op) for nd in self.depNodes )
    def treeNeedsOp_cache(self, cache):
        return any( cache(nd) for nd in self.depNodes )

class RootNode(DTNode):
    """ Special case: root node (no parent by definition, only holds deps list)
    """
    __slots__ = ()
    def __init__(self, deps=None):
        super(RootNode, self).__init__(parent=None, deps=deps)
    def ownDbgStr(self):
        return "/"

class SelectionNode(DTNode):
    """ Selection node (cuts list and dependencies)
    """
    __slots__ = ("cuts",)
    def __init__(self, cuts, parent=None, deps=None):
        self.cuts = cuts
        super(SelectionNode, self).__init__(parent=parent, deps=deps)
    def clone(self):
        return SelectionNode(self.cuts, parent=self.parent, deps=self._deps)
    def aboveSel(self):
        ## return the first SelectionNode in the ancestor tree (or None)
        cand = self.parent
        while cand and not isinstance(cand, SelectionNode):
            cand = cand.parent
        return cand
    @property
    def ownCuts(self):
        parSel = self.aboveSel()
        if not parSel:
            return self.cuts
        else:
            return tuple(c for c in self.cuts if c not in parSel.cuts)
    def ownDbgStr(self): ## for reasonably compact debug printing
        from .treedecorators import makeExprAnd
        return "SelectionNode({0}) with {1:d} dependent nodes".format(makeExprAnd(self.ownCuts).get_TTreeDrawStr(), len(self._deps))
    def treeNeedsOp(self, op):
        return any( opDependsOn(ci, op) for ci in self.cuts ) or super(SelectionNode, self).treeNeedsOp(op)
    def treeNeedsOp_cache(self, cache):
        return any( opDependsOn(ci, cache.op) for ci in self.cuts ) or super(SelectionNode, self).treeNeedsOp_cache(cache)

class PrecalcNode(DTNode):
    """ Precalculation node (expression and dependencies)
    """
    __slots__ = ("op",)
    def __init__(self, op, parent=None, deps=None):
        self.op = op
        super(PrecalcNode, self).__init__(parent=parent, deps=deps)
    def clone(self):
        return PrecalcNode(self.op, parent=self.parent, deps=self._deps)
    def ownDbgStr(self): ## for reasonably compact debug printing
        return "PrecalcNode({0}={1}) with {2:d} dependent nodes".format(self.op.uname, self.op._get_TTreeDrawStr(), len(self._deps))
    def treeNeedsOp(self, op):
        return opDependsOn(self.op, op) or super(PrecalcNode, self).treeNeedsOp(op)
    def treeNeedsOp_cache(self, cache):
        return opDependsOn(self.op, cache.op) or super(PrecalcNode, self).treeNeedsOp_cache(cache)

class SkimmerFillBranchesNode(IDTNode):
    __slots__ = ("branches", "fill_tree_lines")
    def __init__(self, branches, parent=None, fill_tree_lines=None):
        self.branches = branches
        self.fill_tree_lines = fill_tree_lines
        super(SkimmerFillBranchesNode, self).__init__(parent=parent)
    @property
    def isTerminal(self):
        return True
    @property
    def depNodes(self):
        return tuple()
    def clone(self):
        return SkimmerFillBranchesNode(self.branches, parent=self.parent, fill_tree_lines=self.fill_tree_lines)
    def ownDbgStr(self):
        return "SkimmerFillBranchesNode(...)"
    def treeNeedsOp(self, op):
        return any(opDependsOn(var, op) for nm,var,unm in self.branches)


def printTree(nd, indent=0):
    ## helper to (recursively) print a tree
    yield (indent*"  ")+nd.ownDbgStr()
    nPlots = sum( 1 for dep in nd.depNodes if isinstance(dep, PlotNode) )
    yield ((indent+1)*"  ")+"{0:d} plots".format(nPlots)
    for dep in nd.depNodes:
        if not isinstance(dep, PlotNode):
            for ln in printTree(dep, indent=indent+1):
                yield ln

"""
Generate C++ code to fill the histos, with helpers to run it
"""
__all__ = ("createPlotter", "compilePlotter", "runPlotterOnSamples")

import logging
logger = logging.getLogger(__name__)

from itertools import izip, count, chain, groupby

from .factoryhelpers import getTemplate, expandTemplate, expandTemplateAndWrite, getBranchType, insideOtherDirectory
from .plots import *

def collectIdentifiersFromPlots(plots):
    identifiers = set()
    for i,plot in izip(count(1), plots):
        if i % 200 == 0:
            print "Parsing plot #{0:d}/{1:d}".format(i,len(plots))
        try:
            identifiers.update(plot.cut.leafDeps)
        except Exception, e:
            logger.error("Problem parsing cut of plot {0} : {1}".format(plot.name, str(e)))
        try:
            identifiers.update(plot.weight.leafDeps)
        except Exception, e:
            logger.error("Problem parsing weight of plot {0} : {1}".format(plot.name, str(e)))
        for j,sVar in izip(count(), plot.variables):
            try:
                identifiers.update(sVar.leafDeps)
            except Exception, e:
                logger.error("Problem parsing sVar of plot {0} : {1}".format(plot.name, str(e)))
    return identifiers


def getHistType(plot):
    assert len(plot.variables) == len(plot.binnings) and len(plot.variables) == len(plot.axisTitles)
    if len(plot.variables) == 1:
        return "TH1F"
    elif len(plot.variables) == 2:
        return "TH2F"
    elif len(plot.variables) == 3:
        return "TH3F"
    else:
        raise Exception("Invalid number of dimensions")

def getBinningDefinitions(plot, uname):
    decls = []
    for idx,bn in izip(count(), plot.binnings):
        if   isinstance(bn, EquidistantBinning):
            pass
        elif isinstance(bn, VariableBinning):
            arrNm = "{name}_{idx}".format(name=uname, idx=idx)
            decls.append("    double {name}[] = {{ {0} }};".format(", ".join("{0:e}".format(iEdg) for iEdg in bn.binEdges), name=arrNm))
        else:
            raise Exception("Unsupported binning: {0!r}".format(bn))
    return decls

def getBinningUses(plot, uname):
    uses = []
    for idx,bn in izip(count(), plot.binnings):
        if   isinstance(bn, EquidistantBinning):
            uses.append("{0:d}, {1:e}, {2:e}".format(bn.N, bn.mn, bn.mx))
        elif isinstance(bn, VariableBinning):
            arrNm = "{name}_{idx}".format(name=uname, idx=idx)
            uses.append("{0:d}, &({name}[0])".format(len(bn.binEdges)-1, name=arrNm))
        else:
            raise Exception("Unsupported binning: {0!r}".format(bn))
    return ", ".join(uses)

def getOtherHistSettings(plot, uname):
    outLines = []
    ## set bin labels if necessary
    ## x-axis
    if len(plot.axisBinLabels) > 0 and plot.axisBinLabels[0] is not None:
        axisBinLabels = plot.axisBinLabels[0]
        if len(axisBinLabels) == plot.binnings[0].N:
            outLines.append("    {0}".format(" ".join("{hn}->GetXaxis()->SetBinLabel({idx:d}, \"{iLabel}\");".format(hn=uname, idx=i, iLabel=lbl) for i,lbl in izip(count(1), axisBinLabels))))
        else:
            logger.error("Not the same number of x bins ({0:d}) and labels ({1:d}) -> not setting them".format(plot.binnings[0].N, len(axisBinLabels)))
    ## y-axis
    if len(plot.axisBinLabels) > 1 and plot.axisBinLabels[1] is not None:
        axisBinLabels = plot.axisBinLabels[1]
        if len(axisBinLabels) == plot.binnings[1].N:
            outLines.append("    {0}".format(" ".join("{hn}->GetYaxis()->SetBinLabel({idx:d}, \"{iLabel}\");".format(hn=uname, idx=i, iLabel=lbl) for i,lbl in izip(count(1), axisBinLabels))))
        else:
            logger.error("Not the same number of y bins ({0:d}) and labels ({1:d}) -> not setting them".format(plot.binnings[1].N, len(axisBinLabels)))
    ## z-axis
    if len(plot.axisBinLabels) > 2 and plot.axisBinLabels[2] is not None:
        axisBinLabels = plot.axisBinLabels[2]
        if len(axisBinLabels) == plot.binnings[2].N:
            outLines.append("    {0}".format(" ".join("{hn}->GetZaxis()->SetBinLabel({idx:d}, \"{iLabel}\");".format(hn=uname, idx=i, iLabel=lbl) for i,lbl in izip(count(1), axisBinLabels))))
        else:
            logger.error("Not the same number of z bins ({0:d}) and labels ({1:d}) -> not setting them".format(plot.binnings[2].N, len(axisBinLabels)))
    #
    return outLines

def createPlotsInnerLoop_ref(plots, uhNames):
    """
    Original (reference) implementation: evaluate selection, weight and value for each and every histogram
    """
    return "\n".join(
        expandTemplate(getTemplate("Plot")
            , CUT=plot.cut.get_TTreeDrawStr()
            , WEIGHT=plot.weight.get_TTreeDrawStr()
            , VAR=", ".join(v.get_TTreeDrawStr() for v in plot.variables)
            , HIST=uhNames[plot]
            ) for plot in plots
        )

def greedyGroupBy(inputs, keyFunc):
    """
    Greedy version of groupby
    """
    items = list(inputs)
    while len(items) > 0:
        idxs = set()
        val = keyFunc(items[0])
        idxs.add(0)
        thisGroup = [ items[0] ]
        for i,it in izip(count(1), items[1:]):
            if keyFunc(it) == val:
                idxs.add(i)
                thisGroup.append(it)
        yield val, thisGroup
        nBefore = len(items)
        items = [ it for i,it in izip(count(),items) if i not in idxs ]
        assert len(items)+len(thisGroup) == nBefore

def createPlotsInnerLoop_opt1(plots, uhNames, indent=2, alreadyReq=tuple()):
    """
    More optimised plotting loop - take 1: group by cut and weight
    """
    from .treedecorators import makeExprAnd
    return "\n".join((indent*"    ")+ln if len(ln) > 0 else ln for ln in chain.from_iterable(
        [ "__cut = ({0});".format(makeExprAnd([ct for ct in selGrpPlots[0].selection.cuts if ct not in alreadyReq]).get_TTreeDrawStr())
        , "if (__cut) {"
        ] + list("    {0}".format(ln) if len(ln) > 0 else ln for ln in chain.from_iterable(
            [ "__weight = ({0});".format(weight.get_TTreeDrawStr())
            ] + [ "fill({HIST}.get(), {VAR}, __weight);".format(HIST=uhNames[plot], VAR=", ".join(v.get_TTreeDrawStr() for v in plot.variables))
                for plot in wgtGrpPlots
            ] for weight,wgtGrpPlots in greedyGroupBy(selGrpPlots, lambda ip : ip.weight) )) +
        [ "}"
        , ""
        ] for ct,selGrpPlots in greedyGroupBy(plots, lambda ip : ip.cut)
        ))

from .treedecorators import allArgsOfOp, opDependsOn

def plotDependsOn(pt, other):
    return any(opDependsOn(ct, other) for ct in pt.selection.cuts) or any(opDependsOn(wt, other) for wt in pt.selection.weights) or any(opDependsOn(var, other) for var in pt.variables)

def iunique(otherGen):
    """ Remove duplicates from another generator
    """
    alreadyReturned = set()
    for elm in otherGen:
        if elm not in alreadyReturned:
            yield elm
            alreadyReturned.add(elm)

def collectReduces(listOfPlots):
    from .treedecorators import TupleOp, Reduce, Next
    import uuid
    def _addReduces(depDict, op, abovePlotOrReduce):
        ## the one to be used for recursion
        if isinstance(op, TupleOp):
            top = abovePlotOrReduce
            if ( isinstance(op, Reduce) or isinstance(op, Next) ):
                if op not in depDict:
                    depDict[op] = ("r_{0}".format(str(uuid.uuid4()).replace("-", "_")), set())
                    assert op.uname is None
                uname, deps = depDict[op]
                op.uname = uname
                deps.add(top)
                top = op ## build a dependency tree
            for ia in op.args:
                _addReduces(depDict, ia, top)
        else:
            raise Exception("_addReduces called on {0!r}, which is not a TupleOp but a {1}".format(op, op.__class__.__name__))

    depDict = dict()
    for plot in listOfPlots:
        for var in chain((plot.cut, plot.weight), plot.variables):
            _addReduces(depDict, var, plot)
    return depDict ## { op : (uname, depPlotsAndOps) } ## only for reduce opts

def removeReduceUnames(listOfPlots):
    # mirror of the above: clean up afterwards
    from .treedecorators import TupleOp, Reduce, Next
    def _clearReduces(op):
        ## recurse
        if isinstance(op, TupleOp):
            if ( isinstance(op, Reduce) or isinstance(op, Next) ):
                op.uname = None
            for ia in op.args:
                _clearReduces(ia)
        else:
            raise Exception("_clearReduces called on {0!r}, which is not a TupleOp but a {1}".format(op, op.__class__.__name__))
    for plot in listOfPlots:
        for var in chain((plot.cut, plot.weight), plot.variables):
            _clearReduces(var)

def collectPrecalc(listOfPlots):
    from .treedecorators import TupleOp
    def _addPrecalc(depDict, op, abovePlotOrPrecalc):
        ## the one to be used for recursion
        if isinstance(op, TupleOp):
            top = abovePlotOrPrecalc
            if op.uname is not None:
                if op not in depDict:
                    depDict[op] = (op.uname, set())
                uname, deps = depDict[op]
                op.uname = uname ## keep to make sure they get renamed to the same
                deps.add(top)
                top = op ## build a dependency tree
            for ia in op.args:
                _addPrecalc(depDict, ia, top)
        else:
            raise Exception("_addPrecalc called on {0!r}, which is not a TupleOp but a {1}".format(op, op.__class__.__name__))

    depDict = dict()
    for plot in listOfPlots:
        for var in chain((plot.cut, plot.weight), plot.variables):
            _addPrecalc(depDict, var, plot)
    return depDict ## { op : (uname, depPlotsAndOps) } ## only for precalc ops


def commonConditionForAll(somePlots):
    """ find common condition for all plots in the list (allows to move selection before reduce)
    """
    inCommon = []
    notInAll = set() ## caching to avoid too much double work
    for ap in somePlots:
        for cdc in ap.selection.cuts:
            if cdc not in inCommon and cdc not in notInAll:
                if all( cdc in op.selection.cuts for op in somePlots ):
                    inCommon.append(cdc)
                else:
                    notInAll.add(cdc)
    return inCommon

def createPlotsInnerLoop_opt2(plots, uhNames, indent=2):
    """
    Second optimisation round: pre-calculate "expensive" reduce operations
    """
    from .plots import Plot
    reducesWithAllDeps = collectReduces(plots)
    ## 1: not to be forgotten: plots that don't depend on these (keep this simple for now)
    plotLines_noDeps = createPlotsInnerLoop_opt1([ p for p in plots if all( p not in depList for uN,depList in reducesWithAllDeps.itervalues() ) ], uhNames, indent=indent)

    ## make minimal (real reduce+plot-dependency tree)
    reducesWithMinDeps = dict((redOp, (uname,
        [ di for di in deps if not any( ( plotDependsOn(di, do) if isinstance(di, Plot) else opDependsOn(di, do) ) for do in deps if ( not isinstance(do, Plot) ) and ( do != di ) ) ]))
        ## if you depend on another dependee, you need to be further downstream
        ## top-down traversal strategy: always take the next key that is not in any list of dependees (shallow copy then pop)
        for redOp,(uname, deps) in reducesWithAllDeps.iteritems())

    ## temporary solution: put in the right order (leave out-of-bounds to selection)
    def getLinesForRedsAndPlotsDepTreeTopDown(myMinDepDict, indent=0, alreadyReq=tuple()):
        ##print (indent*"  ")+"getLinesForRedsAndPlotsDepTreeTopDown called with {0:d} already required selections".format(len(alreadyReq))
        ##print (indent*"  ")+"Treating plots: ", ", ".join(p.name for p in set(di for r,(u,ds) in myMinDepDict.iteritems() for di in ds if isinstance(di, Plot)))
        ##
        while len(myMinDepDict) > 0:
            redsToTreat = sorted([ k for k,v in myMinDepDict.iteritems() if not any(k in od for ou,od in myMinDepDict.itervalues()) ], key=(lambda k : len(myMinDepDict[k][1])), reverse=True)
            if len(redsToTreat) == 0:
                print "ERROR: also the operators have multiple sibling dependencies -> not handled yet"; break
            ##print (indent*"  ")+"--> Adding reduces in this loop:"
            ##for redOp in redsToTreat:
            ##    print (indent*"  ")+" - ", redOp._get_TTreeDrawStr()

            for redOp in redsToTreat:
                if redOp in myMinDepDict:
                    uName,deps = myMinDepDict[redOp]
                    #
                    commonCuts = [ ct for ct in commonConditionForAll(list(di for di in reducesWithAllDeps[redOp][1] if isinstance(di, Plot))) ]
                    commonCuts_apply = [ ct for ct in commonCuts if ct not in alreadyReq ]
                    commonCuts_applyBefore, commonCuts_applyAfter = [], []
                    for ct in commonCuts_apply:
                        if opDependsOn(ct, redOp):
                            commonCuts_applyAfter.append(ct)
                        else:
                            commonCuts_applyBefore.append(ct)
                    #
                    if len(commonCuts_applyBefore) > 0:
                        from .treedecorators import makeExprAnd
                        yield (indent*"    ")+"if ( {0} ) {{".format(makeExprAnd(commonCuts_applyBefore).get_TTreeDrawStr())
                    else:
                        yield (indent*"    ")+"{"
                    #
                    yield ((indent+1)*"    ")+"const auto {0} = {1};".format(uName, redOp._get_TTreeDrawStr())
                    #
                    if len(commonCuts_applyAfter) > 0:
                        from .treedecorators import makeExprAnd
                        yield ((indent+1)*"    ")+"if ( {0} ) {{".format(makeExprAnd(commonCuts_applyAfter).get_TTreeDrawStr())
                    else:
                        yield ((indent+1)*"    ")+"{"
                    #

                    req_uptohere = list(alreadyReq)+commonCuts_apply
                    ###print "Making block - already applied: ", req_uptohere
                    #
                    ### find those that depend on (not interdependent) reduce ops - this kind of reordering is not handled yet
                    otherDeps = set()
                    for di in deps:
                        if isinstance(di, Plot):
                            for oro,(ouN,odeps) in myMinDepDict.iteritems():
                                if oro != redOp and di in odeps:
                                    otherDeps.add(oro)
                                    odeps.remove(di)
                    for oro in otherDeps:
                        (ouN,odeps) = myMinDepDict[oro]
                        yield ((indent+2)*"    ")+"const auto {0} = {1};".format(ouN, oro._get_TTreeDrawStr())
                        ## clean up: if we got all the dependencies, it's time to clean up
                        if len(odeps) == 0:
                            del myMinDepDict[oro]
                    ###
                    ## NOTE the bookkeeping of this part is actually done above
                    ##print (indent*"  ")+"Passing plots to createPlotsInnerloop_opt1: ", ", ".join(di.name for di in deps if isinstance(di, Plot))
                    for ln in createPlotsInnerLoop_opt1([ di for di in deps if isinstance(di, Plot) ], uhNames, indent=indent+2, alreadyReq=req_uptohere).split("\n"):
                        yield ln
                        ## can forget about dependant reduces (at this stage) they won't appear any more after this and can be handled next
                        ## more interesting case: C depends on A and B, D only on A, E only on B - how will they be ordered if you do everything nicely in blocks?
                    ##
                    ###del myMinDepDict[redOp] ## keep simple like this for now (other option: pass context to the same algo for the next layer)
                    # RECURSE
                    sub_depDict = dict((k,v) for k,v in myMinDepDict.iteritems() if k in reducesWithAllDeps[redOp][1]) ## -> straight down to the next level
                    cp_depDict = dict(sub_depDict)
                    for ln in getLinesForRedsAndPlotsDepTreeTopDown(cp_depDict, indent=indent+2, alreadyReq=req_uptohere):
                        yield ln
                    #
                    yield ((indent+1)*"    ")+"}" ## inner block
                    #
                    yield (indent*"    ")+"}" ## outer block
                    #
                    for k in sub_depDict: ## remove handled deps
                        if k not in cp_depDict:
                            del myMinDepDict[k]
            #
            for redOp in redsToTreat:
                if redOp in myMinDepDict:
                    del myMinDepDict[redOp]

    ## 2. handle these as well
    plotLines_redsWithPlots = list(getLinesForRedsAndPlotsDepTreeTopDown(dict(reducesWithMinDeps), indent=2))
    #import IPython;IPython.embed()

    ## clean up
    removeReduceUnames(plots)

    return "\n".join((plotLines_noDeps, "\n".join(plotLines_redsWithPlots)))

def createPlotsInnerLoop_opt2v2(plots, uhNames, indent=2):
    """
    Second attempt: keep track of things in a bit more organised way

    Build up a tree of Plots and non-terminal nodes (selections and reduces)
    """
    from .hist_opt_2v2 import RootNode, SelectionNode, PrecalcNode, PlotNode, printTree, NodeTreeNeedsOpCache

    reducesWithAllDeps = collectPrecalc(plots)
    reducesWithAllDeps.update(collectReduces(plots)) # { op : (uname, depPlotsAndOps) } ## TODO to be changed - but without the unames the rest is unreadable

    def nCommonCuts_cons(listA, listB):
        for i,iA,iB in izip(count(), listA, listB):
            if iA != iB:
                break
        return i+(1 if iA == iB else 0)
    def commonCuts_cons(listA, listB):
        result = []
        for iA,iB in izip(listA, listB):
            if iA != iB:
                break
            else:
                result.append(iA)
        return result

    logger.info("Ordering selections and plots")
    from itertools import imap
    rootNode = RootNode()
    ## start with selections
    for ap in plots:
        #print "\n\nAdding plot {0} with selection of {1:d} cuts\n".format(ap.name, len(ap.selection.cuts))
        prevSelNode = rootNode
        prevNCommon = 0
        selNode = rootNode
        toSearch = rootNode.depNodes
        #while sum(1 for sn in toSearch if isinstance(sn, SelectionNode)) > 0:
        while True:
            prevSelNode = selNode
            if len(toSearch) > 0 and any(isinstance(nd, SelectionNode) for nd in toSearch):
                selNode,nCommon = max(imap(lambda nd : ( (nd,nCommonCuts_cons(ap.selection.cuts, nd.cuts)) if isinstance(nd, SelectionNode) else (nd,0) ), toSearch), key=lambda (nd,n) : n)
            else:
                selNode,nCommon = None,0
            if selNode and nCommon == len(selNode.cuts):
                if nCommon == len(ap.selection.cuts):
                    #print "Found fully matching selection node"
                    break
                else:
                    if any(isinstance(sn, SelectionNode) for sn in toSearch):
                        #print "Found fully required selection node, going deeper..."
                        toSearch = selNode.depNodes ## next iteration
                        prevNCommon = nCommon
                    else:
                        #print "Found fully required selection node without selections, adding here"
                        newSelNode = SelectionNode(cuts=ap.selection.cuts, parent=selNode)
                        selNode.addDependentNode(newSelNode)
                        selNode = newSelNode
                        break
            elif nCommon > prevNCommon:
                #print "Not fully matching, but common part ({0:d} - versus {1:d} in our selection and {2:d} in best match) -> splitting".format(nCommon, len(ap.selection.cuts), len(selNode.cuts))
                newSel = SelectionNode(cuts=( ap.selection.cuts if nCommon == len(ap.selection.cuts) else commonCuts_cons(ap.selection.cuts, selNode.cuts)), parent=prevSelNode)
                prevSelNode.addDependentNode(newSel)
                prevSelNode.removeDependentNode(selNode)
                selNode.parent = newSel
                newSel.addDependentNode(selNode)
                if nCommon == len(ap.selection.cuts):
                    #print "Adding plot to split node"
                    selNode = newSel
                else:
                    #print "Adding one with our selection"
                    selNode = SelectionNode(cuts=ap.selection.cuts, parent=newSel)
                    newSel.addDependentNode(selNode)
                break
            else:
                #print "Nothing more in common, adding one level higher"
                if len(ap.selection.cuts) > prevNCommon:
                    #print "With selection"
                    selNode = SelectionNode(cuts=ap.selection.cuts, parent=prevSelNode)
                    prevSelNode.addDependentNode(selNode)
                else:
                    #print "Without selection"
                    selNode = prevSelNode
                break
        selNode.addDependentNode(PlotNode(ap, parent=selNode))

    # print "\n\nTree after adding all plot:"
    # ## how does our tree look at this point?
    # for ln in printTree(rootNode):
    #     print ln

    logger.info("Inserting pre-calculated variables")
    ## make minimal (real reduce+plot-dependency tree)
    reducesWithMinDeps = dict((redOp, (uname,
        [ di for di in deps if not any( ( plotDependsOn(di, do) if isinstance(di, Plot) else opDependsOn(di, do) ) for do in deps if ( not isinstance(do, Plot) ) and ( do != di ) ) ]))
        for redOp,(uname, deps) in reducesWithAllDeps.iteritems())

    ## collect weights
    import uuid
    uwNames = dict()
    for ap in plots:
        wOp = ap.selection.weight
        if wOp not in uwNames:
            uname = "w_{0}".format(str(uuid.uuid4()).replace("-", "_"))
            wOp.uname = uname
            uwNames[wOp] = (uname, [ ap ])
        else:
            uwNames[wOp][1].append(ap)

    reducesWithAllDeps.update(uwNames) ## yes that's a bit of a workaround...
    reducesWithMinDeps.update(uwNames)

    logger.debug("Collected pre-calc expressions to insert, found {0:d}".format(len(reducesWithMinDeps)))

    while len(reducesWithMinDeps) > 0:
        redsToTreat = sorted([ k for k,v in reducesWithMinDeps.iteritems() if not any(k in od for ou,od in reducesWithMinDeps.itervalues()) ], key=(lambda k : len(reducesWithMinDeps[k][1])), reverse=True)
        logger.debug("Reduces to treat in this round: {0:d}".format(len(redsToTreat)))
        for redOp in redsToTreat:
            #nodeTreeNeedsOp = ( lambda op : ( lambda nd : nd.treeNeedsOp(redOp) ) )(redOp)
            nodeTreeNeedsOp = NodeTreeNeedsOpCache(redOp)
            logger.debug("Inserting reduce {0}".format(redOp._get_TTreeDrawStr()))
            ## FIXME following line isn't used?
            redCuts = [ ct for ct in commonConditionForAll(list(di for di in reducesWithAllDeps[redOp][1] if isinstance(di, Plot))) ]
            cand = rootNode
            while True:
                if ( isinstance(cand, PrecalcNode) and opDependsOn(cand.op, redOp) ) or ( isinstance(cand, SelectionNode) and any( opDependsOn(ci, redOp) for ci in cand.cuts ) ):
                    ## TODO split the selection node if only some depend - will need that when treating precalc deps as well
                    logger.debug("Candidate is precalc or selection node that depends on us -> insert above")
                    myNode = PrecalcNode(redOp, parent=cand.parent)
                    cand.parent.addDependentNode(myNode)
                    cand.parent.removeDependentNode(cand)
                    cand.parent = myNode
                    myNode.addDependentNode(cand)
                    break
                elif any(isinstance(nd, PlotNode) and nodeTreeNeedsOp(nd) for nd in cand.depNodes) or sum(1 for nd in cand.depNodes if nodeTreeNeedsOp(nd)) > 1:
                    ## TODO we should also check that our validity requirements are satisfied here, otherwise should go further
                    logger.debug("Candidate has a plot or several dependencies that depend on us -> insert below")
                    myNode = PrecalcNode(redOp, parent=cand)
                    for nd in cand.depNodes:
                        if nodeTreeNeedsOp(nd):
                            myNode.addDependentNode(nd)
                            nd.parent = myNode
                    for nd in myNode.depNodes:
                        cand.removeDependentNode(nd)
                    cand.addDependentNode(myNode)
                    break
                else: ## here is where things get interesting
                    if not any( nodeTreeNeedsOp(nd) for nd in cand.depNodes ):
                        print "Nothing depends on this operation... that's most likely wrong"
                        break ## this is a bit problematic
                    else:
                        cand = next(nd for nd in cand.depNodes if nodeTreeNeedsOp(nd))
                        logger.debug("Found one node that depends: {0}".format(cand.ownDbgStr()))
        for trtd in redsToTreat:
            del reducesWithMinDeps[trtd]

    # print "\n\nTree after adding all precalculated variables:"
    # ## how does our tree look at this point?
    # for ln in printTree(rootNode):
    #     print ln

    from .treedecorators import makeExprAnd
    indentStr = "    " ## 4 spaces
    def cppLines(someNode, indent=0):
        dindent = indent
        closeBlock = False
        if isinstance(someNode, SelectionNode):
            yield (indent*indentStr)+"if ( {0} ) {{".format(makeExprAnd(someNode.ownCuts).get_TTreeDrawStr())
            dindent = indent+1
            closeBlock = True
        elif isinstance(someNode, PrecalcNode):
            yield (indent*indentStr)+"const auto {0} = {1};".format(someNode.op.uname, someNode.op._get_TTreeDrawStr())
        elif isinstance(someNode, PlotNode):
            ## TODO check that all cuts have been applied here
            yield (indent*indentStr)+"fill({HIST}.get(), {VAR}, {WEIGHT});".format(
                      HIST=uhNames[someNode.plot]
                    , VAR=", ".join(v.get_TTreeDrawStr() for v in someNode.plot.variables)
                    , WEIGHT=uwNames[someNode.plot.selection.weight][0]
                    )
        if not someNode.isTerminal:
            ## first terminal nodes
            for dn in someNode.depNodes:
                if dn.isTerminal:
                    for ln in cppLines(dn, indent=dindent):
                        yield ln
            ## then dependency tree of the others
            for dn in someNode.depNodes:
                if not dn.isTerminal:
                    for ln in cppLines(dn, indent=dindent):
                        yield ln
        if closeBlock:
            yield (indent*indentStr)+"}"

    logger.info("Generating output")
    ret =  "\n".join(ln for ln in cppLines(rootNode, indent=2))

    ## clean up unames
    removeReduceUnames(plots)
    for wOp in uwNames.iterkeys():
        wOp.uname = None

    return ret

################################################################################
## MAIN METHOD                                                                ##
################################################################################

import os, os.path

def createPlotter(plots, skeleton, outdir=None, **kwargs):
    """
    Turned the config into the main script
    
    this is only a helper method that deals with creating a C++ plotter from it
    """
    if not outdir:
        outdir = os.getcwd()
        logger.warning("No output directory set, writing plotter code to current directory {0}".format(outdir))
    else:
        logger.info("Writing plotter code to output directory {0}".format(outdir))

    ## common forced helpers
    add_packages = list(kwargs.get("add_packages", []))
    include_dirs = list(kwargs.get("include_dirs", []))
    includes = list(kwargs.get("includes", []))
    sources = list(kwargs.get("sources", []))
    linked_libraries = list(kwargs.get("libraries", []))
    add_properties = []

    # add some defaults
    from .factoryhelpers import COMMON_INCLUDE_DIR
    include_dirs.append(os.path.join(COMMON_INCLUDE_DIR))
    includes.append("kinematics.h")
    includes.append("IndexRangeIterator.h")

    if kwargs.get("addScaleFactorsLib", False):
        from . import pathCommonTools
        pathCP3llbb = os.path.dirname(os.path.abspath(pathCommonTools))
        linked_libraries.append(os.path.join(pathCP3llbb, "Framework", "libBinnedValues.so"))
        include_dirs.append(os.path.join(pathCP3llbb, "Framework", "interface"))
        add_properties.append('set_target_properties(plotter PROPERTIES COMPILE_FLAGS "-DSTANDALONE_SCALEFACTORS")')

    logger.info("List of requested plots: {0}".format(", ".join(plot.name for plot in plots)))
    logger.info("List of requested include files: {0}".format(", ".join(inc for inc in includes)))
    logger.info("List of requested source files: {0}".format(", ".join(src for src in sources)))

    ### add systematic variations histos
    allPlots = list(plots)+list(chain.from_iterable( ( mplt.clone(name="__".join((mplt.name, varNm)), selection=varSel) for varNm,varSel in mplt.selection.systVars.iteritems() ) for mplt in plots ))

    import uuid
    unames = dict((plot, "p_{0}".format(str(uuid.uuid4()).replace("-", "_"))) for plot in allPlots)

    expandTemplateAndWrite(os.path.join(outdir, "Plotter.h"), getTemplate("Plotter.h")
            , BRANCHES="\n        ".join(
                'const {typ}& {name} = tree["{name}"].read<{typ}>();'.format(typ=getBranchType(brName, skeleton._skeleton), name=brName)
                for brName in collectIdentifiersFromPlots(allPlots))
            )

    expandTemplateAndWrite(os.path.join(outdir, "Plotter.cc"), getTemplate("Plotter.cc")
            , INCLUDES="\n".join('#include "{0}"'.format(incl) for incl in includes)
            , BEFORE_LOOP="\n".join(chain(
                ## declare histograms
                  chain.from_iterable(chain(
                        getBinningDefinitions(plot, unames[plot])
                      , [ '    std::unique_ptr<{typ}> {uname}(new {typ}("{uname}", "{title}", {binning})); {uname}->SetDirectory(nullptr);'.format(
                            typ=getHistType(plot), uname=unames[plot], title=plot.longTitle, binning=getBinningUses(plot, unames[plot])) ]
                      , getOtherHistSettings(plot, unames[plot])
                    ) for plot in allPlots)
                , ("    {0}".format(ln) for ln in list(kwargs.get("user_initialisation", [])))
                ))
            , IN_LOOP=createPlotsInnerLoop_opt2v2(allPlots, unames)
            , AFTER_LOOP="\n".join( ## save plots
                expandTemplate(getTemplate("SavePlot")
                    , UNIQUE_NAME=unames[plot]
                    , PLOT_NAME=plot.name
                    ) for plot in allPlots
                )
            )

    expandTemplateAndWrite(os.path.join(outdir, "CMakeLists.txt"), getTemplate("CMakeLists_plotter.txt")
            , ADD_FIND="\n".join("find_package({0})".format(fnd) for fnd in add_packages)
            , ADD_INCLUDE_DIRS=" ".join(include_dirs)
            , ADD_SOURCES=" ".join(sources)
            , ADD_PROPERTIES="\n".join(add_properties)
            , ADD_LINK="\n".join("target_link_libraries(plotter {0})".format(lib) for lib in linked_libraries)
            )

def prepareWorkdir(workdir): ## TODO rename to preparePlotsWorkdir
    if os.path.exists(workdir):
        raise Exception("Work directory {0} exists already!".format(workdir))
    os.mkdir(workdir)
    plotterdir = os.path.join(workdir, "plotter")
    histosdir = os.path.join(workdir, "histos")
    plotsdir = os.path.join(workdir, "plots")
    for aDir in (plotterdir, histosdir, plotsdir):
        os.mkdir(aDir)
    return plotterdir, histosdir, plotsdir

################################################################################
## HELPER: COMPILE PLOTTER DIRECTORY                                          ##
################################################################################

import subprocess

def compilePlotter(plotterdir):
    """
    Copy the necessary files and compile the plotter
    """
    try:
        from .import pathCommonTools
        subprocess.check_output(["cp", "-r", os.path.join(pathCommonTools, "cmake"), plotterdir], stderr=subprocess.STDOUT)
        subprocess.check_output(["cp", os.path.join(pathCommonTools, "templates", "generateHeader.sh"), plotterdir], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError, e:
        logger.error("Command {0} failed with exit code {1}\n{2}".format(e.cmd, e.returncode, e.output))
        raise e

    with insideOtherDirectory(plotterdir):
        logger.info("Compiling plotter in {0}".format(plotterdir))
        try:
            logger.debug("Calling CMake")
            subprocess.check_output(["cmake", "."], stderr=subprocess.STDOUT)
            logger.debug("Calling make")
            subprocess.check_output(["make"], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            logger.error("Command {0} failed with exit code {1}\n{2}".format(e.cmd, e.returncode, e.output))
            raise e

    return os.path.join(plotterdir, "plotter.exe")

def splitInChunks(theList, n):
    from itertools import izip, islice
    import math
    N = len(theList)
    chunkLength = int(math.ceil(1.*N/n))
    for iStart, iStop in izip(xrange(0, len(theList), chunkLength), xrange(chunkLength, len(theList)+chunkLength, chunkLength)):
        yield islice(theList, iStart, min(iStop,N))

def _makeSplitTask(commonArgs, toSplitArgs, outDir=None, info=None):
    splitSplitArgs = [ toSplitArgs ] ## no-splitting strategy
    if info and "db_name" in info:
        if info["db_name"].startswith("DYJetsToLL_M-10to50"):
            splitSplitArgs = list(list(chunk) for chunk in splitInChunks(toSplitArgs, 4))
        elif info["db_name"].startswith("TT_Tune"):
            splitSplitArgs = list(list(chunk) for chunk in splitInChunks(toSplitArgs, 3))
    cmds = [ " ".join(commonArgs+splitArgs) for splitArgs in splitSplitArgs ]
    from .batchhelpers import SplitAggregationTask, HaddAction
    return SplitAggregationTask(cmds, finalizeAction=HaddAction(cmds, outDir=outDir))

def _condorClusterFromTasks(taskList, workdir=None):
    from . import pathCMS
    from .condorhelpers import CommandListCondorJob
    condorJob = CommandListCondorJob(list(chain.from_iterable(task.commandList for task in taskList)),
            workDir=workdir,
            envSetupLines=[
                  "# Setup our CMS environment"
                , "pushd {CMS_PATH}".format(CMS_PATH=pathCMS)
                , "source /cvmfs/cms.cern.ch/cmsset_default.sh"
                , "eval `scram runtime --sh`"
                , "popd"
                , 'export THEANO_FLAGS="base_compiledir=$(pwd)"' ## isolate compilation cache for each job
                , ""
                ])
    for task in taskList:
        task.jobCluster = condorJob
    return condorJob

def _slurmArrayFromTasks(taskList, workdir=None):
    from . import pathCMS
    from .slurmhelpers import CommandListSlurmJob
    cfg_opts = {
          "environmentType" : "cms"
        , "cmsswDir"        : pathCMS
        , "sbatch_time"     : "0-02:00"
        , "sbatch_mem"      : "2048"
        , "stageoutFiles"   : ["*.root"]
        }
    slurmJob = CommandListSlurmJob(list(chain.from_iterable(task.commandList for task in taskList)), workDir=workdir, configOpts=cfg_opts)
    for task in taskList:
        task.jobCluster = slurmJob
    return slurmJob

def runPlotterOnSamples(plotterName, samples, outdir=None, suffix=None, useCluster=False, clusterworkdir=None, taskMon=None, verbose=False):
    """ Run the plotter for a sample """
    import os.path
    if useCluster:
        if outdir:
            if not ( os.path.exists(outdir) and os.path.isdir(outdir) ):
                raise Exception("Output path {} is not a directory")
        else:
            import os
            outdir = os.path.abspath(os.getcwd())
        taskList = []
        for sampName, sampDict in samples.iteritems():
            outFileName = ( "{0}.root".format(sampName) if suffix is None else "{0}{1}.root".format(sampName, suffix) )
            taskList.append(_makeSplitTask([plotterName, outFileName, sampDict["tree_name"], sampDict["sample_cut"]], sampDict["files"], outDir=outdir, info=sampDict))
        logger.info("{0:d} samples -> created {1:d} tasks with in total {2:d} commands".format(len(samples), len(taskList), sum(len(tsk.commandList) for tsk in taskList)))

        if False:
            clusterJob = _condorClusterFromTasks(taskList, workdir=clusterworkdir)
        else:
            clusterJob = _slurmArrayFromTasks(taskList, workdir=clusterworkdir)

        clusterJob.submit()
        if taskMon:
            taskMon.add([clusterJob], taskList)
            logger.info("Added slurm job to monitor")
        else:
            from .slurmhelpers import makeSlurmTasksMonitor as makeTasksMonitor
            mon = makeTasksMonitor([clusterJob], taskList)
            mon.collect() ## wait here

    else: ## run one after the other
        for sampName, sampDict in samples.iteritems():
            outFileName = ( "{0}.root".format(sampName) if suffix is None else "{0}{1}.root".format(sampName, suffix) )
            if outdir:
                outFileName = os.path.join(outdir, outFileName)
            logger.info("Writing histograms for sample {0} to file {1}".format(sampName, outFileName))
            cmdTokens = [plotterName, outFileName, sampDict["tree_name"], sampDict["sample_cut"]]+sampDict["files"]
            try:
                allout = subprocess.check_output(cmdTokens, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError, e:
                logger.error("Command {0} failed with exit code {1}\n{2}".format(" ".join(e.cmd), e.returncode, e.output))
                raise e
            if verbose:
                logger.info("Output of {}:".format(" ".join(cmdTokens)))
                print allout
                logger.info("END of command output")

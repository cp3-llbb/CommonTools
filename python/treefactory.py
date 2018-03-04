"""
Generate C++ to fill a skimmed tree, with helpers to run it
"""
__all__ = ("createSkimmer", "compileSkimmer", "runSkimmerOnSamples")

import logging
logger = logging.getLogger(__name__)

from itertools import chain

from .factoryhelpers import getTemplate, expandTemplate, expandTemplateAndWrite, getBranchType, insideOtherDirectory

def collectIdentifiersForSkimmer(selection, branchVars):
    identifiers = set()
    from .treedecorators import adaptArg
    try:
        identifiers.update(adaptArg(selection).leafDeps)
    except Exception, e:
        logger.error("Problem parsing selection for skimmer: {0}".format(str(e)))
    for brNm,brVar in branchVars.iteritems():
        try:
            identifiers.update(adaptArg(brVar).leafDeps)
        except Exception, e:
            logger.error("Problem parsing branch {0} : {1}".format(brNm, str(e)))
    return identifiers

def collectReducesFromCuts(cutsList, varList):
    from .treedecorators import TupleOp, Reduce, Next
    import uuid
    def _addReduces(depDict, op, aboveCut):
        if isinstance(op, TupleOp):
            top = aboveCut
            if ( isinstance(op, Reduce) or isinstance(op, Next) ):
                if op not in depDict:
                    depDict[op] = ("r_{0}".format(str(uuid.uuid4()).replace("-", "_")), set())
                    assert op.uname is None
                uname, deps = depDict[op]
                op.uname = uname
                deps.add(top)
                top = op
            for ia in op.args:
                _addReduces(depDict, ia, top)
        else:
            raise Exception("_addReduces called on {0!r}, which is not a TupleOp but a {1}".format(op, op.__class__.__name__))

    depDict = dict()
    for ct in cutsList:
        _addReduces(depDict, ct, ct)
    for v in varList:
        _addReduces(depDict, v, v)
    return depDict ## { op : (uname, depCutsAndOps) }

def clearReducesFromCuts(cutsList, varList):
    from .treedecorators import TupleOp, Reduce, Next
    import uuid
    def _clearReduces(op):
        if isinstance(op, TupleOp):
            if ( isinstance(op, Reduce) or isinstance(op, Next) ):
                op.uname = None
            for ia in op.args:
                _clearReduces(ia)
        else:
            raise Exception("_clearReduces called on {0!r}, which is not a TupleOp but a {1}".format(op, op.__class__.__name__))

    for expr in chain(cutsList, varList):
        _clearReduces(expr)

def collectPrecalcFromCuts(cutsList, varList):
    from .treedecorators import TupleOp
    def _addPrecalc(depDict, op, aboveCut):
        ## the one to be used for recursion
        if isinstance(op, TupleOp):
            top = aboveCut
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
    for ct in cutsList:
        _addPrecalc(depDict, ct, ct)
    for v in varList:
        _addPrecalc(depDict, v, v)
    return depDict ## { op : (uname, depPlotsAndOps) } ## only for precalc ops

def createSkimmerInnerLoop_opt1(selCuts, branchesWithUnameList, fill_tree_lines=None):
    """
    """
    ## NOTE this is a bit more limited scope than the histfactory: only need to arrange the cuts and reduces properly
    from .treedecorators import adaptArg, opDependsOn, boolType
    varsList =  [ adaptArg(var) for nm,var,unm in branchesWithUnameList ]
    reducesWithAllDeps = collectPrecalcFromCuts(selCuts, varsList)
    reducesWithAllDeps.update(collectReducesFromCuts(selCuts, varsList))

    def selDependsOnSel(s1, s2):
        # does the first arg depend on the second? (i.e. is s2 a validity requirement for s1)
        vd1 = set(adaptArg(d, typeHint=boolType) for ct in s1.cuts for d in ct.validDeps)
        return any( c2 in vd1 for c2 in s2.cuts )
    def selDependsOnRed(s1, r2):
        return any( opDependsOn(ct, r2.op) for ct in s1.cuts )
    def redDependsOnSel(r1, s2):
        vd1 = set(adaptArg(d, typeHint=boolType) for d in r1.op.validDeps)
        return any( c2 in vd1 for c2 in s2.cuts )
    def redDependsOnRed(r1, r2):
        vd1 = set(adaptArg(d, typeHint=boolType) for d in r1.op.validDeps)
        return opDependsOn(r1.op, r2.op) or any( opDependsOn(si, r2.op) for si in vd1 )
    def cut_reduce_comparator(o1, o2):
        ## sel dep on red : via opDependsOn
        ## red dep on sel : only if in validDeps
        ## sel dep on sel : only if in validDeps of any of the reduce ops it depends on
        ## red dep on dep
        ## neg if o1 should come first
        if isinstance(o1, SelectionNode):
            if isinstance(o2, SelectionNode):
                if selDependsOnSel(o2, o1):
                    #print "{0} depends on {1}".format(o2.ownDbgStr(), o1.ownDbgStr())
                    return -1
                elif selDependsOnSel(o1, o2):
                    #print "{0} depends on {1}".format(o1.ownDbgStr(), o2.ownDbgStr())
                    return 1
                else:
                    #print "no dependency between {0} and {1}".format(o1.ownDbgStr(), o2.ownDbgStr())
                    return 0
            elif isinstance(o2, PrecalcNode):
                if redDependsOnSel(o2, o1):
                    #print "{0} depends on {1}".format(o2.ownDbgStr(), o1.ownDbgStr())
                    return -1
                elif selDependsOnRed(o1, o2):
                    #print "{0} depends on {1}".format(o1.ownDbgStr(), o2.ownDbgStr())
                    return 1
                else:
                    #print "no dependency between {0} and {1}".format(o1.ownDbgStr(), o2.ownDbgStr())
                    return 0
            else:
                print "Unexpected type for second argument: ", type(o2)
        elif isinstance(o1, PrecalcNode):
            if isinstance(o2, SelectionNode):
                if selDependsOnRed(o2, o1):
                    #print "{0} depends on {1}".format(o2.ownDbgStr(), o1.ownDbgStr())
                    return -1
                elif redDependsOnSel(o1, o2):
                    #print "{0} depends on {1}".format(o1.ownDbgStr(), o2.ownDbgStr())
                    return 1
                else:
                    return 0
            elif isinstance(o2, PrecalcNode):
                if redDependsOnRed(o2, o1):
                    #print "{0} depends on {1}".format(o2.ownDbgStr(), o1.ownDbgStr())
                    return -1
                elif redDependsOnRed(o1, o2):
                    #print "{0} depends on {1}".format(o1.ownDbgStr(), o2.ownDbgStr())
                    return 1
                else:
                    #print "no dependency between {0} and {1}".format(o1.ownDbgStr(), o2.ownDbgStr())
                    return 0
            else:
                print "Unexpected type for second argument: ", type(o2)
        elif isinstance(o1, RootNode):
            return -1
        else:
            print "Unexpected type for first argument: ", type(o1)

    def treeDependsOn(ndWithTree, otherNode):
        return cut_reduce_comparator(ndWithTree, otherNode) > 0 or any( treeDependsOn(dnd, otherNode) for dnd in ndWithTree.depNodes )
    def depOnTree(myNode, otherWithTree):
        return cut_reduce_comparator(myNode, otherWithTree) > 0 or any( depOnTree(myNode, dnd) for dnd in otherWithTree.depNodes )

    from .hist_opt_2v2 import RootNode, SelectionNode, PrecalcNode, SkimmerFillBranchesNode, printTree

    skimmerNode = SkimmerFillBranchesNode(branchesWithUnameList, fill_tree_lines=fill_tree_lines)

    unsortedNodes = [ SelectionNode((c,)) for c in selCuts ] + [ PrecalcNode(red) for red in reducesWithAllDeps.iterkeys() ]

    rootNode = RootNode()
    for nd in unsortedNodes:
        whereAmI = rootNode
        #print "Inserting ", nd.ownDbgStr()
        while True:
            if any(depOnTree(nd, ond) for ond in whereAmI.depNodes):
                #print "Stepping to ", whereAmI.ownDbgStr()
                whereAmI = next(ond for ond in whereAmI.depNodes if depOnTree(nd, ond))
            else: ## you don't depend on anything here
                if depOnTree(whereAmI, nd): ## insert above
                    #print "Inserting above ", whereAmI.ownDbgStr()
                    if whereAmI.parent:
                        nd.parent = whereAmI.parent
                        nd.parent.removeDependentNode(whereAmI)
                        nd.parent.addDependentNode(nd)
                    else:
                        print "Inserting above the root node - you must be kidding"
                    whereAmI.parent = nd
                    nd.addDependentNode(whereAmI)
                    break
                elif len(whereAmI.depNodes) == 1: ## special case here: go as deep as possible to stay in the same order
                    whereAmI = whereAmI.depNodes[0]
                elif len(whereAmI.depNodes) > 1: ## sanity check
                    print "There's something seriously wrong: more than one dependency for the same node"
                else: ## at end, insert below
                    #print "Inserting below ", whereAmI.ownDbgStr()
                    nd.parent = whereAmI
                    whereAmI.addDependentNode(nd)
                    break
        #print "Tree after inserting ", nd.ownDbgStr()
        #for ln in printTree(rootNode):
        #    print ln

    ## collapse selection nodes
    ndAbove = rootNode
    while len(ndAbove.depNodes) > 0:
        nd = ndAbove.depNodes[0]
        if isinstance(ndAbove, SelectionNode) and isinstance(nd, SelectionNode):
            deps = list(nd.depNodes)
            ndAbove.removeDependentNode(nd)
            ndAbove.cuts = tuple(chain(ndAbove.cuts, nd.cuts))
            for ad in deps:
                nd.removeDependentNode(ad)
                ad.parent = ndAbove
                ndAbove.addDependentNode(ad)
        elif len(ndAbove.depNodes) > 1:
            print "ERROR more than one dependent node"
        else:
            ndAbove = nd
    ## stopping criterium makes this the "tip" of the tree
    ndAbove.addDependentNode(skimmerNode)
    skimmerNode.parent = ndAbove

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
        elif isinstance(someNode, SkimmerFillBranchesNode):
            for nm,var,unm in someNode.branches:
                yield (indent*indentStr)+ "{uname} = ( {expr} );".format(uname=unm, expr=adaptArg(var).get_TTreeDrawStr())
            if someNode.fill_tree_lines:
                yield ""
                for ln in someNode.fill_tree_lines:
                    yield (indent*indentStr)+ln
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
    retCode = "\n".join(ln for ln in cppLines(rootNode, indent=2))

    clearReducesFromCuts(selCuts, varsList)

    return retCode

################################################################################
## MAIN METHOD                                                                ##
################################################################################

import os, os.path

def createSkimmer(selection, branchVars, skeleton, outdir=None, treeName="t", **kwargs): ## includes, sources as kwargs
    """
    Generate C++ code from selection and variable definitions
    """
    if not outdir:
        outdir = os.getcwd()
        logger.warning("No output directory set, writing skimmer code to current directory {0}".format(outdir))
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
    # add jsoncpp (from external)
    from . import pathCommonTools
    external_dir = os.path.join(os.path.abspath(pathCommonTools), "external")
    include_dirs.append(os.path.join(external_dir, "include"))
    sources.append(os.path.join(external_dir, "src", "jsoncpp.cpp"))

    if kwargs.get("addScaleFactorsLib", False):
        pathCP3llbb = os.path.dirname(os.path.abspath(pathCommonTools))
        linked_libraries.append(os.path.join(pathCP3llbb, "Framework", "libBinnedValues.so"))
        include_dirs.append(os.path.join(pathCP3llbb, "Framework", "interface"))
        add_properties.append('set_target_properties(skimmer PROPERTIES COMPILE_FLAGS "-DSTANDALONE_SCALEFACTORS")')

    logger.info("List of requested branches: {0}".format(", ".join(nm for nm in branchVars.iterkeys())))
    logger.info("List of requested include files: {0}".format(", ".join(inc for inc in includes)))
    logger.info("List of requested source files: {0}".format(", ".join(src for src in sources)))

    expandTemplateAndWrite(os.path.join(outdir, "Skimmer.h"), getTemplate("Skimmer.h")
            , BRANCHES="\n        ".join(
                'const {typ}& {name} = tree["{name}"].read<{typ}>();'.format(typ=getBranchType(brName, skeleton._skeleton), name=brName)
                for brName in collectIdentifiersForSkimmer(selection.cut, branchVars))
            )

    import uuid
    branchesWithUnameList = list((nm, var, "b_{0}".format(str(uuid.uuid4()).replace("-", "_"))) for nm,var in branchVars.iteritems()) ## keep declarations and filling in the same order
    expandTemplateAndWrite(os.path.join(outdir, "Skimmer.cc"), getTemplate("Skimmer.cc")
            , INCLUDES="\n".join('#include "{0}"'.format(incl) for incl in includes)
            ## initialisation
            , OUTPUT_TREE_NAME=treeName
            , BEFORE_LOOP="\n".join(chain(

                ("    {typ}& {uname} = output_tree[\"{name}\"].write<{typ}>();".format(
                    typ=var._typeName, uname=unm, name=nm ## assumes stubs
                    ) for nm,var,unm in branchesWithUnameList)
                , ("    {0}".format(ln) for ln in list(kwargs.get("user_initialisation", [])))
                ))
            ## event loop
            , GLOBAL_CUT_AND_OUTPUT_BRANCHES_FILLING=createSkimmerInnerLoop_opt1(selection.cuts, branchesWithUnameList, fill_tree_lines=("output_tree.fill();", "++selected_entries;"))
            )

    expandTemplateAndWrite(os.path.join(outdir, "CMakeLists.txt"), getTemplate("CMakeLists_skimmer.txt")
            , ADD_FIND="\n".join("find_package({0})".format(fnd) for fnd in add_packages)
            , ADD_INCLUDE_DIRS=" ".join(include_dirs)
            , ADD_SOURCES =" ".join(sources)
            , ADD_PROPERTIES="\n".join(add_properties)
            , ADD_LINK="\n".join("target_link_libraries(skimmer {0})".format(lib) for lib in linked_libraries)
            )

def prepareWorkdir(workdir):
    # need much less than for plotter (output dir is passed as arg to skimmer, name generated from dataset)
    if os.path.exists(workdir):
        raise Exception("Work directory {0} exists already!".format(workdir))
    os.mkdir(workdir)
    return workdir

################################################################################
## HELPER: COMPILE SKIMMER DIRECTORY                                          ##
################################################################################

import subprocess

def compileSkimmer(skimmerdir):
    """
    Copy the necessary files and compile the skimmer
    """
    try:
        from .import pathCommonTools
        subprocess.check_output(["cp", "-r", os.path.join(pathCommonTools, "cmake"), skimmerdir], stderr=subprocess.STDOUT)
        subprocess.check_output(["cp", os.path.join(pathCommonTools, "templates", "generateHeader.sh"), skimmerdir], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError, e:
        logger.error("Command {0} failed with exit code {1}\n{2}".format(e.cmd, e.returncode, e.output))
        raise e

    with insideOtherDirectory(skimmerdir):
        logger.info("Compiling skimmer in {0}".format(skimmerdir))
        try:
            logger.debug("Calling CMake")
            subprocess.check_output(["cmake", "."], stderr=subprocess.STDOUT)
            logger.debug("Calling make")
            subprocess.check_output(["make"], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            logger.error("Command {0} failed with exit code {1}\n{2}".format(e.cmd, e.returncode, e.output))
            raise e

    return os.path.join(skimmerdir, "skimmer.exe")

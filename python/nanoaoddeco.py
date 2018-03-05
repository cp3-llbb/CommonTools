from .treedecorators import levelsAbove, addIntoHierarchy, TreeStub, BranchGroupStub, SmartTupleStub

def decoratedNanoAOD(nnAODTree):
    allLvs = dict((lv.GetName(), lv) for lv in nnAODTree.GetListOfLeaves())
    noCountLvs = set()
    collectionLvs = dict()
    for lvNm, lv in allLvs.iteritems():
        cntLv = lv.GetLeafCount()
        if cntLv:
            if cntLv.GetName() not in collectionLvs:
                collectionLvs[cntLv.GetName()] = []
            collectionLvs[cntLv.GetName()].append(lvNm)
        else:
            noCountLvs.add(lvNm)

    import re
    refPat = re.compile("(?P<target>\w+)Idx(?P<suff>\w+)?")
    def prefix_to_collectionName(prefix):
        return "{0}{1}s".format(prefix[0].lower(), prefix[1:].rstrip("_")) # un-capitalize
    ## construct the collections
    tree = TreeStub(nnAODTree)
    evtHierarchy = levelsAbove([], "event")
    # > event
    for cntNm, collAttrs in collectionLvs.iteritems():
        prefix = "{}_".format(cntNm[1:]) ## from nJet to Jet_
        if not all(lvNm.startswith(prefix) for lvNm in collAttrs):
            if all(lvNm.startswith(prefix[:-1]) for lvNm in collAttrs):
                prefix = prefix[:-1]
            else:
                print "Warning: not all leafs countable with '{0}' have names starting with '{1}': {2}".format(cntNm, prefix, ", ".join(lvNm for lvNm in collAttrs if not lvNm.startswith(prefix)))
        objs_smart = BranchGroupStub(prefix)
        collName = prefix_to_collectionName(prefix)
        addIntoHierarchy(collName, objs_smart, tree, evtHierarchy,
                capabilities=[ SmartTupleStub._SmartIterable(cntNm) ])
        for lvNm in collAttrs:
            name_nopref = lvNm[len(prefix):]
            m = refPat.match(name_nopref)
            if m:
                target = m.group("target")
                nm = ( "{0}{1}".format(target, m.group("suff")) if m.group("suff") else target )
                targetColl = ("genParts" if target == "mcMatch" else prefix_to_collectionName(target))
                objs_smart._addCapability(SmartTupleStub._RefToOther(nm, ( lambda collN, idxN : ( lambda obj : getattr(obj.event, collN)[getattr(obj, idxN)] ) )(targetColl, name_nopref), repl=(name_nopref,)))

    addIntoHierarchy("PV", BranchGroupStub("PV_"), tree, evtHierarchy)

    addIntoHierarchy("HLT", BranchGroupStub("HLT_"), tree, evtHierarchy)
    addIntoHierarchy("Flag", BranchGroupStub("Flag_"), tree, evtHierarchy)

    addIntoHierarchy("LHE", BranchGroupStub("LHE_"), tree, evtHierarchy)

    addIntoHierarchy("MET", BranchGroupStub("MET_"), tree, evtHierarchy)
    addIntoHierarchy("TkMET", BranchGroupStub("TkMET_"), tree, evtHierarchy)
    addIntoHierarchy("CaloMET", BranchGroupStub("CaloMET_"), tree, evtHierarchy)
    addIntoHierarchy("RawMET", BranchGroupStub("RawMET_"), tree, evtHierarchy)
    addIntoHierarchy("PuppiMET", BranchGroupStub("PuppiMET_"), tree, evtHierarchy)

    addIntoHierarchy("SoftActivityJet", BranchGroupStub("SoftActivityJet"), tree, evtHierarchy)
    addIntoHierarchy("HLTrigger", BranchGroupStub("HLTrigger"), tree, evtHierarchy)
    addIntoHierarchy("fixedGridRhoFastjet", BranchGroupStub("fixedGridRhoFastjet"), tree, evtHierarchy)
    # > event

    return tree

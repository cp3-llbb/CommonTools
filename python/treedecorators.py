import ROOT
from itertools import chain, izip
import copy

boolType = "bool"
PODTypes = set(("Float_t", "Double_t", "Int_t", "UInt_t", "Bool_t", "Char_t", "UChar_t", "ULong64_t", "int", "unsigned", "unsigned short", "char", "signed char", "unsigned char", "float", "double", "bool", "Short_t", "size_t", "std::size_t", "unsigned short")) ## there are many more (at least unsigned)
SizeType = "Int_t"
## TODO implement a "type system" - only need numeric types (boolean, integral and floating point, different precisions, math operators -> largest, comparison operators always -> bool)
## -> Python data model (emulating numeric types)
## for iterables / non-zero length things: may need new "elementary" operations (to be converted into control flow) - adapt "streaming" style and use bit-shift operations for readabilty (filter, map, reduce, zip (should not even be necessary: just stream enough info and optimise through getters later) etc. - fine as long as it is transparent enough, PURE functions start to matter here)

################################################################################
##                                 INTERFACES                                 ##
################################################################################

class TupleStub(object):
    """
    Interface & base class for stubs

    NOTE: to avoid conflicts with branch names, subclasses should not define
          new "visible" attributes (not starting with "_")
    """
    __slots__ = ("__weakref__", "_typeName")
    def __init__(self, typeName):
        self._typeName = typeName
    @property
    def op(self):
        raise ValueError("Can only get operation for 'complete' stubs (with a defined type)")
    def _get(self, name):
        raise AttributeError("No attribute called {0!r} for object {1!r}".format(name, self))
    def __getattr__(self, name):
        return self._get(name)

class TupleOp(object):
    """
    Interface for operations on leafs and resulting objects / numbers
    """
    __slots__ = ("__weakref__", "uname", "_explValidDeps")
    def __init__(self):
        self.uname = None ## cache ID for optimisations
        self._explValidDeps = []
    @property
    def args(self):
        # return iterable over other operations
        return tuple()
    @property
    def leafDeps(self):
        # return iterable over other all used fields from the TTree
        return tuple()
    @property
    def validDeps(self):
        # requirements for this expression to be valid (recursive by construction)
        lst = list(self._explValidDeps)
        for a in self.args:
            lst += a.validDeps
        return lst
    def addValidDep(self, dependency):
        self._explValidDeps.append(adaptArg(dependency, typeHint=boolType))
    @property
    def extDeps(self):
        # return iterable of (type, name) over externally-defined variables used (no-recursive)
        return tuple()
    @property
    def result(self):
        pass

    def __hash__(self):
        return hash(repr(self))

    ## Backends TODO: there should be a way to separate this a bit...
    def get_TTreeDrawStr(self):
        """
        Generate string for TTree::Draw (TTreeFormula etc.)
        Mostly for debugging and making sure all features are there
        """
        if self.uname is not None:
            return self.uname
        else:
            return self._get_TTreeDrawStr()

    def __eq__(self, other):
        raise Exception("TupleOp has no default __eq__") ## FIXME should be something like not implemented or so
    def __ne__(self, other):
        return not ( self == other )

# helpers
def allArgsOfOp(op, stopAtUName=False):
    """ Recursively yield all TupleOps this one depends on
    """
    for ia in op.args:
        yield ia
        if ( not stopAtUName ) or ( ia.uname is None ):
            for aa in allArgsOfOp(ia):
                yield aa

def opDependsOn(arg, other):
    """ Is other present anywhere in the dependency tree of arg?
    """
    return ( arg == other ) or ( other in arg.validDeps ) or any(ia == other for ia in allArgsOfOp(arg))

################################################################################
##                                   STUBS                                    ##
################################################################################

class PODStub(TupleStub):
    """
    Just a number
    """
    __slots__ = ("_parent",)
    def __init__(self, parent, typeName):
        self._parent = parent
        super(PODStub, self).__init__(typeName)
    @property
    def op(self):
        return self._parent
    def __repr__(self):
        return "PODStub({0!r}, {1!r})".format(self._parent, self._typeName)
    def _binaryOp(self, opName, other, outType="Double_t"):
        return MathOp(opName, self, other, outType=outType).result
## operator overloads
for nm,opNm in {
          "__add__" : "add"
        , "__sub__" : "subtract"
        , "__mul__" : "multiply"
        , "__truediv__" : " divide"
        , "__div__" : "divide"
        }.iteritems():
    setattr(PODStub, nm, (lambda oN : (lambda self, other : self._binaryOp(oN, other)))(opNm))
for nm in ("__lt__", "__le__", "__eq__", "__ne__", "__gt__", "__ge__"):
    setattr(PODStub, nm, (lambda oN, oT : (lambda self, other : self._binaryOp(oN, other, outType=oT)))(nm.strip("_"), boolType))

class ObjectStub(PODStub):
    """
    Imitate an object
    """
    __slots__ = ("_typ",)
    def __init__(self, parent, typeName):
        self._typ = getattr(ROOT, typeName) ## NOTE could also use TClass machinery
        super(ObjectStub, self).__init__(parent, typeName)
    def _get(self, name):
        if name not in dir(self._typ):
            raise AttributeError("Type {0} has no member {1}".format(self._typeName, name))
        if hasattr(self._typ, name) and isinstance(getattr(self._typ, name), ROOT.MethodProxy):
            return ObjectMethodStub(self, name)
        else:
            return GetDataMember(self, name).result
    def __repr__(self):
        return "ObjectStub({0!r}, {1!r})".format(self._parent, self._typeName)
    ## for mappable types: operator[] and valueType
    def __getitem__(self, ky):
        if self._get("__getitem__"):
            return GetItem(self, ky, indexType=self.indexType).result
        else:
            return NotImplemented
    @property
    def valueType(self):
        if self._typ.__name__.startswith("map<"):
            return self._typ.__name__[4:-1].split(",")[-1].strip()
        else:
            print "Name: ", self._typ.__name__
            return NotImplemented
    @property
    def indexType(self):
        if self._typ.__name__.startswith("map<"):
            return self._typ.__name__[4:-1].split(",")[0].strip()
        else:
            print "Name: ", self._typ.__name__
            return NotImplemented

    ## TODO implement more operators, if they are supported by the underlying class

class ArrayStub(TupleStub): ## different from an array result of a calculation or not? Not really, in fact...
    """
    (possibly var-sized) array of anything
    """
    __slots__ = ("_parent", "_length", "valueType")
    def __init__(self, parent, typeName, length):
        self._parent = parent
        self._length = length
        self.valueType = typeName
        super(ArrayStub, self).__init__("[{0}]".format(typeName))
    @property
    def op(self):
        return self._parent
    def __getitem__(self, index):
        return GetItem(self, index).result
    def __len__(self):
        return self._length
    def __repr__(self):
        return "ArrayStub({0!r}, {1!r}, {2!r})".format(self._parent, self._typeName, self._length)


class VectorStub(ObjectStub):
    """
    Vector-as-array (to be eliminated with var-array branches / generalised into object)
    """
    __slots__ = ("_parent", "valueType")
    def __init__(self, parent, typeName):
        self._parent = parent
        ##self.valueType = getattr(ROOT, typeName).value_type ## usable from 6.04.something on
        self.valueType = ">".join(tk.strip() for tk in "<".join(tok.strip() for tok in next(mem for mem in dir(getattr(ROOT, typeName)) if mem.startswith("_vector<") and mem.endswith("___M_range_check")).split("<")[1:]).split(">")[:-1])
        super(VectorStub, self).__init__(parent, typeName)
    @property
    def op(self):
        return self._parent
    def __getitem__(self, index):
        return GetItem(self, index).result
    def __len__(self):
        return op.extMethod("Length$")(self)
    def __repr__(self):
        return "VectorStub({0!r}, {1!r})".format(self._parent, self._typeName)

import re
vecPat = re.compile("vector\<(?P<item>[a-zA-Z_0-9\<\>,\: ]+)\>")

def makeStubForType(typeName, parent, length=None):
    if length is not None:
        return ArrayStub(parent, typeName, length)
    if typeName in PODTypes:
        return PODStub(parent, typeName) ## maybe this one can also take the type name
    else:
        m = vecPat.match(typeName)
        if m:
            return VectorStub(parent, typeName)
        else:
            return ObjectStub(parent, typeName)

def adaptArg(arg, typeHint=None):
    if isinstance(arg, TupleStub):
        return arg.op
    elif isinstance(arg, TupleOp):
        return arg
    elif typeHint is not None:
        if str(arg) == arg: ## string, needs quote
            return Const(typeHint, '"{}"'.format(arg))
        else:
            return Const(typeHint, arg)
    else:
        raise ValueError("Should get some kind of type hint")

def makeConst(value, typeHint):
    return makeStubForType(typeHint, adaptArg(value, typeHint))

class MethodStub(TupleStub):
    """
    Imitate a free-standing method
    """
    __slots__ = ("_name",)
    def __init__(self, name):
        self._name = name
        super(MethodStub, self).__init__("{0}(...)".format(self._name))
    def __call__(self, *args):
        ## TODO maybe tihs is a good place to resolve the right overload? or do some arguments checking
        return CallMethod(self._name, tuple(args)).result
    def __repr__(self):
        return "MethodStub({0!r})".format(self._name)

class ObjectMethodStub(TupleStub): ## TODO data members?
    """
    Imitate a member method of an object
    """
    __slots__ = ("_objStb", "_name")
    def __init__(self, objStb, name):
        self._objStb = objStb
        self._name = name
        super(ObjectMethodStub, self).__init__("{0}.{1}(...)".format(objStb._typeName, self._name))
    def __call__(self, *args):
        ## TODO maybe tihs is a good place to resolve the right overload? or do some arguments checking
        return CallMemberMethod(self._objStb, self._name, tuple(args)).result
    def __repr__(self):
        return "ObjectMethodStub({0!r}, {1!r})".format(self._objStb, self._name)

def allLeafs(branch, split=False): ## study splitlevel in tree as well
    """
    Recursively collect TTree leaves (TLeaf and TBranchElement)
    """
    if split:
        raise NotImplementedError("Going into TBranchElement not implemented yet")
    for lv in branch.GetListOfLeaves():
        yield lv
    for br in branch.GetListOfBranches():
        if isinstance(br, ROOT.TBranchElement):
            yield br
        else:
            for lv in allLeafs(br):
                yield lv

class SmartTupleStub(TupleStub):
    """
    First try a fixed list of proxies (which should have a _parent attribute to refer up the tree)
    """
    __slots__ = ("_parent", "_smartLeafs", "_extraCap")
    ## TODO make a SmartLeafStub base class (problems with multiple inheritance, maybe, unless these can always have smart leafs as well)
    def __init__(self, typeName, parent=None):
        self._smartLeafs = dict()
        self._extraCap = list()
        self._registerParent(parent)
        super(SmartTupleStub, self).__init__(typeName)
    @property
    def op(self):
        return self._parent

    def _registerSmartLeaf(self, name, stub, extraCap=None):
        stub._registerParent(self, extraCap=extraCap)
        self._smartLeafs[name] = stub

    def _registerParent(self, parent, extraCap=None):
        self._parent = parent
        if extraCap:
            for hlp in extraCap:
                self._addCapability(hlp)

    def _addCapability(self, hlp):
        hlp._parent = self
        self._extraCap.append(hlp)

    def __getattr__(self, name): ## FIXME as all are registered, we could probably also do this with properties
        # override to first check smart leafs
        if name in self._smartLeafs:
            return self._smartLeafs[name]
        else:
            att = self._getattrFromCap(name)
            if att is not None:
                return att
            else:
                return self._get(name)

    def _getCapWithAttr(self, name, exceptionIfAbsent=False):
        for hlp in self._extraCap:
            if name in hlp._dir:
                return hlp
        if exceptionIfAbsent:
            raise AttributeError("Object {0!r} has no attribute with name {1!r}".format(self, name))

    def _getattrFromCap(self, name, exceptionIfAbsent=False):
        hlp = self._getCapWithAttr(name, exceptionIfAbsent=exceptionIfAbsent)
        if hlp is not None:
            return getattr(hlp, name)

    ## inspect
    def __dir__(self):
        return list(set(self._availLeafs()).difference(self._listedLeafsBelow()))
    ## pass full list top-down
    def _moreAvailLeafs(self): ## excluding own
        if self._parent is not None:
            return self._parent._availLeafs()
        else:
            return set()
    def _availLeafs(self): ## including own
        avail = self._moreAvailLeafs()
        avail.update(self._smartLeafs.iterkeys())
        for hlp in self._extraCap:
            avail.update(hlp._dir)
        return avail
    ## extra helper (split in two)
    def _listedLeafsBelow(self): ## excluding own
        lst = set()
        for ch in self._smartLeafs.itervalues():
            lst.update(set(ch._listedLeafs()))
        for dc in self._extraCap:
            lst.update(dc._replLeafs())
        return lst
    ## pass already-listed bottom up
    def _listedLeafs(self): ## including own
        lst = self._listedLeafsBelow()
        availListed = set(self.__dir__()).intersection(self._moreAvailLeafs()) ## exclude those that have already been listed
        ## add object members
        lst.update(availListed)
        return lst

    ## extra decorations
    class _SmartLeafDecoration(object):
        __slots__ = ("__weakref__", "_parent")
        _dir = tuple()
        def __init__(self, parent=None):
            self._parent = parent
        def _replLeafs(self):
            return set()
        @property
        def _leafDeps(self):
            return tuple()

    class _SmartIterable(_SmartLeafDecoration):
        """ Approach a structure of arrays as an array of structures """
        __slots__ = ("_len",)
        _dir = ("__getitem__", "__len__", "__nonzero__", "__iter__")
        def __init__(self, _len, parent=None):
            if str(_len) == _len:
                self._len = ( lambda ilen : (lambda self : getattr(self._parent, ilen)) )(_len) ## one level up from parent
            else:
                self._len = _len
            super(SmartTupleStub._SmartIterable, self).__init__(parent=parent)
        def __getitem__(self, idx):
            return SmartLeafItemStub(idx, parent=self._parent)
        def __len__(self):
            return self._len(self._parent)
        def __iter__(self):
            for i in xrange(len(self)):
                yield self[i]
        def __nonzero__(self):
            return self.__len__() > 0 ## FIXME put what makes sense...
        def _replLeafs(self):
            return self[-1]._availLeafs()
        @property
        def _leafDeps(self):
            return adaptArg(self.__len__()).leafDeps

    class _WrappedIterable(_SmartLeafDecoration):
        """ Return wrapped elements of the array (attached to a LeafFacade) """
        __slots__ = ("_base", "_stubMap")
        _dir = ("__getitem__", "__len__", "__nonzero__", "__iter__")
        def __init__(self, base, stubMap, parent=None):
            self._base = base
            self._stubMap = stubMap
            super(SmartTupleStub._WrappedIterable, self).__init__(parent=parent)
        def _wrap(self, rawItm):
            return self._stubMap[rawItm._typeName](rawItm._parent, pStub=self._parent)
        def __getitem__(self, idx):
            return self._wrap(self._base[idx])
        def __len__(self):
            return self._base.__len__()
        def __iter__(self):
            for itm in self._base:
                yield self_wrap(itm)
        def __nonzero__(self):
            return self.__len__() > 0 ## FIXME put what makes sense
        def _replLeafs(self):
            return self[-1]._availLeafs()
        @property
        def _leafDeps(self):
            return self._base.leafDeps

    class _BoolTestableFromLeaf(_SmartLeafDecoration):
        __slots__ = ("_bool",)
        _dir = ("__nonzero__",)
        def __init__(self, _bool, parent=None):
            self._bool = _bool
            super(SmartTupleStub._BoolTestableFromLeaf, self).__init__(parent=parent)
        def __nonzero__(self):
            return self._bool(self._parent)

    class _RefToOther(_SmartLeafDecoration):
        __slots__ = ("_name", "_refGetter", "_repl")
        def __init__(self, name, refGetter, parent=None, repl=None):
            self._name = name
            self._refGetter = refGetter
            self._repl = tuple(repl) if repl else tuple()
            super(SmartTupleStub._RefToOther, self).__init__(parent=parent)
        @property
        def _dir(self):
            return (self._name,)
        def _replLeafs(self):
            return self._repl
        def __getattr__(self, name):
            if name == self._name:
                return self._refGetter(self._parent)
            else:
                raise AttributeError("No attribute called {0!r} for object {1!r}".format(name, self))
        def __repr__(self):
            return "SmartTupleStub._RefToOther({0!r}, {1!r}, parent={2!r})".format(self._name, self._refGetter, self._parent)

    class _RefList(_SmartLeafDecoration):
        __slots__ = ("_base", "_cont")
        _dir = ("__getitem__", "__iter__", "__len__", "__nonzero__")
        def __init__(self, base, cont, parent=None):
            self._base = base
            self._cont = cont
            super(SmartTupleStub._RefList, self).__init__(parent=parent)
        def __getitem__(self, idx):
            return self._cont[self._base[idx]]
        def __iter__(self):
            for i in self._base:
                yield self._cont[i]
        def __len__(self):
            return self._base.__len__()
        def __nonzero__(self):
            return self.__len__() != 0 ### FIXME
        @property
        def _leafDeps(self):
            ###print "RefList with base {0!r} and container {1!r}".format(self._base, self._cont)
            return chain(self._base._parent.leafDeps, self._cont._get_leafDeps()) ## FIXME this probably won't work for MC particle refs

    ## resolve iterable-like methods dynamically (could be implemented generically using properties)
    def __getitem__(self, idx):
        method = self._getattrFromCap("__getitem__")
        if method:
            return method(idx)
        else:
            return NotImplemented
    def __len__(self):
        method = self._getattrFromCap("__len__")
        if method:
            return method()
        else:
            return NotImplemented
    def __iter__(self):
        for elm in self._getattFromCap("__iter__", True)():
            yield elm
        ## FIXME this should probably be done differently (use filter/map/reduce/... directly)
    def __nonzero__(self):
        ## NOTE important as soon as __len__ is implemented (see python reference on the data model)
        method = self._getattrFromCap("__nonzero__")
        if method:
            return method()
        else:
            return NotImplemented

    def _get_leafDeps(self):
        return chain.from_iterable(cp._leafDeps for cp in self._extraCap)

class TreeStub(SmartTupleStub):
    """
    Tree stub
    """
    __slots__ = ("_skeleton", "_lvs")
    def __init__(self, skeleton):
        self._skeleton = skeleton
        self._lvs = dict()
        self._readLeafs() ## also fill self._lvs
        super(TreeStub, self).__init__("struct")

    def _readLeafs(self):
        self._lvs = dict( (br.GetName(), br) for br in allLeafs(self._skeleton) )

    def _get(self, name):
        if name in self._lvs:
            lv = self._lvs[name]
            if not lv: ## update in case we moved somewhere else or so
                print "DBG: re-reading leafs"
                self._readLeafs()
                lv = self._lvs[name]
                assert lv
            if isinstance(lv, ROOT.TLeaf):
                if lv.GetLeafCount():
                    lenLv = lv.GetLeafCount()
                    return GetArrayLeaf(lv.GetTypeName(), name, GetLeaf(lenLv.GetTypeName(), lenLv.GetName())).result
                elif lv.GetTitle().endswith("]"):
                    tp,ln = tuple(lv.GetTitle().strip("]").split("["))
                    return GetArrayLeaf(lv.GetTypeName(), name, Const(SizeType, int(ln))).result
                else:
                    return GetLeaf(lv.GetTypeName(), name).result
            else:
                return GetLeaf(lv.GetClassName() if lv.GetClassName() != '' else lv.GetTypeName(), name).result
        else:
            raise AttributeError("Tree has no branch with name {0}".format(repr(name)))
    def __repr__(self):
        return "TreeStub({0!r})".format(self._skeleton)

    def _availLeafs(self):
        avail = super(TreeStub, self)._availLeafs()
        avail.update(set(lv for lv in self._lvs.iterkeys() if "." not in lv and not lv.endswith("_"))) ## TODO let the classes tell us...
        return avail

class BranchGroupStub(SmartTupleStub):
    """
    Stub for a group of related branches (with shared prefix)
    """
    __slots__ = ("_prefix", "_nStrp")
    def __init__(self, prefix, nStrp=0, **kwargs):
        self._prefix = prefix
        self._nStrp = nStrp
        super(BranchGroupStub, self).__init__("struct", **kwargs)
    def _get(self, name):
        return getattr(self._parent, "".join((("".join(self._prefix.split("_")[:-self._nStrp]) if self._nStrp > 0 else self._prefix), name))) ## TODO could composition of join be made optional?
    def __repr__(self):
        return "BranchGroupStub({0!r}, parent={1!r})".format(self._prefix, self._parent)

    def _listedLeafs(self):
        return set("".join((self._prefix, ky)) for ky in super(BranchGroupStub, self)._listedLeafs())

    def _moreAvailLeafs(self):
        return set(lf[len(self._prefix):] for lf in super(BranchGroupStub, self)._moreAvailLeafs() if lf.startswith(self._prefix) and lf != self._prefix)

class SmartLeafItemStub(SmartTupleStub):
    ### FIXME maybe need to make BranchGroupStub a base class, with the current behaviour for non-indexed and 
    """
    Stub for an item in a group of related branches
    """
    __slots__ = ("_idx",)
    ## NOTE special case: always has a parent, but is never registered - maybe we should change that and use the copy trick here
    def __init__(self, idx, parent=None):
        self._idx = adaptArg(idx, typeHint=SizeType)
        super(SmartLeafItemStub, self).__init__("struct", parent=parent)

    @property
    def i(self):
        return makeStubForType(SizeType, self._idx)

    class _ItemSmartLeafStub(SmartTupleStub):
        __slots__ = ("_orig",)
        def __init__(self, orig, parent=None):
            self._orig = orig
            super(SmartLeafItemStub._ItemSmartLeafStub, self).__init__("struct", parent=parent)
        def __getattr__(self, name):
            return getattr(self._orig, name)[self._orig._idx] ## first attempt

    def __getattr__(self, name):
        if name.startswith("_ipython"):
            raise AttributeError("No attribute called {0!r} for object {1!r}".format(name, self))
        # override to first check smart leafs
        if name in self._parent._smartLeafs: ## unless they are refs, then jump from parent
            print "Getting smart leaf {0} of {1}".format(name, self)
            return SmartLeafItemStub._ItemSmartLeafStub(self._parent._smartLeafs[name], self)
        else:
            att = self._getattrFromCap(name)
            if att is not None:
                return att
            hlp = self._parent._getCapWithAttr(name)
            if hlp is not None:
                cp = copy.copy(hlp)
                cp._parent = self
                if isinstance(cp, SmartTupleStub._RefToOther) and isinstance(cp._refGetter, GoUpBy):
                    cp._refGetter = copy.copy(cp._refGetter)
                    cp._refGetter.nSteps += 1
                return getattr(cp, name)
            else:
                return self._parent._get(name)[self._idx]
    def __repr__(self):
        return "SmartLeafItemStub({0!r}, parent={1!r})".format(self._idx, self._parent)

    def _moreAvailLeafs(self): ## everything from parent except list inteface
        avail = self._parent._availLeafs()
        avail.discard("__len__")
        avail.discard("__getitem__")
        ## TODO discard a few more (references that are not up and not indexed like our array, see above - needs a bit of logic, may not be possible until arriving at the final branch)
        return avail

    def __eq__(self, other):
        if self._parent == other._parent:
            return self.i == other.i
        else:
            raise Exception("Only objects from the same container can be compared for equality")
    def __ne__(self, other):
        return not ( self == other )

class GoUpBy(object):
    """
    Construct .., ../.. etc.
    """
    __slots__ = ("__weakref__", "nSteps",)
    def __init__(self, nSteps):
        self.nSteps = nSteps
    def __call__(self, start):
        i = 0
        res = start
        while i < self.nSteps:
            res = res._parent
            i += 1
        return res
    def __repr__(self):
        return "GoUpBy({0:d})".format(self.nSteps)

################################################################################
##                                 OPERATIONS                                 ##
################################################################################

class Const(TupleOp):
    """
    Hard-coded number
    """
    __slots__ = ("typeName", "value")
    def __init__(self, typeName, value):
        self.typeName = typeName
        self.value = value
        super(Const, self).__init__()
    @property
    def result(self):
        return makeStubForType(self.typeName, self)
    def __repr__(self):
        return "Const({0!r})".format(self.value)
    def __eq__(self, other):
        return isinstance(other, Const) and ( self.typeName == other.typeName ) and ( self.value == other.value )
    # backends
    def _get_TTreeDrawStr(self):
        try:
            if abs(self.value) == float("inf"):
                return "std::numeric_limits<{0}>::{mnmx}()".format(self.typeName, mnmx=("min" if self.value < 0. else "max"))
        except:
            pass
        return str(self.value) ## should maybe be type-aware...

class Construct(TupleOp):
    __slots__ = ("typeName", "_args")
    def __init__(self, typeName, args):
        self.typeName = typeName
        self._args = tuple(adaptArg(a, typeHint="Double_t") for a in args)
        super(Construct, self).__init__()
    @property
    def args(self):
        return self._args
    @property
    def leafDeps(self):
        return chain.from_iterable( arg.leafDeps for arg in self._args )
    @property
    def result(self):
        return makeStubForType(self.typeName, self)
    def __repr__(self):
        return "Construct({0!r}, {1})".format(self.typeName, ", ".join(repr(a) for a in self._args))
    def __eq__(self, other):
        return isinstance(other, Construct) and ( self.typeName == other.typeName ) and len(self._args) == len(other._args) and all( ( aa == ab ) for aa,ab in izip(self._args, other._args) )
    def _get_TTreeDrawStr(self):
        return "{0}{{{1}}}".format(self.typeName, ", ".join(a.get_TTreeDrawStr() for a in self._args))

class InitList(TupleOp):
    __slots__ = ("typeName", "elms")
    def __init__(self, typeName, elmType, elms):
        self.typeName = typeName
        self.elms = tuple(adaptArg(e, typeHint=elmType) for e in elms)
        super(InitList, self).__init__()
    @property
    def args(self):
        return self.elms
    @property
    def leafDeps(self):
        return chain.from_iterable( arg.leafDeps for arg in self.elms )
    @property
    def result(self):
        return makeStubForType(self.typeName, self)
    def __repr__(self):
        return "InitList<{0}>({1})".format(self.typeName, ", ".join(repr(elm) for elm in self.elms))
    def __eq__(self, other):
        return isinstance(other, InitList) and ( self.typeName == other.typeName ) and len(self.elms) == len(other.elms) and all( ( ea == eb ) for ea, eb in izip(self.elms, other.elms) )
    def _get_TTreeDrawStr(self):
        return "{{ {0} }}".format(", ".join(elm.get_TTreeDrawStr() for elm in self.elms))

class ExtVar(TupleOp):
    """
    Externally-defined variable (used by name)
    """
    __slots__ = ("typeName", "name")
    def __init__(self, typeName, name):
        self.typeName = typeName
        self.name = name
        super(ExtVar, self).__init__()
    @property
    def extDeps(self):
        return ((self.typeName, self.name),)
    @property
    def result(self):
        return makeStubForType(self.typeName, self)
    def __repr__(self):
        return "ExtVar({0!r}, {1!r})".format(self.typeName, self.name)
    def __eq__(self, other):
        return isinstance(other, ExtVar) and ( self.typeName == other.typeName ) and ( self.name == other.name )
    # backends
    def _get_TTreeDrawStr(self):
        return self.name

class GetLeaf(TupleOp):
    """
    Get the number from a leaf
    """
    __slots__ = ("typeName", "name")
    def __init__(self, typeName, name):
        self.typeName = typeName
        self.name = name
        super(GetLeaf, self).__init__()
    @property
    def leafDeps(self):
        return self.name,
    @property
    def result(self):
        return makeStubForType(self.typeName, self)
    def __repr__(self):
        return "GetLeaf({0!r}, {1!r})".format(self.typeName, self.name)
    def __eq__(self, other): ## TODO maybe name is enough
        return isinstance(other, GetLeaf) and ( self.typeName == other.typeName ) and ( self.name == other.name )
    # backends
    def _get_TTreeDrawStr(self):
        return self.name

class GetArrayLeaf(TupleOp):
    """
    Get the number from a leaf
    """
    __slots__ = ("typeName", "name", "length")
    def __init__(self, typeName, name, length):
        self.typeName = typeName
        self.name = name
        self.length = length
        super(GetArrayLeaf, self).__init__()
    @property
    def leafDeps(self):
        return self.name, ## TODO add length (if applicable !!!). Maybe at this point need to allow for Const "stub" (with same operator overloads as POD stub)
    @property
    def result(self):
        return makeStubForType(self.typeName, self, makeStubForType(SizeType, self.length))
    def __repr__(self):
        return "GetArrayLeaf({0!r}, {1!r}, {2!r})".format(self.typeName, self.name, self.length)
    def __eq__(self, other): ## TODO maybe name is enough
        return isinstance(other, GetArrayLeaf) and ( self.typeName == other.typeName ) and ( self.name == other.name ) and ( self.length == other.length )
    # backends
    def _get_TTreeDrawStr(self):
        return self.name

class GetItem(TupleOp): 
    """
    Get item from array (from function call or from array leaf)
    """
    __slots__ = ("arg", "typeName", "index")
    def __init__(self, arg, index, indexType=SizeType):
        self.arg = adaptArg(arg)
        self.typeName = arg.valueType
        self.index = adaptArg(index, typeHint=SizeType)
        super(GetItem, self).__init__()
        ## add validity requirement
        ## TODO in the case of a ref (MC, -1 or good) or index (< len), we *could* do some checks
        ## TODO for the rng_min_element_by etc. case, the best would be to add (to GetItem) a validity requirement at construction time
        if isinstance(self.index, CallMethod) and self.index.name == "*" and isinstance(self.index._args[0], Next):
            self.addValidDep(self.index._args[0].isValid())
    @property
    def args(self):
        return [ self.arg ] + ([ self.index ] if not isinstance(self.index, Const) else [])
    @property
    def leafDeps(self):
        return chain.from_iterable(dep.leafDeps for dep in (self.arg, self.index))
    @property
    def result(self):
        return makeStubForType(self.typeName, self) ## TODO make sure that any parent gives back the right type name (may have to call it itemtype or so)
    def __repr__(self):
        return "GetItem({0!r}, {1!r})".format(self.arg, self.index)
    def __eq__(self, other): ## TODO maybe typeName is not needed
        return isinstance(other, GetItem) and ( self.arg == other.arg ) and ( self.typeName == other.typeName ) and ( self.index == other.index )
    # backends
    def _get_TTreeDrawStr(self):
        return "{0}[{1}]".format(self.arg.get_TTreeDrawStr(), self.index.get_TTreeDrawStr())

class LocalVariablePlaceholder(TupleOp):
    """
    Placeholder type for a local variable connected to an index (first step in a specific-to-general strategy)
    """
    __slots__ = ("name", "typeHint")
    def __init__(self, name, typeHint):
        self.name = name
        self.typeHint = typeHint
        super(LocalVariablePlaceholder, self).__init__()
    @property
    def leafDeps(self):
        return tuple()
    @property
    def result(self):
        return makeStubForType(self.typeHint, self)
    def __eq__(self, other): ## TODO ??
        return isinstance(other, LocalVariablePlaceholder) and ( self.name == other.name ) and ( self.typeHint == other.typeHint )
    def _get_TTreeDrawStr(self):
        return str(self.name)
    def __repr__(self):
        return "LocalVariablePlaceholder({0!r}, {1!r})".format(self.name, self.typeHint)

def isRefList(rng):
    """ Test if the range is a list of references or a group of vectors
    """
    iterCap = rng._getCapWithAttr("__getitem__")
    return ( iterCap is not None ) and isinstance(iterCap, SmartTupleStub._RefList)

def getCapturesForExprs(expressions):
    captures = set()
    for expr in expressions:
        for a in allArgsOfOp(expr, stopAtUName=True):
            if a.uname:
                captures.add(a.uname)
            for evT,evN in a.extDeps:
                if True: ## TODO only if evT is small
                    captures.add(evN)
                else:
                    captures.add("&{0}".format(evN))
    return captures

class Next(TupleOp):
    """ std::find_if
    """
    __slots__ = ("rng", "predFun", "_itArg", "_predExpr", "_refList")
    def __init__(self, rng, predFun):
        self.rng = rng
        self.predFun = predFun
        self._init()
        super(Next, self).__init__()
    def _init(self):
        if isRefList(self.rng):
            refListCap = self.rng._getCapWithAttr("__getitem__")
            self._itArg = adaptArg(refListCap._base)
            self._predExpr = adaptArg(self.predFun(refListCap._cont[LocalVariablePlaceholder("item", "unsigned short")]), typeHint=boolType)
            self._refList = True
        else:
            self._itArg = adaptArg(op.len(self.rng))
            self._predExpr = adaptArg(self.predFun(self.rng[LocalVariablePlaceholder("i", "unsigned short")]), typeHint=boolType)
            self._refList = False
    @property
    def args(self):
        return [ self._predExpr ]
    @property
    def leafDeps(self):
        return chain(self.rng._get_leafDeps(), self._predExpr.leafDeps)
    def isValid(self):
        if self._refList:
            return ( self.result != op.extMethod("std::end")(self._itArg) )
        else:
            return ( self.result != op.extMethod("IndexRangeIterator<unsigned short>")(self._itArg, self._itArg) )
    @property
    def result(self):
        return makeStubForType("unsigned short", self)
    def __repr__(self):
        if self._refList:
            return "Next_RefList( {0!r}, {1!r} )".format(self._itArg, self._predExpr)
        else:
            return "Next_Generic( {0!r}, {1!r} )".format(self._itArg, self._predExpr)
    def __eq__(self, other):
        return isinstance(other, Next) and ( self.rng == other.rng ) and ( self._predExpr == other._predExpr ) and ( self._itArg == other._itArg ) and ( self._refList == other._refList )
    def _get_TTreeDrawStr(self):
        if self._refList:
            return "std::find_if(std::begin({arg}), std::end({arg}), [{captures}] ( unsigned short item ) {{ return {predExpr}; }} )".format(
                    arg=self._itArg.get_TTreeDrawStr()
                  , predExpr=self._predExpr.get_TTreeDrawStr()
                  , captures=",".join(chain(["this"], getCapturesForExprs((self._predExpr,))))
                  )
        else:
            return "std::find_if({itTp}(0,{N}), {itTp}({N},{N}), [{captures}] ( unsigned short i ) {{ return {predExpr}; }} )".format(
                    itTp="IndexRangeIterator<unsigned short>"
                  , N=self._itArg.get_TTreeDrawStr()
                  , predExpr=self._predExpr.get_TTreeDrawStr()
                  , captures=",".join(chain(["this"], getCapturesForExprs((self._predExpr,))))
                  )

class Reduce(TupleOp):
    """
    reduce (std::accumulate) over an iterable

    accuFun: res, item -> nextResExpr
    isAssociative: if not, items are guaranteed to be processed in order (otherwise could be distribute)
    """
    __slots__ = ("rng", "start", "accuFun", "valueType", "isAssociative", "_funExpr", "_itArg", "_refList")
    def __init__(self, rng, start, accuFun, valueType=None, isAssociative=False):
        self.rng = rng
        self.start = adaptArg(start)
        self.accuFun = accuFun
        self.valueType = valueType if valueType else self.start.valueType
        self.isAssociative = isAssociative
        self._init()
        super(Reduce, self).__init__()
    def _init(self):
        if isRefList(self.rng):
            refListCap = self.rng._getCapWithAttr("__getitem__")
            self._funExpr = adaptArg(self.accuFun(
                      makeStubForType(self.valueType, LocalVariablePlaceholder("res", self.valueType))
                    , refListCap._cont[LocalVariablePlaceholder("item", "unsigned short int")]
                    ), typeHint=self.valueType)
            self._itArg = adaptArg(refListCap._base)
            self._refList = True
        else:
            self._funExpr= adaptArg(self.accuFun(
                      makeStubForType(self.valueType, LocalVariablePlaceholder("res", self.valueType))
                    , self.rng[LocalVariablePlaceholder("i", "unsigned short int")]
                    ), typeHint=self.valueType)
            self._itArg = adaptArg(op.len(self.rng))
            self._refList = False

    @property
    def args(self):
        return [ self.start, self._funExpr ]
    @property
    def leafDeps(self):
        return chain(self.rng._get_leafDeps(), self.start.leafDeps, self._funExpr.leafDeps)
    @property
    def result(self):
        return makeStubForType(self.valueType, self)

    def __repr__(self):
        if self._refList:
            return "Reduce_RefList( {0!r}, {1!r}, {2!r}, valueType={3!r}, isAssociative={4} )".format(self._itArg, self.start, self._funExpr, self.valueType, self.isAssociative)
        else:
            return "Reduce_Generic( {0!r}, {1!r}, {2!r}, valueType={3!r}, isAssociative={4} )".format(self._itArg, self.start, self._funExpr, self.valueType, self.isAssociative)
    def __eq__(self, other):
        return isinstance(other, Reduce) and ( self.rng == other.rng ) and ( self.start == other.start ) and ( self._refList == other._refList ) and ( self._itArg == other._itArg ) and ( self._funExpr == other._funExpr ) and ( self.valueType == other.valueType ) and ( self.isAssociative == other.isAssociative )
    # backend
    def _get_TTreeDrawStr(self):
        if self._refList:
            return "std::accumulate(std::begin({arg}), std::end({arg}), {valTp}({start}), [{captures}] ( {valTp} res, unsigned short item ) -> {valTp} {{ return {funExpr}; }} )".format(
                    valTp=self.valueType
                  , arg=self._itArg.get_TTreeDrawStr()
                  , start=self.start.get_TTreeDrawStr()
                  , funExpr=self._funExpr.get_TTreeDrawStr()
                  , captures=",".join(chain(["this"], getCapturesForExprs((self._funExpr,))))
                  )
        else: # generic case (typically virtual container (e.g. ttW_lepton_*) -> isinstance(iterCap, SmartTupleStub._SmartIterable))
            return "std::accumulate({itTp}(0,{N}), {itTp}({N},{N}), {valTp}({start}), [{captures}] ( {valTp} res, unsigned short i ) -> {valTp} {{ return {funExpr}; }} )".format(
                    valTp=self.valueType
                  , itTp="IndexRangeIterator<unsigned short>"
                  , N=self._itArg.get_TTreeDrawStr()
                  , start=self.start.get_TTreeDrawStr()
                  , funExpr=self._funExpr.get_TTreeDrawStr()
                  , captures=",".join(chain(["this"], getCapturesForExprs((self._funExpr,))))
                  )
            ## what works now: op.rng_sum(tup.muons, lambda mu : mu.p4.Pt()) + op.rng_sum(tup.electrons, lambda el : el.p4.Pt()) - op.rng_sum(tup.ttW.l, lambda l : l.L.p4.Pt()) (sum of non-selected lepton PT's)

class GetDataMember(TupleOp):
    """
    Get a data member
    """
    __slots__ = ("this", "name")
    def __init__(self, this, name):
        self.this = adaptArg(this)
        self.name = name ## NOTE can only be a hardcoded string this way
        super(GetDataMember, self).__init__()
    @property
    def args(self):
        return [ self.this ]
    @property
    def leafDeps(self):
        return self.this.leafDeps ## TODO and add something for the (possibly) new branches we ask for if splitlevel is high?
    @property
    def result(self):
        if not self.name.startswith("_"):
            try:
                protoTp = self.this.result._typ
                proto = protoTp() ## should *in principle* work for most ROOT objects
                att = getattr(proto, self.name)
                tpNm = type(att).__name__
                if protoTp.__name__.startswith("pair<") and self.name in ("first", "second"):
                    tpNms = tuple(tok.strip() for tok in protoTp.__name__[5:-1].split(","))
                    return makeStubForType((tpNms[0] if self.name == "first" else tpNms[1]), self)
                return makeStubForType(tpNm, self)
            except Exception, e:
                print "Problem getting type of data member {0} of {1!r}".format(self.name, self.this), e
        return makeStubForType("void", self)
    def __repr__(self):
        return "GetDataMember({0!r}, {1!r})".format(self.this, self.name)
    def __eq__(self, other):
        return isinstance(other, GetDataMember) and ( self.this == other.this ) and ( self.name == other.name )
    # backends
    def _get_TTreeDrawStr(self):
        return "{0}.{1}".format(self.this.get_TTreeDrawStr(), self.name)

class CallMethod(TupleOp):
    """
    Call a method
    """
    __slots__ = ("name", "_mp", "_args")
    def __init__(self, name, args):
        self.name = name ## NOTE can only be a hardcoded string this way
        try:
            self._mp  = getattr(ROOT, name)
        except:
            self._mp = None
        self._args = tuple(adaptArg(arg) for arg in args)
        super(CallMethod, self).__init__()
    @property
    def args(self):
        return self._args
    @property
    def leafDeps(self):
        return chain.from_iterable( arg.leafDeps for arg in self._args )
    @property
    def result(self):
        retTypeN = next( tok.strip("*&") for tok in self._mp.func_doc.split() if tok != "const" ) if self._mp else "Float_t"
        return makeStubForType(retTypeN, self)
    def __repr__(self):
        return "CallMethod({0!r}, ({1}))".format(self.name, ", ".join(repr(arg) for arg in self._args))
    def __eq__(self, other):
        return isinstance(other, CallMethod) and ( self.name == other.name ) and ( len(self._args) == len(other._args) ) and all( ( sa == oa ) for sa, oa in izip(self._args, other._args))
    # backends
    def _get_TTreeDrawStr(self):
        return "{0}({1})".format(self.name, ", ".join(arg.get_TTreeDrawStr() for arg in self._args))

class CallMemberMethod(TupleOp):
    #return CallMemberMethod(self._objStb.parent, self._name, tuple(args)).result
    """
    Call a member method
    """
    __slots__ = ("this", "name", "_mp", "_args")
    def __init__(self, this, name, args):
        self.this = adaptArg(this)
        self.name = name ## NOTE can only be a hardcoded string this way
        self._mp  = getattr(this._typ, name)
        self._args = tuple(adaptArg(arg) for arg in args)
        super(CallMemberMethod, self).__init__()
    @property
    def args(self):
        return chain([self.this], self._args)
    @property
    def leafDeps(self):
        return chain( self.this.leafDeps, chain.from_iterable( arg.leafDeps for arg in self._args ) )
    @property
    def result(self):
        retTypeN = next( tok.strip("*&") for tok in self._mp.func_doc.split() if tok != "const" )
        return makeStubForType(retTypeN, self)
    def __repr__(self):
        return "CallMemberMethod({0!r}, {1!r}, ({2}))".format(self.this, self.name, ", ".join(repr(arg) for arg in self._args))
    def __eq__(self, other):
        return isinstance(other, CallMemberMethod) and ( self.this == other.this ) and ( self.name == other.name ) and ( len(self._args) == len(other._args) ) and all( ( sa == oa ) for sa, oa in izip(self._args, other._args))
    # backends
    def _get_TTreeDrawStr(self):
        return "{0}.{1}({2})".format(self.this.get_TTreeDrawStr(), self.name, ", ".join(arg.get_TTreeDrawStr() for arg in self._args))

mathOpFuns_TTreeDrawStr = {
      "add"      : lambda *args : "( {0} )".format(" + ".join(arg.get_TTreeDrawStr() for arg in args))
    , "multiply" : lambda *args : "( {0} )".format(" * ".join(arg.get_TTreeDrawStr() for arg in args))
    , "subtract" : lambda a1,a2 : "( {0} - {1} )".format(a1.get_TTreeDrawStr(), a2.get_TTreeDrawStr())
    , "divide"   : lambda a1,a2 : "( {0} / {1} )".format(a1.get_TTreeDrawStr(), a2.get_TTreeDrawStr())
    #
    , "lt" : lambda a1,a2 : "( {0} <  {1} )".format(a1.get_TTreeDrawStr(), a2.get_TTreeDrawStr())
    , "le" : lambda a1,a2 : "( {0} <= {1} )".format(a1.get_TTreeDrawStr(), a2.get_TTreeDrawStr())
    , "eq" : lambda a1,a2 : "( {0} == {1} )".format(a1.get_TTreeDrawStr(), a2.get_TTreeDrawStr())
    , "ne" : lambda a1,a2 : "( {0} != {1} )".format(a1.get_TTreeDrawStr(), a2.get_TTreeDrawStr())
    , "gt" : lambda a1,a2 : "( {0} >  {1} )".format(a1.get_TTreeDrawStr(), a2.get_TTreeDrawStr())
    , "ge" : lambda a1,a2 : "( {0} >= {1} )".format(a1.get_TTreeDrawStr(), a2.get_TTreeDrawStr())
    , "and" : lambda *args : "( {0} )".format(" && ".join(a.get_TTreeDrawStr() for a in args))
    , "or"  : lambda *args : "( {0} )".format(" || ".join(a.get_TTreeDrawStr() for a in args))
    , "not" : lambda a : "( ! {0} )".format(a.get_TTreeDrawStr())
    #
    , "abs" : lambda arg : "std::abs( {0} )".format(arg.get_TTreeDrawStr())
    , "log" : lambda arg : "std::log( {0} )".format(arg.get_TTreeDrawStr())
    , "log10" : lambda arg : "std::log10( {0} )".format(arg.get_TTreeDrawStr())
    , "max" : lambda a1,a2 : "std::max( {0}, {1} )".format(a1.get_TTreeDrawStr(), a2.get_TTreeDrawStr())
    , "min" : lambda a1,a2 : "std::min( {0}, {1} )".format(a1.get_TTreeDrawStr(), a2.get_TTreeDrawStr())
    }

class MathOp(TupleOp):
    """
    Mathematical function N->1, e.g. sin, abs, ( lambda x, y : x*y )
    """
    __slots__ = ("outType", "op", "_args")
    def __init__(self, op, *args, **kwargs):
        self.outType = kwargs.pop("outType", "Double_t")
        assert len(kwargs) == 0
        self.op = op
        self._args = tuple(adaptArg(a, typeHint="Double_t") for a in args)
        super(MathOp, self).__init__()
    @property
    def args(self):
        return self._args
    @property
    def leafDeps(self):
        return chain.from_iterable(arg.leafDeps for arg in self._args)
    @property
    def result(self):
        return makeStubForType(self.outType, self)
    def __repr__(self):
        return "{0}({1})".format(self.op, ", ".join(repr(arg) for arg in self._args))
    def __eq__(self, other):
        return isinstance(other, MathOp) and ( self.outType == other.outType ) and ( self.op == other.op ) and ( len(self._args) == len(other._args) ) and all( ( sa == oa ) for sa, oa in izip(self._args, other._args))
    # no TTreeDrawStr backend, this is an abstract base class
    # convention: wrap *result*, if all parts do that, we have not too many excess parentheses
    def _get_TTreeDrawStr(self):
        return mathOpFuns_TTreeDrawStr[self.op](*self._args)

## FIXME this can be done by MathOp, as things are now
# also of this type, for now ( control flow -> may be lazy, dep. on implementation )
class SwitchOp(MathOp): ## may need another layer of indirection around...
    """
    Ternary operator if cond then trueBranch else falseBranch
    """
    __slots__ = ()
    def __init__(self, cond, trueBr, falseBr):
        if isinstance(trueBr, TupleStub) and isinstance(falseBr, TupleStub):
            assert trueBr._typeName == falseBr._typeName
        super(SwitchOp, self).__init__("switch", adaptArg(cond, typeHint=boolType), trueBr, falseBr, outType=(trueBr._typeName if isinstance(trueBr, TupleStub) else falseBr._typeName if isinstance(falseBr, TupleStub) else "Double_t"))
    # backends
    def _get_TTreeDrawStr(self):
        return "( {0} ? {1} : {2} )".format(*(arg.get_TTreeDrawStr() for arg in self._args))
        #return "( {0}*{1} + ( ! {0} )*{2} )".format(*(arg.get_TTreeDrawStr() for arg in self._args))

class Adaptor(object):
    """
    Helper class: compose two single-argument callables
    """
    __slots__ = ("__weakref__", "getter", "worker")
    def __init__(self, getter, worker):
        self.getter = getter
        self.worker = worker
    def __call__(self, arg):
        return self.worker(self.getter(arg))
    def __repr__(self):
        return "Adaptor({0!r}, {1!r})".format(self.getter, self.worker)

class op(object):
    """
    pseudo-module
    """
    @staticmethod
    def NOT(sth):
        return MathOp("not", sth, outType=boolType).result
    @staticmethod
    def AND(*args):
        return MathOp("and", *args, outType=boolType).result
    @staticmethod
    def OR(*args):
        return MathOp("or", *args, outType=boolType).result
    @staticmethod
    def switch(test, trueBranch, falseBranch):
        return SwitchOp(test, trueBranch, falseBranch).result
    @staticmethod
    def extMethod(name):
        return MethodStub(name) ## TODO somehow take care of includes as well
    @staticmethod
    def extVar(typeName, name):
        return ExtVar(typeName, name).result
    @staticmethod
    def construct(typeName, args):
        return Construct(typeName, args).result
    @staticmethod
    def initList(typeName, elmName, elms):
        return InitList(typeName, elmName, elms).result
    @staticmethod
    def abs(sth):
        return MathOp("abs", sth, outType="Float_t").result
    @staticmethod
    def sign(sth):
        return op.switch(sth!=0., sth/op.abs(sth), 0.)
    @staticmethod
    def sum(*args, **kwargs):
        return MathOp("add", *args, outType=kwargs.pop("outType", "Float_t")).result
    @staticmethod
    def product(*args):
        return MathOp("multiply", *args, outType="Float_t").result
    @staticmethod
    def log(sth):
        return MathOp("log", sth, outType="Float_t").result
    @staticmethod
    def log10(sth):
        return MathOp("log10", sth, outType="Float_t").result
    @staticmethod
    def max(a1,a2):
        return MathOp("max", a1, a2, outType="Float_t").result
    @staticmethod
    def min(a1,a2):
        return MathOp("min", a1, a2, outType="Float_t").result
    @staticmethod
    def in_range(low, arg, up):
        return op.AND(arg > low, arg < up)

    ## range operations
    @staticmethod
    def len(sth):
        return sth.__len__() ## __builtins__.len check it is an integer
    @staticmethod
    def rng_sum(rng, fun, start=makeConst(0., "Float_t")):
        return Reduce(rng, start, ( lambda fn : ( lambda res, elm : res+fn(elm) ) )(fun), valueType=start._typeName, isAssociative=True).result
    @staticmethod
    def rng_count(rng, pred): ## specialised version of sum, for convenience
        return Reduce(rng, makeConst(0, "Int_t"), ( lambda prd : ( lambda res, elm : res+op.switch(prd(elm), makeConst(1, "Int_t"), makeConst(0, "Int_t")) ) )(pred), valueType="Int_t", isAssociative=True).result
    @staticmethod
    def rng_product(rng, fun):
        return Reduce(rng, makeConst(1., "Float_t"), ( lambda fn : ( lambda res, elm : res*fn(elm) ) )(fun), valueType="Float_t", isAssociative=True).result
    @staticmethod
    def rng_max(rng, fun):
        return Reduce(rng, makeConst(float("-inf"), "Float_t"), ( lambda fn : ( lambda res, elm : op.max(res, fn(elm)) ) )(fun), valueType="Float_t", isAssociative=True).result
    @staticmethod
    def rng_min(rng, fun):
        return Reduce(rng, makeConst(float("+inf"), "Float_t"), ( lambda fn : ( lambda res, elm : op.min(res, fn(elm)) ) )(fun), valueType="Float_t", isAssociative=True).result
    ##
    @staticmethod
    def rng_max_element_by(rng, fun=lambda elm : elm):
        ## stick with the convention: only work with indices referring to the object containers (not to the position in the one with selected object indices)
        cont = rng._getCapWithAttr("__getitem__")._cont if isRefList(rng) else rng
        return cont[Reduce(rng, makeConst(-1, "Int_t"),
            ( lambda fn,lst :
                ( lambda ires, elm : op.switch(fn(elm) > fn(lst[ires]), elm.i, ires) )
            )(fun, cont),
            valueType="Int_t", isAssociative=True).result] ## FIXME if we want to automatically check the validity of this, probably need to cache it in the GetItem that is created here
    @staticmethod
    def rng_min_element_by(rng, fun=lambda elm : elm):
        ## stick with the convention: only work with indices referring to the object containers (not to the position in the one with selected object indices)
        cont = rng._getCapWithAttr("__getitem__")._cont if isRefList(rng) else rng
        return cont[Reduce(rng, makeConst(-1, "Int_t"),
            ( lambda fn,lst :
                ( lambda ires, elm : op.switch(op.OR(ires < 0, fn(elm) < fn(lst[ires])), elm.i, ires) )
            )(fun, cont),
            valueType="Int_t", isAssociative=True).result]
    ## early-exit algorithms
    @staticmethod
    def rng_any(rng, fun=lambda elm : elm):
        return Next(rng, fun).isValid()
    @staticmethod
    def rng_find(rng, pred=lambda elm : makeConst("true", boolType)):
        cont = rng._getCapWithAttr("__getitem__")._cont if isRefList(rng) else rng
        return cont[op.extMethod("*")(Next(rng, pred))]


    ## Kinematics and helpers
    @staticmethod
    def invariant_mass(*args):
        return op.extMethod("ROOT::Math::VectorUtil::InvariantMass")(*args)
    @staticmethod
    def invariant_mass_squared(*args):
        return op.extMethod("ROOT::Math::VectorUtil::InvariantMass2")(*args)
    @staticmethod
    def deltaPhi(a1, a2):
        return op.extMethod("Kinematics::deltaPhi")(a1, a2)
    @staticmethod
    def deltaR(a1, a2):
        return op.extMethod("Kinematics::deltaR")(a1, a2)
    @staticmethod
    def signedDeltaPhi(a1, a2):
        return op.extMethod("Kinematics::signedDeltaPhi")(a1, a2)
    @staticmethod
    def signedDeltaEta(a1, a2):
        return op.extMethod("Kinematics::signedDeltaEta")(a1, a2)

## related helpers
def makeExprAnd(listOfReqs):
    """ op.AND for expressions (helper for histfactory etc.)
    """
    if len(listOfReqs) > 1:
        return adaptArg(op.AND(*listOfReqs))
    elif len(listOfReqs) == 1:
        return listOfReqs[0]
    else:
        return adaptArg(makeConst("true", boolType), typeHint=boolType)
def makeExprProduct(listOfFactors):
    """ op.product for expressions (helper for histfactory etc.)
    """
    if len(listOfFactors) > 1:
        return adaptArg(op.product(*listOfFactors))
    elif len(listOfFactors) == 1:
        return listOfFactors[0]
    else:
        return adaptArg(makeConst(1., "float"), typeHint="float")

def levelsAbove(prevLevels, thisLevel):
    levels = [ SmartTupleStub._RefToOther(rf._name, GoUpBy(rf._refGetter.nSteps+1)) for rf in prevLevels ]
    levels.append(SmartTupleStub._RefToOther(thisLevel, GoUpBy(1)))
    return levels

def addIntoHierarchy(name, smartLeaf, parent, hierarchy, capabilities=[]):
    for cap in capabilities+list(copy.copy(cap) for cap in hierarchy):
        smartLeaf._addCapability(cap)
    parent._registerSmartLeaf(name, smartLeaf)
    return smartLeaf

def addRefListFacade(parent, name, collection):
    fac = LeafFacade(name, parent)
    base = getattr(parent, name)
    #fac = SmartTupleStub(base._typeName, parent=parent) ## TODO may need to customise a little bit
    fac._addCapability(SmartTupleStub._RefList(base, collection))
    parent._registerSmartLeaf(name, fac)

def addWPSelGroup(name, prefix, collection, parent, hierarchy):
    grp = BranchGroupStub(prefix) ## TODO __dir__ is not so happy with this, maybe need a (fairly simple) customisation of SmartTupleStub and/or BranchGroupStub
    addIntoHierarchy(name, grp, parent, hierarchy)
    for wp in grp._availLeafs():
        #if not wp.startswith("_"): ## TODO improve a bit on that
        if wp.startswith("I") or wp.startswith("B"):
            if hasattr(getattr(grp, wp), "__len__"):
                addRefListFacade(grp, wp, collection)
            else:
                grp._addCapability(SmartTupleStub._RefToOther(wp, (lambda coll, iwp : ( lambda wpgrp : collection[wpgrp._get(iwp)] ))(collection, wp)))
    return grp

def addWPWPSelGroup(name, prefix, collectionGroup, parent, hierarchy):
    ## FIXME can be removed when truth-matching gives jet index back (instead of index in selected-jets container)
    grp = BranchGroupStub(prefix) ## TODO __dir__ is not so happy with this, maybe need a (fairly simple) customisation of SmartTupleStub and/or BranchGroupStub
    addIntoHierarchy(name, grp, parent, hierarchy)
    for wp in grp._availLeafs():
        #if not wp.startswith("_"): ## TODO improve a bit on that
        if wp.startswith("I") or wp.startswith("B"):
            if hasattr(getattr(grp, wp), "__len__"):
                addRefListFacade(grp, wp, getattr(collectionGroup, wp))
            else:
                grp._addCapability(SmartTupleStub._RefToOther(wp, (lambda collGrp, iwp : ( lambda wpgrp : getattr(collGrp, iwp)[wpgrp._get(iwp)] ))(collectionGroup, wp)))
    return grp

class LeafFacade(SmartTupleStub):
    __slots__ = ("_name",)
    def __init__(self, name, parent=None):
        self._name = name
        typeName = ( getattr(parent, name)._typeName if parent is not None else "struct" )
        super(LeafFacade, self).__init__(typeName, parent=parent)
    ### main use: say we only hide one leaf. All other functionality is in the base class and works fine
    def _listedLeafs(self): ## including own
        lst = self._listedLeafsBelow()
        lst.update(self._name)
        return lst
        ## FIXME this is wrong - do not want to inherit all branches from the parent

class SmartObjectStub(ObjectStub):
    """
    Imitate an object, with additional methods/properties
    """
    def __init__(self, parent, typeName, caps=None, parentStub=None):
        ## NOTE: inherits _typ (PyROOT type)
        self._caps = caps
        self._parentStub = parentStub
        super(SmartObjectStub, self).__init__(parent, typeName)
    def __getattr__(self, name):
        for cap in self._caps:
            if name in cap._dir:
                cp = copy.copy(cap)
                cp._parent = self
                return getattr(cp, name)

        hlp = self._parentStub._getCapWithAttr(name)
        if hlp:
            return getattr(hlp, name)

        return self._get(name) ## fallback (which is the most common)
    def __dir__(self): ## including own
        return list(self._availLeafs())
    def _availLeafs(self):
        avail = set()
        for hlp in self._caps:
            avail.update(hlp._dir)
        for hlp in self._parentStub._extraCap:
            avail.update(hlp._dir)
        for att in dir(self._typ):
            if not att.startswith("_"):
                avail.add(att)
        return avail
    def __repr__(self):
        return "SmartObjectStub({0!r}, {1!r})".format(self._parent, self._typeName)

    from collections import MutableMapping
    class Map(MutableMapping):
        """
        usage: instStub = myMap[typNm](parent)
        """
        def __init__(self, items):
            self._capDict = dict(items)
        def __iter__(self):
            for k in self._capDict:
                yield k
        def __len__(self):
            return len(self._capDict)
        def __setitem__(self, k, v):
            self._capDict[k] = v
        def __delitem__(self, k):
            del self._capDict[k]
        def get(self, k): ## without decoration
            return self._capDict[k]
        def __getitem__(self, typeName):
            if typeName in self._capDict:
                return ( lambda typNm, cap :
                            ( lambda p,pStub=None : SmartObjectStub(p, typNm, caps=cap, parentStub=pStub) )
                       )(typeName, self._capDict[typeName])
            else:
                raise KeyError("Type with name {} not found".format(typeName))

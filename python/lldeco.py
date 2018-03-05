"""
Helper classes for llX tree decorators
"""
__all__ = ("leptonAdaptor", "onlyMuon", "onlyElectron", "LeptonScaleFactor", "DiLeptonScaleFactor")

from .treedecorators import PODStub, SwitchOp

class LeptonStub(PODStub):
    """ Reference to a lepton (electron or muon), or anything operation on it """
    __slots__ = ("el", "mu")
    def __init__(self, parent, el=None, mu=None):
        self.el = el if el is not None else parent.record.electrons[parent.idx]
        self.mu = mu if mu is not None else parent.record.muons[parent.idx]
        tpNm = self.el._typeName
        assert self.mu._typeName == tpNm
        super(LeptonStub, self).__init__(parent, tpNm)
    @property
    def op(self):
        return SwitchOp(self._parent.isEl, self.el, self.mu)
    def _get(self, name):
        try:
            return LeptonStub(self._parent, el=getattr(self.el, name), mu=getattr(self.mu, name))
        except Exception, e:
            raise AttributeError("Problem getting attribute '{0}' for LeptonStub with {1} and {2}: {3}".format(name, self.el, self.mu, str(e)))
    def __call__(self, *args):
        try: ## TODO the same as for _binaryOp
            return LeptonStub(self._parent, el=self.el(*args), mu=self.mu(*args))
        except Exception, e:
            raise AttributeError("Problem with __all__ on LeptonStub with {0} and {1}: {2}".format(self.el, self.mu, str(e)))
    def __repr__(self):
        return "LeptonStub({0!r}, el={1!r}, mu={2!r})".format(self._parent, self.el, self.mu)

    def _binaryOp(self, opName, other, outType="Double_t"):
        if isinstance(other, LeptonStub) and ( self._parent == other._parent ):
            return LeptonStub(self._parent,
                    el=self.el._binaryOp(opName, other.el, outType=outType),
                    mu=self.mu._binaryOp(opName, other.mu, outType=outType))
        else:
            return super(LeptonStub, self)._binaryOp(opName, other, outType=outType)

def onlyElectron(fun, muonValue=-1.):
    """ apply fun to the electron (or fill the muon value) """
    return lambda l : op.switch(l.isEl, fun(l.L.el), muonValue)
def onlyMuon(fun, electronValue=-1.):
    """ apply fun to the muon (or fill the electron value) """
    return lambda l : op.switch(op.NOT(l.isEl), fun(l.L.mu), electronValue)
def leptonAdaptor(elFun, muFun):
    """ apply fun to the electron or the muon, as applicable """
    return lambda l : op.switch(l.isEl, elFun(l.L.el), muFun(l.L.mu))

from .treedecorators import SmartTupleStub

class LeptonRef(SmartTupleStub._RefToOther):
    __slots__ = tuple()
    def __init__(self, name, parent=None):
        super(LeptonRef, self).__init__(name, None, parent=parent)
    def __getattr__(self, name):
        if name == self._name:
            return LeptonStub(self._parent)
        else:
            raise AttributeError("No attribute called {0!r} for object {1!r}".format(name, self))
    def __repr__(self):
        return "LeptonRef({0!r}, parent={1!r})".format(self._name, self._parent)

def prodIfIterable(sfArg, **kwargs):
    return (( lambda x : op.product(*(iw(x, **kwargs) for iw in sfArg)) )
              if hasattr(sfArg, "__iter__") else
            ( lambda x : sfArg(x, **kwargs) ))

from .treedecorators import op, boolType, makeConst
class LeptonScaleFactor(object):
    def __init__(self, elSF, muSF, cache=True):
        self.elSF = elSF
        self.muSF = muSF
        self.cache = cache
    def __call__(self, lepton, variation="Nominal"):
        kwargs = dict(withMCCheck=False, precalc=False, variation=variation)
        expr = op.switch(op.extVar(boolType, "runOnMC")
                , leptonAdaptor(prodIfIterable(self.elSF, **kwargs), prodIfIterable(self.muSF, **kwargs))(lepton)
                , makeConst(1., "Float_t")
                )
        if self.cache:
            import uuid ## caching
            expr._parent.uname = "sf_{0}".format(str(uuid.uuid4()).replace("-", "_"))
        return expr

class DiLeptonScaleFactor(object):
    class _LL(object):
        def __init__(self, l1, l2):
            self.l1 = l1
            self.l2 = l2

    def __init__(self, elelSF=None, elmuSF=None, muelSF=None, mumuSF=None, cache=True):
        assert all(arg is not None for arg in (elelSF, elmuSF, muelSF, mumuSF))
        self.elelSF = elelSF
        self.elmuSF = elmuSF
        self.muelSF = muelSF
        self.mumuSF = mumuSF
        self.cache = cache
    def __call__(self, ll, variation="Nominal"):
        kwargs = dict(withMCCheck=False, precalc=False, variation=variation)
        expr = op.switch(op.extVar(boolType, "runOnMC")
                , op.switch(ll.isElEl, prodIfIterable(self.elelSF, **kwargs)(DiLeptonScaleFactor._LL(ll.l1.L.el, ll.l2.L.el))
                , op.switch(ll.isElMu, prodIfIterable(self.elmuSF, **kwargs)(DiLeptonScaleFactor._LL(ll.l1.L.el, ll.l2.L.mu))
                , op.switch(ll.isMuEl, prodIfIterable(self.muelSF, **kwargs)(DiLeptonScaleFactor._LL(ll.l1.L.mu, ll.l2.L.el))
                , op.switch(ll.isMuMu, prodIfIterable(self.mumuSF, **kwargs)(DiLeptonScaleFactor._LL(ll.l1.L.mu, ll.l2.L.mu))
                , makeConst(1., "Float_t")))))
                , makeConst(1., "Float_t")
                )
        if self.cache:
            import uuid ## caching
            expr._parent.uname = "sf_{0}".format(str(uuid.uuid4()).replace("-", "_"))
        return expr

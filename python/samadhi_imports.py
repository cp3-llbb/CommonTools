""" Common helper module to manipulate sys.path and import SAMADhi (inside a CMSSW environment) """

import sys
# Add default ingrid storm package
sys.path.append('/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/lib/python2.7/site-packages/storm-0.20-py2.7-linux-x86_64.egg')
sys.path.append('/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/lib/python2.7/site-packages/MySQL_python-1.2.3-py2.7-linux-x86_64.egg')

import os

try:
    CMSSW_BASE = os.environ['CMSSW_BASE']
    if CMSSW_BASE == "":
        raise ImportError("Environment problem: CMSSW_BASE is empty")
    SCRAM_ARCH = os.environ['SCRAM_ARCH']
    sys.path.append(os.path.join(CMSSW_BASE,'bin', SCRAM_ARCH))
except KeyError, e:
    raise ImportError("This script needs the CMSSW environment to run, please run `cmsenv` first (error when getting CMSSW environment variable {0})".format(str(e))
)

try:
    import SAMADhi
    from SAMADhi import Dataset, Sample, DbStore
except ImportError, e:
    raise ImportError("Could not import the necessary symbols from the SAMADhi package ({0})".format(str(e)))

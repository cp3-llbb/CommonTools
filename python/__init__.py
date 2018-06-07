__all__ = ("pathCommonTools", "pathCP3llbb", "pathCMS")
import os.path
pathCommonTools = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
pathCP3llbb = os.path.dirname(os.path.abspath(pathCommonTools))
_pathCMS_paths = os.path.dirname(os.path.dirname(pathCP3llbb))
import os
_pathCMS_env = os.getenv("CMSSW_BASE")
pathCMS = _pathCMS_paths
if _pathCMS_env == "":
    print("Warning: Could not get CMSSW_BASE variable from the environment")
elif _pathCMS_env != _pathCMS_paths:
    print("Warning: CommonTools is not using the CMSSW release version from $CMSSW_BASE ({0} versus {1}), using the former".format(_pathCMS_paths, _pathCMS_env))
    pathCMS = _pathCMS_paths

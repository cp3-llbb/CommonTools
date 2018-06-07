#!/bin/sh
#
# Creates a scram-like (symlinked) python install directory for *Tools packages
# in the equivalent of ${CMSSW_BASE}/src/install_python (or ${PREFIX}/install_python, if PREFIX is defined)
#
thisscript="$(realpath ${0})"
commontoolspath="$(dirname ${thisscript})"
cp3llbbpath="$(dirname ${commontoolspath})"
if [[ "$(basename ${cp3llbbpath})" != "cp3_llbb" ]]; then
  echo "Directory above CommonTools is not called cp3_llbb, aborting"
  exit 1
fi
basepath="$(dirname ${cp3llbbpath})"
if [[ -z "${PREFIX}" ]]; then
  PREFIX="${basepath}"
fi
installpath="${PREFIX}/install_python"
if [[ -a "${installpath}" ]]; then
  echo "Install path ${installpath} already exists, aborting"
  exit 1
fi
echo "Installing into ${installpath}, make sure to add it to PYTHONPATH as well"
mkdir -p "${installpath}"
pushd "${basepath}" > /dev/null
for pkgpy in */*Tools/python; do
  pkgpath_py="${basepath}/${pkgpy}"
  if [[ ! -d "${pkgpath_py}" ]]; then
    echo "ASSERT FAILURE: ${pkgpath_py}"
    exit 1
  fi
  pkgname_full="$(dirname ${pkgpy})"
  pkgname="$(basename ${pkgname_full})"
  hatname="$(dirname  ${pkgname_full})"
  hatinstalldir="${installpath}/${hatname}"
  mkdir -p "${hatinstalldir}"
  hatinitpy="${hatinstalldir}/__init__.py"
  if [[ ! -f "${hatinitpy}" ]]; then
    echo "" > "${hatinitpy}"
  fi
  ln -s "${pkgpath_py}" "${hatinstalldir}/${pkgname}"
  echo "Installed ${pkgname_full}"
done

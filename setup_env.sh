# No shebang. Must be sourced

case $(hostname) in
    ingrid*) module purge
        module load gcc/gcc-4.9.1-sl6_amd64
        module load python/python27_sl6_gcc49
        module load boost/1.57_sl6_gcc49
        module load root/6.04.00-sl6_gcc49
        ;;

    lxplus*) source /cvmfs/cms.cern.ch/slc6_amd64_gcc491/external/gcc/4.9.1-cms/etc/profile.d/init.sh
        source /cvmfs/cms.cern.ch/slc6_amd64_gcc491/lcg/root/6.02.00-cms4/etc/profile.d/init.sh
        source /cvmfs/cms.cern.ch/slc6_amd64_gcc491/external/boost/1.57.0-cms/etc/profile.d/init.sh
        source /cvmfs/cms.cern.ch/slc6_amd64_gcc491/external/libjpg/8b-cms/etc/profile.d/init.sh
        source /cvmfs/cms.cern.ch/slc6_amd64_gcc491/external/libpng/1.6.16/etc/profile.d/init.sh
        source /cvmfs/cms.cern.ch/slc6_amd64_gcc491/external/xrootd/4.0.4/etc/profile.d/init.sh
        source /cvmfs/cms.cern.ch/slc6_amd64_gcc491/lcg/root/6.02.00-odfocd/etc/profile.d/init.sh
        source /cvmfs/cms.cern.ch/slc6_amd64_gcc491/external/pcre/7.9__8.33-cms/etc/profile.d/init.sh
        source /cvmfs/cms.cern.ch/slc6_amd64_gcc491/external/xz/5.0.3__5.1.2alpha-cms/etc/profile.d/init.sh
        source /cvmfs/cms.cern.ch/slc6_amd64_gcc491/external/zlib/1.2.8-cms/etc/profile.d/init.sh
        ;;
esac

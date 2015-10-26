# histFactory

A tool to create histograms from trees

## Setup instructions

You can use this tool either in a standalone way or within CMSSW. Within CMSSW gives more satisfactory results as you'll have for free dictionaries generation for the cp3-llbb framework and analyses.

In both case, you just have to clone the `CommonTools` repository:

 - In standalone mode, you can clone the repository where you want
 - In CMSSW mode, the best is to clone the repository in the `src/cp3-llbb` folder.

If inside a CMSSW env., cmake will automatically look for dictionaries in all folders inside the `src/cp3-llbb` folder. A dictionary is identified by a set of two files, `src/classes.h` and `src/classes_def.h`. If these files are found for a given folder, the dictionary will be built automatically.

In standalone mode, you have to make sure to use a C++11 compatible compiler, and you must have `python-dev` and `ROOT` available. The best way on `ingrid` and `lxplus` is to source the `setup_env.sh` script.

## Build instructions

```bash
mkdir build
cd build

# This step takes a bit of time as the externals will be built.
cmake ..

make
```

## How to use

### Setup environment

 - Standalone mode: on `ingrid` and `lxplus`, source `setup_env.sh`
 - In CMSSW mode: a `cmsenv` is enough

### Create histograms

```bash
./createHistoWithMultiDraw.exe -d ../samples/mysamples.json [-o outputdir] -- ../plots/myplots.json
```

### Use condor to fill histograms

See condorExample.py for usage.

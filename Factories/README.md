# Factories

A tool to create histograms and trees in an automated way

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

You have the choice to either create histograms or trees. This choice is made by running the correct executable (either `histFactory.exe` to create histograms, or `treeFactory.exe` to create a tree)

### Setup environment

 - Standalone mode: on `ingrid` and `lxplus`, source `setup_env.sh`
 - In CMSSW mode: a `cmsenv` is enough

### Use condor

See condorExample.py for usage.

### On-the-fly code generation

Steps are the same if you want to generate trees or histograms. Details below assume you want to create histograms. If it's not the case, simply replace `plotter` by `skimmer` in the instructions.

 1) First, the code for the plotter needs to be generated. For that, you need to run `createPlotter.exe`. This will create a bunch of C++ code responsible for creating all the histograms you specified. The specification of these histograms is still done in a python script, as before.

 2) Once the code is generated, it needs to be compiled in order to produce an executable. This executable will produce the plots for a given sample. The specification of the samples is still done in JSON, as before.

An helper script is available to create a viable working directory for the plotter (some dependencies are needed if you want to successfully build the code). This script, `createPlotter.sh`, is created automatically in your build directory after you execute the `cmake` command. An example of usage is:

```
./createPlotter.sh <skeleton ROOT file> <python configuration file> <output directory>
```

**Note**: Outside of CMSSW, you need to have [TreeWrapper](https://github.com/blinkseb/TreeWrapper) installed somewhere (say in `TW`). Then, to be able to build the generated code (or run `createPlotter.sh`), you'll need the following environment variables to be set:
 - `CMAKE_LIBRARY_PATH` to `$TW/.libs`
 - `CMAKE_INCLUDE_PATH` to `$TW/interface`

3 arguments are needed:
 1) `skeleton ROOT file`: The absolute path of a ROOT file from one of your datasets. It's needed because of code creating the plotting code needs to know the structure of the tree to correctly identify what is a branch in your plot / cut strings. This can be *any* file from *any* dataset, it really does not matter: you just have to ensure that the tree structure is correct.

 2) `python configuration file`: Path to your python script generating the list of plots.

 3) `output directory`: The name of the directory where the code of the plotter will be created. This directory must not exist, otherwise the script will exit with an error message.


In addition to generate the code, the script will also build it for you. You should now have a working executable named `plotter.exe` inside the `build` directory of the `output directory`.

The last step is to create the plots. You need to run the plotter like this

```
./plotter.exe -d <JSON file>
```

where `JSON file` is a path to a JSON file describing your dataset. Multiple datasets per file are supported.

You can find example of valid python file for both histograms and trees, as well as a sample JSON file in the `test` folder.

### Python file format

#### Common to tree and histograms mode

The following variables can be defined, and are not mandatory:
 - `include_directories`: (list of strings) Paths to additional include directories. Used in conjonction of the `headers` variable, to specify where to look for the headers. **Warning**: only absolute paths are supported
 - `headers`: (list of strings) List of headers to include in the generated code.
 - `library_directories`: (list of strings) Paths to additional library directories. Used in conjonction of the `libraries` variable, to specify additional paths where cmake will look for libraries. **Warning**: only absolute paths are supported
 - `libraries`: (list of strings) List of additional libraries to link against. **Warning**: only the name of the library is needed (without the `lib` prefix or the `.so` extension)
 - `sources`: (list of strings) Paths to additional source files to be compiled and linked with the executable. **Warning**: only absolute paths are supported
 - `extra_branches`: (list of strings) Branches to be read from the input files. Useful if branches are not used explicitly for filling the histograms (and thus would not be read by the plotter), but still have to be read to perform additional actions (for instance, call functions defined in the variables below).
 - `code_before_loop`: (string) Code inserted in the plotter, before the loop on the events starts.
 - `code_in_loop`: (string) Code inserted in the actual loop over the events (before the histograms are filled)
 - `code_after_loop`: (string) Code inserted after the loop over the events.
Specified paths cans be absolute, relative from the current directory, or relative from the directory where the python script is stored.

In case a single sample is to be reweighted to produce different outputs, another dictionary can be defined: `sample_weights`. Each key is the name of the resulting reweighting, and the corresponding entry gives the weight to be used (any valid C++ code).

#### Generating histograms

An example of a valid python script is given in `test/plots.py`. The script needs to declare a global variable named `plots`, which is a list of dictionaries containing these keys:

 - `name` (mandatory): The name of the histogram inside the output file
 - `variable` (mandatory): The formula used to fill the histogram. Histograms can be 1-, 2- or 3-dimensional. For multi-dimensional histograms, the variables to be used for each dimension are to be separated by `:::`.
 - `plot_cut` (optional, default to `"1"`): the cut to apply before filling the histogram
 - `binning` (mandatory): String defining the binning to be used for each dimension. Each dimension can use fixed or variable-sized binning, for instance: `(10, 0, 5, 3, { 0, 2, 2.5, 3 })` defines 10 fixed-sized bins from `x=0` to `x=5` and 3 variable-size bins over `y`, where the bin edges are defined in the array `{}`.
 - `folder` (optional): Folder inside the output file where the histogram is to be saved.
 - `normalize-to`: Name of an alternate normalisation constant to be used (given in the input JSON)


#### Generating a tree

An example of a valid python script is given in `test/tree.py`. The script needs to declare a global variable named `tree`, which is a dictionary containing these keys:

 - `name` (mandatory): the name of the tree inside the output file
 - `cut` (optional, default to `"1"`): the cut to apply before filling the tree
 - `clone` (optional, default to `False`): if set to `True`, the input tree is cloned into the output tree.
 - `branches` (mandatory): a list of branches to create. Format of this list is given below.

The value of the `branches` key is a list of dictionaries. Each dictionary describe a branch to create, with the following format:

 - `name`: the name of the branch
 - `variable`: the formula used to evaluate the branch value.
 - `type`: the type of the branch. Default to `float`


### JSON file format

The entries in the JSON file passed to either `plotter.exe` or `skimmer.exe` can have the following fields:
 - `is-data` (default to `False`): specifies if the sample is data or not. No event weight is applied in the former case
 - `sample_cut` (default to `1`): apply cut on the whole sample
 - `tree_name` (default to `t`): name of the TTree from which to read the data
 - `db_name` (defaults to the sample name): name of the sample in the DB.
 - `output_name` (defaults to the `db_name`): "base" name of the output file
 - `suffix` (default to `_histos` for HistFactory, and `_skim` for TreeFactory): suffix appended to the "base" output name
 - `cross-section` (default to `1`): stored as TParameter in the output file
 - `event-weight-sum` (default to `1`): stored as TParameter in the output file. In HistFactory, histograms are scaled by `cross-section/event-weight-sum`
 - `extras-event-weight-sum` (optional): Dictionary of extra event weight sums to use (for systematics, for instance). By default the only key is `"nominal"`, with value `event-weight-sum`
 - `sample-weight` (optional): Name of the special per-event sample weight to be used (see above, Python file format)
 - `files`: List of files as input, or:
 - `path`: Take all `.root` files in this directory
 - `event-start` (default `0`): first event to be read
 - `event-end` (default last): last event to be read

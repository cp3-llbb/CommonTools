// Read some trees, output an histos
// A. Mertens (September 2015)

#include <Python.h>

#include <json/json.h>

#include <iostream>
#include <fstream>
#include <memory>
#include <cstdio>

#include <TVirtualTreePlayer.h>
#include <TMultiDrawTreePlayer.h>
#include <TChain.h>
#include <TTree.h>
#include <TFile.h>
#include <TApplication.h>
#include <TObject.h>  // For kWriteDelete

#include <tclap/CmdLine.h>

struct Plot {
    std::string name;
    std::string variable;
    std::string plot_cut;
    std::string binning;
};

struct Dataset {
    std::string name;
    std::string db_name;
    std::string output_name;
    std::string tree_name;
    std::string path;
    std::vector<std::string> files;
    std::string cut;

    // Futur
    std::map<std::string, std::string> options;
};

#define CHECK_AND_GET(var, obj) if (PyDict_Contains(value, obj) == 1) { \
    PyObject* item = PyDict_GetItem(value, obj); \
    if (! PyString_Check(item)) {\
        std::cerr << "Error: the '" << PyString_AsString(obj) << "' value must be a string" << std::endl; \
        return false; \
    } \
    var = PyString_AsString(item); \
} else { \
    std::cerr << "Error: '" << PyString_AsString(obj) << "' key is missing" << std::endl; \
    return false; \
}

bool plot_from_PyObject(PyObject* value, Plot& plot) {
    static PyObject* PY_NAME = PyString_FromString("name");
    static PyObject* PY_VARIABLE = PyString_FromString("variable");
    static PyObject* PY_PLOT_CUT = PyString_FromString("plot_cut");
    static PyObject* PY_BINNING = PyString_FromString("binning");

    if (! PyDict_Check(value)) {
        std::cerr << "Error: plots dictionnary value must be a dictionnary" << std::endl;
    }

    CHECK_AND_GET(plot.name, PY_NAME);
    CHECK_AND_GET(plot.variable, PY_VARIABLE);
    CHECK_AND_GET(plot.plot_cut, PY_PLOT_CUT);
    CHECK_AND_GET(plot.binning, PY_BINNING);

    return true;
}

bool execute(const std::vector<Dataset>& datasets, const std::vector<std::string>& config_file, bool python, std::string output_dir = "");
bool parse_datasets(const std::string& json_file, std::vector<Dataset>& datasets);

bool parse_json_plots(const std::vector<std::string>& json_file, std::vector<Plot>& plots) {
    plots.clear();

    for (const auto& plot_json_file: json_file) {
        std::ifstream f(plot_json_file);

        Json::Value root;
        Json::Reader reader;
        if (! reader.parse(f, root)) {
            std::cerr << "Failed to parse '" << plot_json_file << "'." << std::endl;
            return false;
        }

        for (auto it = root.begin(); it != root.end(); it++) {
            Plot p = {it.name(), (*it)["variable"].asString(), (*it)["plot_cut"].asString(), (*it)["binning"].asString()};
            plots.push_back(p);
        }
    }
}

bool parse_python_plots(const std::string& python_file, std::vector<Plot>& plots) {

    plots.clear();

    std::FILE* f = std::fopen(python_file.c_str(), "r");
    if (!f) {
        std::cerr << "Failed to open '" << python_file << "'" <<std::endl;
        return false;
    }


    Py_Initialize();

    const std::string PLOTS_KEY_NAME = "plots";

    // Get a reference to the main module
    // and global dictionary
    PyObject* main_module = PyImport_AddModule("__main__");
    PyObject* global_dict = PyModule_GetDict(main_module);

    // If PyROOT is used inside the script, it performs some cleanups when the python env. is destroyed. This cleanup makes ROOT unusable afterwards.
    // The cleanup function is registered with the `atexit` module.
    // The solution is to not execute the cleanup function. For that, before destroying the python env, we check the list of exit functions,
    // and delete the one from PyROOT if found

    // Ensure the module is loaded
    PyObject* atexit_module = PyImport_ImportModule("atexit");

    // Execute the script
    PyObject* script_result = PyRun_File(f, python_file.c_str(), Py_file_input, global_dict, global_dict);

    if (! script_result) {
        PyErr_Print();
        return false;
    } else {
        PyObject* py_plots = PyDict_GetItemString(global_dict, "plots");
        if (!py_plots) {
            std::cerr << "No 'plots' variable declared in python script" << std::endl;
            return false;
        }

        if (! PyList_Check(py_plots)) {
            std::cerr << "The 'plots' variable is not a list" << std::endl;
            return false;
        }

        size_t l = PyList_Size(py_plots);
        if (! l)
            return true;

        for (size_t i = 0; i < l; i++) {
            PyObject* item = PyList_GetItem(py_plots, i);

            Plot plot;
            if (plot_from_PyObject(item, plot)) {
                plots.push_back(plot);
            }
        }
    }

    PyObject* atexit_exithandlers = PyObject_GetAttrString(atexit_module, "_exithandlers");
    for (size_t i = 0; i < PySequence_Size(atexit_exithandlers); i++) {
        PyObject* tuple = PySequence_GetItem(atexit_exithandlers, i);
        PyObject* f = PySequence_GetItem(tuple, 0);
        PyObject* module = PyFunction_GetModule(f);

        if (module && strcmp(PyString_AsString(module), "ROOT") == 0) {
            PySequence_DelItem(atexit_exithandlers, i);
            break;
        }
    }

    Py_Finalize();

    return true;
}

bool execute(const std::vector<Dataset>& datasets, const std::vector<std::string>& config_files, bool python, std::string output_dir/* = ""*/) {

    std::vector<Plot> plots;

    if (python) {
        parse_python_plots(config_files[0], plots);
    } else {
        parse_json_plots(config_files, plots);
    }

    // Setting the TVirtualTreePlayer
    TVirtualTreePlayer::SetPlayer("TMultiDrawTreePlayer");

    std::cout << "List of requested plots: ";
    for (size_t i = 0; i < plots.size(); i++) {
        std::cout << "'" << plots[i].name << "'";
        if (i != plots.size() - 1)
            std::cout << ", ";
    }

    std::cout << std::endl << std::endl;

    for (const Dataset& dataset: datasets) {

        // If an output directory is specified, use it, otherwise use the current directory
        if (output_dir == "")
          output_dir = ".";
        // If an output file name is specified in the Json, use it, otherwise use the sample DB name
        std::string output_file = output_dir + "/" + dataset.output_name;

        std::cout << "Running on sample '" << dataset.name << "'." << std::endl;
        std::cout << "Output file: " << output_file << std::endl;

        std::unique_ptr<TChain> t(new TChain(dataset.tree_name.c_str()));

        for (const auto& file: dataset.files)
            t->Add(file.c_str());
        
        std::unique_ptr<TFile> outfile(TFile::Open(output_file.c_str(), "recreate"));

        TMultiDrawTreePlayer* player = dynamic_cast<TMultiDrawTreePlayer*>(t->GetPlayer());

        // Looping over the different plots
        for (auto& p: plots) {
            std::string plot_var = p.variable + ">>" + p.name + p.binning;
            player->queueDraw(plot_var.c_str(), p.plot_cut.c_str(), "goff");
        }

        player->execute();

        for (auto& p: plots) {
            TObject* obj = gDirectory->Get(p.name.c_str());
            if (obj)
                obj->Write(nullptr, TObject::kOverwrite);
        }

        outfile->Write(nullptr, TObject::kOverwrite);
    }

    return true;
}

bool parse_datasets(const std::string& json_file, std::vector<Dataset>& datasets) {

    Json::Value root;
    {
        std::ifstream f(json_file);
        Json::Reader reader;
        if (! reader.parse(f, root, false)) {
            std::cerr << "Failed to parse '" << json_file << "'" << std::endl;
            return false;
        }
    }

    datasets.clear();

    // Looping over the different samples
    Json::Value::Members samples_str = root.getMemberNames();
    for (size_t index = 0; index < root.size(); index++) {

        const Json::Value& sample = root[samples_str[index]];
        Dataset dataset;

        // Mandatory fields
        dataset.name = samples_str[index];
        dataset.db_name = sample["db_name"].asString();
        dataset.cut = sample.get("sample_cut", "1").asString();
        dataset.tree_name = sample.get("tree_name", "t").asString();

        //dataset.output_name
        if (sample.isMember("output_name")) {
            dataset.output_name = sample["output_name"].asString();
        } else {
            dataset.output_name = dataset.db_name + "_histos.root";
        }

        // If a list of files is specified, only use those
        if (sample.isMember("files")) {
            Json::Value files = sample["files"];

            for(auto it = files.begin(); it != files.end(); ++it) {
                dataset.files.push_back((*it).asString());
            }
        } else if (sample.isMember("path")) {
            dataset.path = sample["path"].asString();
            dataset.files.push_back(dataset.path + "/*.root");
        }

        datasets.push_back(dataset);
    }

    return true;
}

int main( int argc, char* argv[]) {

    try {

        TCLAP::CmdLine cmd("Create histograms from trees", ' ', "0.1.0");

        TCLAP::ValueArg<std::string> datasetArg("d", "dataset", "Input datasets", true, "", "JSON file", cmd);
        TCLAP::ValueArg<std::string> outputArg("o", "output", "Output directory", false, "", "ROOT file", cmd);
        TCLAP::UnlabeledMultiArg<std::string> plotsArg("plots", "List of plots", true, "JSON/Python file", cmd);

        cmd.parse(argc, argv);

        bool python = false;
        const std::vector<std::string>& plots = plotsArg.getValue();
        if (plots.size() == 1 && plots[0].substr(plots[0].find_last_of(".") + 1) == "py") {
            python = true;
        }

        std::vector<Dataset> datasets;
        parse_datasets(datasetArg.getValue(), datasets);

        if (datasets.empty()) {
            std::cerr << "Error: no input datasets specified." << std::endl;
            return 1;
        }

        std::unique_ptr<TApplication> app;

        bool ret = false;
        if (python) {
            /*
             * When PyROOT is loaded, it creates it's own ROOT application ([1] and [2]). We do not want this to happen,
             * because it messes with our already loaded ROOT.
             *
             * To prevent this, we create here our own application (which does nothing), just to prevent `CreatePyROOTApplication`
             * to do anything.
             *
             * [1] https://github.com/root-mirror/root/blob/0a62e34aa86b812651cfcf9526ba03b975adaa5c/bindings/pyroot/ROOT.py#L476
             * [2] https://github.com/root-mirror/root/blob/0a62e34aa86b812651cfcf9526ba03b975adaa5c/bindings/pyroot/src/TPyROOTApplication.cxx#L117
             */

            app.reset(new TApplication("dummy", 0, NULL));
        }

        ret = execute(datasets, plots, python, outputArg.getValue());
        return (ret ? 0 : 1);

    } catch (TCLAP::ArgException &e) {
        std::cerr << "error: " << e.error() << " for arg " << e.argId() << std::endl;
        return 1;
    }

    return 0;
}


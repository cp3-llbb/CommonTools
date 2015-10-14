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

#include <tclap/CmdLine.h>

struct Plot {
    std::string name;
    std::string variable;
    std::string plot_cut;
    std::string binning;
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

bool execute(const std::string& datasets_json, const std::vector<Plot>& plots);

bool execute(const std::string& datasets_json, const std::string& python) {
    std::FILE* f = std::fopen(python.c_str(), "r");
    if (!f) {
        std::cerr << "Failed to open '" << python << "'" <<std::endl;
        return false;
    }

    std::vector<Plot> plots;


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
    PyObject* script_result = PyRun_File(f, python.c_str(), Py_file_input, global_dict, global_dict);

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

    if (plots.empty())
        return false;

    return execute(datasets_json, plots);
}

// Plots are specified in JSON files
bool execute(const std::string& datasets_json, const std::vector<std::string>& plots_json) {

    // Plots are in JSON format. Parse these files

    // Get the list of plots to draw
    std::vector<Plot> plots;
    for (const auto& plot_json_file: plots_json) {
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

    return execute(datasets_json, plots);
}

bool execute(const std::string& datasets_json, const std::vector<Plot>& plots) {
    // Setting the TVirtualTreePlayer
    TVirtualTreePlayer::SetPlayer("TMultiDrawTreePlayer");

    // Getting the list of samples    
    Json::Value samplesroot;
    {
        std::ifstream config_doc(datasets_json);

        Json::Reader samplesreader;
        bool parsingSuccessful = samplesreader.parse(config_doc, samplesroot, false);
        if (!parsingSuccessful) {
            std::cerr << "Failed to parse '" << datasets_json << "'" << std::endl;
            return false;
        }
    }

    std::cout << "List of requested plots: ";
    for (size_t i = 0; i < plots.size(); i++) {
        std::cout << "'" << plots[i].name << "'";
        if (i != plots.size() - 1)
            std::cout << ", ";
    }

    std::cout << std::endl << std::endl;

    // Looping over the different samples
    Json::Value::Members samples_str = samplesroot.getMemberNames();
    for (unsigned int index = 0; index < samplesroot.size(); index++){    

        const Json::Value samplearray = samplesroot[samples_str.at(index)];

        std::string tree_name = samplearray.get("tree_name","ASCII").asString();
        std::string path = samplearray.get("path","ASCII").asString();
        std::string db_name = samplearray.get("db_name","ASCII").asString();
        std::string sample_cut = samplearray.get("sample_cut","ASCII").asString();

        std::cout << "Running on sample '" << samples_str.at(index) << "'" << std::endl;

        std::unique_ptr<TChain> t(new TChain(tree_name.c_str()));

        std::string infiles = path+"/*.root";

        t->Add(infiles.c_str());

        std::unique_ptr<TFile> outfile(TFile::Open((db_name+"_histos.root").c_str(), "recreate"));

        TMultiDrawTreePlayer* player = dynamic_cast<TMultiDrawTreePlayer*>(t->GetPlayer());

        // Looping over the different plots
        for (auto& p: plots) {
            std::string plot_var = p.variable + ">>" + p.name + p.binning;
            player->queueDraw(plot_var.c_str(), p.plot_cut.c_str());
        }

        player->execute();

        for (auto& p: plots) {
            gDirectory->Get(p.name.c_str())->Write();
        }

        outfile->Write();
    }

    return true;
}


int main( int argc, char* argv[]) {

    try {

        TCLAP::CmdLine cmd("Create histograms from trees", ' ', "0.1.0");

        TCLAP::ValueArg<std::string> datasetArg("d", "dataset", "Input datasets", true, "", "JSON file", cmd);
        TCLAP::UnlabeledMultiArg<std::string> plotsArg("plots", "List of plots", true, "JSON file", cmd);

        cmd.parse(argc, argv);

        bool python = false;
        const std::vector<std::string>& plots = plotsArg.getValue();
        if (plots.size() == 1 && plots[0].substr(plots[0].find_last_of(".") + 1) == "py") {
            python = true;
        }

        bool ret = false;
        if (python) {
            /*
             * When PyROOT is loaded, it creates it's own ROOT application ([1] and [2]). We do not want this to happen,
             * because it messes with our already loaded ROOT.
             *
             * To prevent this, we create here our own application (which does nothing), just to prevent `CreatePyROOTApplicationµ
             * to do anything.
             *
             * [1] https://github.com/root-mirror/root/blob/0a62e34aa86b812651cfcf9526ba03b975adaa5c/bindings/pyroot/ROOT.py#L476
             * [2] https://github.com/root-mirror/root/blob/0a62e34aa86b812651cfcf9526ba03b975adaa5c/bindings/pyroot/src/TPyROOTApplication.cxx#L117
             */

            std::unique_ptr<TApplication> app(new TApplication("dummy", 0, NULL));
            ret = execute(datasetArg.getValue(), plots[0]);
        } else
            ret = execute(datasetArg.getValue(), plots);

        return (ret ? 0 : 1);

    } catch (TCLAP::ArgException &e) {
        std::cerr << "error: " << e.error() << " for arg " << e.argId() << std::endl;
        return 1;
    }

    return 0;
}


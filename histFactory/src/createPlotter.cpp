// Read some trees, output an histos
// A. Mertens (September 2015)

#include <Python.h>

#include <histFactory/config.h>

#include <iostream>
#include <fstream>
#include <memory>
#include <cstdio>

#include <TChain.h>
#include <TApplication.h>

// Ugly hack to access list of leaves in the formula
#define protected public
#include <TTreeFormula.h>
#undef protected

#include <uuid/uuid.h>

#include <tclap/CmdLine.h>

#include <ctemplate/template.h>

struct Branch {
    std::string name;
    std::string type;
};

struct Plot {
    std::string name;
    std::string variable;
    std::string plot_cut;
    std::string binning;

    std::shared_ptr<TTreeFormula> var;
    std::shared_ptr<TTreeFormula> selector;
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

std::string get_uuid() {
    uuid_t out;
    uuid_generate(out);

    std::string uuid;
    uuid.resize(37);

    uuid_unparse(out, &uuid[0]);

    uuid[8] = '_';
    uuid[13] = '_';
    uuid[18] = '_';
    uuid[23] = '_';

    // Remove null terminator
    uuid.resize(36);

    // Ensure name starts with a letter to be a valid C++ identifier
    uuid = "p_" + uuid;

    return uuid;
}

inline TBranch* getTopBranch(TBranch* branch) {
    if (! branch)
        return nullptr;

    if (branch == branch->GetMother())
        return branch;

    return getTopBranch(branch->GetMother());
}

inline std::string getTemplate(const std::string& name) {
    std::string p = TEMPLATE_PATH;
    p += "/" + name + ".tpl";

    return p;
}

bool execute(const std::string& skeleton, const std::string& config_file, std::string output_dir = "");

bool get_plots(const std::string& python_file, std::vector<Plot>& plots) {

    plots.clear();

    std::FILE* f = std::fopen(python_file.c_str(), "r");
    if (!f) {
        std::cerr << "Failed to open '" << python_file << "'" <<std::endl;
        return false;
    }

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

    return true;
}

bool execute(const std::string& skeleton, const std::string& config_file, std::string output_dir/* = ""*/) {

    std::vector<Plot> plots;
    // If an output directory is specified, use it, otherwise use the current directory
    if (output_dir == "")
      output_dir = ".";

    std::map<std::string, std::string> unique_names;

    get_plots(config_file, plots);

    std::cout << "List of requested plots: ";
    for (size_t i = 0; i < plots.size(); i++) {
        std::cout << "'" << plots[i].name << "'";
        if (i != plots.size() - 1)
            std::cout << ", ";
    }
    std::cout << std::endl;

    // Convert plots name to unique name to avoid collision between different runs
    for (Plot& plot: plots) {
        std::string uuid = get_uuid();
        unique_names[uuid] = plot.name;
        plot.name = uuid;
    }

    std::unique_ptr<TChain> t(new TChain("t"));
    t->Add(skeleton.c_str());

    std::vector<Branch> branches;
    std::function<void(TTreeFormula*)> getBranches = [&branches, &getBranches](TTreeFormula* f) {
        if (!f)
            return;

        for (size_t i = 0; i < f->GetNcodes(); i++) {
            TLeaf* leaf = f->GetLeaf(i);
            if (! leaf)
                continue;

            TBranch* p_branch = getTopBranch(leaf->GetBranch());

            Branch branch;
            branch.name = p_branch->GetName();
            if (std::find_if(branches.begin(), branches.end(), [&branch](const Branch& b) {  return b.name == branch.name;  }) == branches.end()) {
                branch.type = p_branch->GetClassName();
                if (branch.type.empty())
                    branch.type = leaf->GetTypeName();

                branches.push_back(branch);
            }

            for (size_t j = 0; j < f->fNdimensions[i]; j++) {
                if (f->fVarIndexes[i][j])
                    getBranches(f->fVarIndexes[i][j]);
            }
        }

        for (size_t i = 0; i < f->fAliases.GetEntriesFast(); i++) {
            getBranches((TTreeFormula*) f->fAliases.UncheckedAt(i));
        }
    };

    std::string hists_declaration;
    std::string text_plots;
    for (auto& p: plots) {
        // Create formulas
        p.var.reset(new TTreeFormula("var", p.variable.c_str(), t.get()));
        p.selector.reset(new TTreeFormula("selector", p.plot_cut.c_str(), t.get()));

        getBranches(p.var.get());
        getBranches(p.selector.get());

        std::string binning = p.binning;
        binning.erase(std::remove_if(binning.begin(), binning.end(), [](char chr) { return chr == '(' || chr == ')'; }), binning.end());
        hists_declaration += "TH1* " + p.name + " = new TH1F(\"" + p.name + "\", \"\", " + binning + ");\n";

        ctemplate::TemplateDictionary plot("plot");
        plot.SetValue("CUT", p.plot_cut);
        plot.SetValue("VAR", p.variable);
        plot.SetValue("HIST", p.name);

        ctemplate::ExpandTemplate(getTemplate("Plot"), ctemplate::DO_NOT_STRIP, &plot, &text_plots);
    }

    // Sort alphabetically
    std::sort(branches.begin(), branches.end(), [](const Branch& a, const Branch& b) {
            return a.name < b.name;
            });

    std::string text_branches;
    for (const auto& branch: branches)  {
        text_branches += "const " + branch.type + "& " + branch.name + " = tree[\"" + branch.name + "\"].read<" + branch.type + ">();\n        ";
    }

    ctemplate::TemplateDictionary header("header");
    header.SetValue("BRANCHES", text_branches);

    std::string output;
    ctemplate::ExpandTemplate(getTemplate("Plotter.h"), ctemplate::DO_NOT_STRIP, &header, &output);

    std::ofstream out(output_dir + "/Plotter.h");
    out << output;
    out.close();

    output.clear();

    std::string text_save_plots;
    for (auto& p: plots) {
        ctemplate::TemplateDictionary save_plot("save_plot");
        save_plot.SetValue("UNIQUE_NAME", p.name);
        save_plot.SetValue("PLOT_NAME", unique_names[p.name]);
        ctemplate::ExpandTemplate(getTemplate("SavePlot"), ctemplate::DO_NOT_STRIP, &save_plot, &text_save_plots);
    }

    ctemplate::TemplateDictionary source("source");
    source.SetValue("HISTS_DECLARATION", hists_declaration);
    source.SetValue("PLOTS", text_plots);
    source.SetValue("SAVE_PLOTS", text_save_plots);
    ctemplate::ExpandTemplate(getTemplate("Plotter.cc"), ctemplate::DO_NOT_STRIP, &source, &output);

    out.open(output_dir + "/Plotter.cc");
    out << output;
    out.close();

    return true;
}

int main( int argc, char* argv[]) {

    try {

        TCLAP::CmdLine cmd("Create histograms from trees", ' ', "0.2.0");

        TCLAP::ValueArg<std::string> skeletonArg("i", "input", "Input file containing a skeleton tree", true, "", "ROOT file", cmd);
        TCLAP::ValueArg<std::string> outputArg("o", "output", "Output directory", false, "", "FOLDER", cmd);
        TCLAP::UnlabeledValueArg<std::string> plotsArg("plots", "A python script which will be executed and should returns a list of plots", true, "", "Python script", cmd);

        cmd.parse(argc, argv);

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

        std::unique_ptr<TApplication> app(new TApplication("dummy", 0, NULL));

        Py_Initialize();

        bool ret = execute(skeletonArg.getValue(), plotsArg.getValue(), outputArg.getValue());

        Py_Finalize();

        return (ret ? 0 : 1);

    } catch (TCLAP::ArgException &e) {
        std::cerr << "error: " << e.error() << " for arg " << e.argId() << std::endl;
        return 1;
    }

    return 0;
}


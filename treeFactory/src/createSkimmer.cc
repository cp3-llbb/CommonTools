/*
Copyright 2015 Sébastien Brochet

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

#include <Python.h>

#include <treeFactory/config.h>

#include <iostream>
#include <fstream>
#include <memory>
#include <unordered_map>

#include <TChain.h>
#include <TBranch.h>
#include <TLeaf.h>
#include <TApplication.h>

#include <formula_parser.h>

#include <uuid/uuid.h>

#include <tclap/CmdLine.h>

#include <ctemplate/template.h>

#include <boost/filesystem.hpp>
#include <boost/system/error_code.hpp>
namespace fs = boost::filesystem;

struct InputBranch {
    std::string name;
    std::string type;
};

struct OutputBranch {
    std::string name;
    std::string unique_name;
    std::string variable;
    std::string type;
};

struct Tree {
    std::string name;
    std::string cut;
    std::vector<OutputBranch> branches;
};

struct UserCode {
    std::string before_loop;
    std::string in_loop;
    std::string after_loop;
};

struct Extra {
    UserCode userCode;
    std::set<std::string> includes;
    std::set<fs::path> sources;
    std::set<std::string> extra_branches;
    std::map<std::string, std::string> sample_weights;
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

#define GET(var, obj) if (PyDict_Contains(value, obj) == 1) { \
    PyObject* item = PyDict_GetItem(value, obj); \
    if (! PyString_Check(item)) {\
        std::cerr << "Error: the '" << PyString_AsString(obj) << "' value must be a string" << std::endl; \
        return false; \
    } \
    var = PyString_AsString(item); \
}

bool output_branch_from_PyObject(PyObject* value, OutputBranch& branch) {
    static PyObject* PY_NAME = PyString_FromString("name");
    static PyObject* PY_VARIABLE = PyString_FromString("variable");
    static PyObject* PY_TYPE = PyString_FromString("type");

    if (! PyDict_Check(value)) {
        std::cerr << "Error: branches dictionnary value must be a dictionnary" << std::endl;
    }

    CHECK_AND_GET(branch.name, PY_NAME);
    CHECK_AND_GET(branch.variable, PY_VARIABLE);
    branch.type = "float";
    GET(branch.type, PY_TYPE);

    return true;
}

std::string get_uuid();

bool tree_from_PyObject(PyObject* value, Tree& tree) {
    static PyObject* PY_NAME = PyString_FromString("name");
    static PyObject* PY_CUT = PyString_FromString("cut");
    static PyObject* PY_BRANCHES = PyString_FromString("branches");

    CHECK_AND_GET(tree.name, PY_NAME);

    tree.cut = "1";
    GET(tree.cut, PY_CUT);
    
    if (PyDict_Contains(value, PY_BRANCHES) == 0) {
        std::cout << "No branches declared in tree" << std::endl;
        return false;
    }

    PyObject* py_branches = PyDict_GetItem(value, PY_BRANCHES);
    
    if (! PyList_Check(py_branches)) {
        std::cerr << "The '" << PyString_AsString(PY_BRANCHES) << "' value is not a list" << std::endl;
        return false;
    }

    size_t l = PyList_Size(py_branches);
    if (! l)
        return false;

    for (size_t i = 0; i < l; i++) {
        PyObject* item = PyList_GetItem(py_branches, i);

        OutputBranch branch;
        if (output_branch_from_PyObject(item, branch)) {
            branch.unique_name = get_uuid();
            tree.branches.push_back(branch);
        }
    }

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

std::vector<std::string> split(const std::string& s, const std::string& delimiters) {

    std::vector<std::string> result;

    size_t current;
    size_t next = -1;
    do
    {
        next = s.find_first_not_of(delimiters, next + 1);
        if (next == std::string::npos)
            break;
        next -= 1;

        current = next + 1;
        next = s.find_first_of(delimiters, current);
        result.push_back(s.substr(current, next - current));
    }
    while (next != std::string::npos);

    return result;
}

bool execute(const std::string& skeleton, const std::string& config_file, std::string output_dir = "");

/**
 * Parse a python file and extract the list of branches to create
 */
bool get_output_tree(const std::string& python_file, Tree& tree, Extra& extra) {

    std::FILE* f = std::fopen(python_file.c_str(), "r");
    if (!f) {
        std::cerr << "Failed to open '" << python_file << "'" <<std::endl;
        return false;
    }

    const std::string TREE_KEY_NAME = "tree";

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
    }
    
    PyObject* py_tree = PyDict_GetItemString(global_dict, TREE_KEY_NAME.c_str());
    if (!py_tree) {
        std::cerr << "No '" << TREE_KEY_NAME << "' variable declared in python script" << std::endl;
        return false;
    }

    if (! PyDict_Check(py_tree)) {
        std::cerr << "The '" << TREE_KEY_NAME << "' variable is not a dictionary" << std::endl;
        return false;
    }

    if (! tree_from_PyObject(py_tree, tree))
        return false;
    
    fs::path python_dir(python_file);
    python_dir = python_dir.parent_path();

    // Retrieve list of include files
    PyObject* py_includes = PyDict_GetItemString(global_dict, "includes");
    if (py_includes) {

        if (! PyList_Check(py_includes)) {
            std::cerr << "The 'includes' variable is not a list" << std::endl;
            return false;
        }

        size_t l = PyList_Size(py_includes);

        for (size_t i = 0; i < l; i++) {
            PyObject* item = PyList_GetItem(py_includes, i);
            if (! PyString_Check(item) ) {
                std::cerr << "The items of the 'include' list must be strings" << std::endl;
                return false;
            }
            std::string temp_string( PyString_AsString(item) );
            if ( temp_string.find("<") != std::string::npos ){
                std::cout << "Header file " << temp_string << " seems to be a library header. No attempt will be made to check its path." << std::endl;
                extra.includes.emplace(temp_string);
            } else {
                boost::system::error_code dummy; // dummy error code to get the noexcept exists() overload
                fs::path temp_path( temp_string );
                if ( !fs::exists(temp_path, dummy) || !fs::is_regular_file(temp_path) ) {
                    if ( !fs::exists(python_dir/temp_path, dummy) || !fs::is_regular_file(python_dir/temp_path) ) {
                        std::cerr << "File " << temp_path.filename().string() << " could not be found in ./" << temp_path.parent_path().string() << " or in ./" << (python_dir/temp_path).parent_path().string() << std::endl;
                        return false;
                    } else {
                        temp_path = python_dir/temp_path;
                    }
                }
                extra.includes.emplace(temp_path.string());
            }
        }

    }
    
    // Retrieve list of source files
    PyObject* py_sources = PyDict_GetItemString(global_dict, "sources");
    if (py_sources) {

        if (! PyList_Check(py_sources)) {
            std::cerr << "The 'sources' variable is not a list" << std::endl;
            return false;
        }

        size_t l = PyList_Size(py_sources);

        for (size_t i = 0; i < l; i++) {
            PyObject* item = PyList_GetItem(py_sources, i);
            if (! PyString_Check(item) ) {
                std::cerr << "The items of the 'sources' list must be strings" << std::endl;
                return false;
            }
            boost::system::error_code dummy; // dummy error code to get the noexcept exists() overload
            fs::path temp_path( PyString_AsString(item) );
            if ( !fs::exists(temp_path, dummy) || !fs::is_regular_file(temp_path) ) {
                if ( !fs::exists(python_dir/temp_path, dummy) || !fs::is_regular_file(python_dir/temp_path) ) {
                    std::cerr << "File " << temp_path.filename().string() << " could not be found in ./" << temp_path.parent_path().string() << " or in ./" << (python_dir/temp_path).parent_path().string() << std::endl;
                    return false;
                } else {
                    temp_path = python_dir/temp_path;
                }
            }
            extra.sources.emplace(temp_path);
        }

    }

    // Retrieve list of additional branches
    PyObject* py_extra_branches = PyDict_GetItemString(global_dict, "extra_branches");
    if (py_extra_branches) {

        if (! PyList_Check(py_extra_branches)) {
            std::cerr << "The 'extra_branches' variable is not a list" << std::endl;
            return false;
        }

        size_t l = PyList_Size(py_extra_branches);

        for (size_t i = 0; i < l; i++) {
            PyObject* item = PyList_GetItem(py_extra_branches, i);
            if (! PyString_Check(item) ) {
                std::cerr << "The items of the 'extra_branches' list must be strings" << std::endl;
                return false;
            }
            extra.extra_branches.emplace( PyString_AsString(item) );
        }

    }

    // Retrieve user code to be included in the function
    PyObject* py_before_loop = PyDict_GetItemString(global_dict, "code_before_loop");
    if (py_before_loop) {
        if (! PyString_Check(py_before_loop)) {
            std::cerr << "The 'before_loop' variable is not a string" << std::endl;
            return false;
        }
        extra.userCode.before_loop = PyString_AsString(py_before_loop);
    }
    PyObject* py_in_loop = PyDict_GetItemString(global_dict, "code_in_loop");
    if (py_in_loop) {
        if (! PyString_Check(py_in_loop)) {
            std::cerr << "The 'in_loop' variable is not a string" << std::endl;
            return false;
        }
        extra.userCode.in_loop = PyString_AsString(py_in_loop);
    }
    PyObject* py_after_loop = PyDict_GetItemString(global_dict, "code_after_loop");
    if (py_after_loop) {
        if (! PyString_Check(py_after_loop)) {
            std::cerr << "The 'after_loop' variable is not a string" << std::endl;
            return false;
        }
        extra.userCode.after_loop = PyString_AsString(py_after_loop);
    }

    // Retrieve dict of sample weights
    // The key can be set in the sample json to indicate which sample weight to use
    // The value is any valid C++ code, which will be added in the global `getSampleWeight`
    // function.
    PyObject* py_sample_weights = PyDict_GetItemString(global_dict, "sample_weights");
    if (py_sample_weights) {
        if (! PyDict_Check(py_sample_weights)) {
            std::cerr << "The 'sample_weights' variable is not a dictionnary" << std::endl;
            return false;
        }

        PyObject* key, *value;
        Py_ssize_t pos = 0;
        while (PyDict_Next(py_sample_weights, &pos, &key, &value)) {
            if (! PyString_Check(key)) {
                std::cerr << "Keys of 'sample_weights' dict must be strings" << std::endl;
                return false;
            }

            if (! PyString_Check(value)) {
                std::cerr << "Values of 'sample_weights' dict must be strings" << std::endl;
                return false;
            }

            extra.sample_weights.emplace(PyString_AsString(key), PyString_AsString(value));
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

    Tree output_tree;
    Extra extra;
    // If an output directory is specified, use it, otherwise use the current directory
    if (output_dir == "")
      output_dir = ".";

    std::map<std::string, std::string> unique_names;

    if (! get_output_tree(config_file, output_tree, extra))
        return false;

    std::cout << "List of branches in the output tree: ";
    for (size_t i = 0; i < output_tree.branches.size(); i++) {
        std::cout << "'" << output_tree.branches[i].name << "'";
        if (i != output_tree.branches.size() - 1)
            std::cout << ", ";
    }
    std::cout << std::endl;
    
    std::cout << "List of requested include files: ";
    for (const auto& i: extra.includes) {
        std::cout << "'" << i << "', ";
    }
    std::cout << std::endl;

    std::cout << "List of requested source files: ";
    for (const auto& s: extra.sources) {
        std::cout << "'" << s.string() << "', ";
    }
    std::cout << std::endl;

    std::cout << "List of requested extra branches: ";
    for (const auto& s: extra.extra_branches) {
        std::cout << "'" << s << "', ";
    }
    std::cout << std::endl;
    
    if( !extra.userCode.before_loop.empty() )
      std::cout << "User has requested code before the event loop." << std::endl;
    if( !extra.userCode.in_loop.empty() )
      std::cout << "User has requested code in the event loop." << std::endl;
    if( !extra.userCode.after_loop.empty() )
      std::cout << "User has requested code after the event loop." << std::endl;

    parser::parser parser;

    std::unique_ptr<TChain> t(new TChain("t"));
    t->Add(skeleton.c_str());

    // Get list of all branches
    std::unordered_map<std::string, InputBranch> tree_branches;
    TObjArray* root_tree_branches = t->GetListOfBranches();
    for (size_t i = 0; i < static_cast<size_t>(root_tree_branches->GetEntries()); i++) {
        TBranch* b = static_cast<TBranch*>(root_tree_branches->UncheckedAt(i));

        InputBranch branch;
        branch.name = b->GetName();
        branch.type = b->GetClassName();

        if (branch.type.empty()) {
            TLeaf* leaf = b->GetLeaf(branch.name.c_str());
            if (! leaf) {
                std::cerr << "Error: can't deduce type for branch '" << branch.name << "'" << std::endl;
                continue;
            }
            branch.type = leaf->GetTypeName();
        }

        tree_branches.emplace(branch.name, branch);
    }


    std::string output_branches_declaration;
    std::string output_branches_filling;
    std::set<std::string> identifiers;

    // Tree cut
    if (!parser.parse(output_tree.cut, identifiers))
        std::cerr << "Warning: " << output_tree.cut << " failed to parse." << std::endl;

    for (auto& b: output_tree.branches) {

        if (! parser.parse(b.variable, identifiers))
            std::cerr << "Warning: " << b.variable << " failed to parse." << std::endl;

        output_branches_declaration += "    " + b.type + "& " + b.unique_name + " = output_tree[\"" + b.name + "\"].write<" + b.type + ">();\n";
        output_branches_filling += "        " + b.unique_name + " = (" + b.variable + ");\n";
    }

    for (const auto& it: extra.sample_weights) {
        if (! parser.parse(it.second, identifiers)) {
            std::cerr << "Warning: " << it.second << " failed to parse." << std::endl;
        }
    }

    // Update the list of identifiers with the extra branches requested by the user
    identifiers.insert(extra.extra_branches.begin(), extra.extra_branches.end());

    // Everything is parsed. Collect the list of branches used by the formula
    std::vector<InputBranch> branches;
    for (const auto& id: identifiers) {
        auto branch = tree_branches.find(id);
        if (branch == tree_branches.end())
            continue;

        branches.push_back(branch->second);
    }

    std::string input_branches_declaration;
    for (const auto& branch: branches)  {
        input_branches_declaration += "const " + branch.type + "& " + branch.name + " = tree[\"" + branch.name + "\"].read<" + branch.type + ">();\n        ";
    }

    ctemplate::TemplateDictionary header("header");
    header.SetValue("BRANCHES", input_branches_declaration);

    std::string output;
    ctemplate::ExpandTemplate(getTemplate("Skimmer.h"), ctemplate::DO_NOT_STRIP, &header, &output);

    std::ofstream out(output_dir + "/Skimmer.h");
    out << output;
    out.close();

    output.clear();

    // Create cut string
    std::string global_cut = "        if (! (" + output_tree.cut + ")) { continue; }";

    std::string text_includes;
    for (const auto& f: extra.includes) {
        if (f.find('<') != std::string::npos)
            text_includes += "#include " + f + "\n";
        else
            text_includes += "#include \"" + fs::path(f).filename().string() + "\"\n";
    }

    // Create `getSampleWeight` function
    std::string sample_weight_function = "    if ((m_dataset.sample_weight_key.empty()) || (m_dataset.sample_weight_key == \"none\")) {\n        return 1.;\n    }\n";
    for (const auto& it: extra.sample_weights) {
        sample_weight_function += R"(    if (m_dataset.sample_weight_key == ")" + it.first + R"(") {)" + "\n";
        sample_weight_function += "        return (" + it.second + ");\n";
        sample_weight_function += "    }\n";
    }

    sample_weight_function += "\n    return 1.;";
    
    ctemplate::TemplateDictionary source("source");
    source.SetValue("INCLUDES", text_includes);
    source.SetValue("OUTPUT_TREE_NAME", output_tree.name);
    source.SetValue("OUTPUT_BRANCHES_DECLARATION", output_branches_declaration);
    source.SetValue("GLOBAL_CUT", global_cut);
    source.SetValue("OUTPUT_BRANCHES_FILLING", output_branches_filling);
    source.SetValue("USER_CODE_BEFORE_LOOP", extra.userCode.before_loop);
    source.SetValue("USER_CODE_IN_LOOP", extra.userCode.in_loop);
    source.SetValue("USER_CODE_AFTER_LOOP", extra.userCode.after_loop);
    source.SetValue("SAMPLE_WEIGHT_IMPL", sample_weight_function);
    ctemplate::ExpandTemplate(getTemplate("Skimmer.cc"), ctemplate::DO_NOT_STRIP, &source, &output);

    out.open(output_dir + "/Skimmer.cc");
    out << output;
    out.close();
    
    // Make external sources accessible to plotter 
    std::set<fs::path> include_dirs;
    for(const auto& f: extra.includes){
      if(f.find('<') == std::string::npos)
        include_dirs.emplace( fs::path(f).parent_path() );
    }
    std::string include_cmake;
    for(const auto& d: include_dirs)
      include_cmake += d.string() + " ";
    
    std::string source_cmake;
    for(const auto& s: extra.sources)
      source_cmake += s.string() + " ";

    ctemplate::TemplateDictionary cmake("cmake");
    cmake.SetValue("ADD_INCLUDES", include_cmake);
    cmake.SetValue("ADD_SOURCES", source_cmake);
    std::string cmake_output;
    ctemplate::ExpandTemplate(getTemplate("CMakeLists.txt"), ctemplate::DO_NOT_STRIP, &cmake, &cmake_output);
    out.open(output_dir + "/CMakeLists.txt");
    out << cmake_output;
    out.close();

    return true;
}

int main( int argc, char* argv[]) {

    try {

        TCLAP::CmdLine cmd("Create histograms from trees", ' ', "0.2.0");

        TCLAP::ValueArg<std::string> skeletonArg("i", "input", "Input file containing a skeleton tree", true, "", "ROOT file", cmd);
        TCLAP::ValueArg<std::string> outputArg("o", "output", "Output directory", false, "", "FOLDER", cmd);
        TCLAP::UnlabeledValueArg<std::string> treeArg("tree", "A python script which will be executed and should describe the tree to create", true, "", "Python script", cmd);

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

        bool ret = execute(skeletonArg.getValue(), treeArg.getValue(), outputArg.getValue());

        Py_Finalize();

        return (ret ? 0 : 1);

    } catch (TCLAP::ArgException &e) {
        std::cerr << "error: " << e.error() << " for arg " << e.argId() << std::endl;
        return 1;
    }

    return 0;
}


#include <Factory.h>

#include <TChain.h>
#include <TBranch.h>
#include <TLeaf.h>
#include <TApplication.h>
#include <TROOT.h>

#include <formula_parser.h>

#include <tclap/CmdLine.h>

#include <ctemplate/template.h>

#include <uuid/uuid.h>
#include <boost/filesystem/fstream.hpp>
#include <stdexcept>

namespace fs = boost::filesystem;

Factory::Factory(const std::string& skeleton, const std::string& config_file):
    Factory(skeleton, config_file, "") {}


Factory::Factory(const std::string& skeleton, const std::string& config_file, const std::string& output_dir) {

    m_output_dir = output_dir;
    if (! fs::exists(m_output_dir))
        fs::create_directory(m_output_dir);

    // Open skeleton, and extract the list of all the branches in tree
    std::cout << "Extracting list of branches from skeleton..." << std::endl;
    std::unique_ptr<TChain> t(new TChain("t"));
    t->Add(skeleton.c_str());

    // Get list of all branches
    TObjArray* root_tree_branches = t->GetListOfBranches();
    for (size_t i = 0; i < static_cast<size_t>(root_tree_branches->GetEntries()); i++) {
        TBranch* b = static_cast<TBranch*>(root_tree_branches->UncheckedAt(i));

        Branch branch;
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

        m_tree_branches.emplace(branch.name, branch);
    }
    std::cout << "Done." << std::endl;

    std::FILE* f = std::fopen(config_file.c_str(), "r");
    if (!f) {
        throw std::runtime_error("Failed to open '" + config_file + "'");
    }

    Py_Initialize();

    // Get a reference to the main module
    // and global dictionary
    PyObject* main_module = PyImport_AddModule("__main__");
    m_global_dict = PyModule_GetDict(main_module);

    // If PyROOT is used inside the script, it performs some cleanups when the python env. is destroyed. This cleanup makes ROOT unusable afterwards.
    // The cleanup function is registered with the `atexit` module.
    // The solution is to not execute the cleanup function. For that, before destroying the python env, we check the list of exit functions,
    // and delete the one from PyROOT if found

    // Ensure the module is loaded
    PyObject* atexit_module = PyImport_ImportModule("atexit");

    // Execute the script
    PyObject* script_result = PyRun_File(f, config_file.c_str(), Py_file_input, m_global_dict, m_global_dict);

    if (! script_result) {
        PyErr_Print();
        throw std::runtime_error("");
    }

    std::cout << std::endl << "Summary:" << std::endl;

    // Parse include path, include files
    PyObject* py_include_dirs = PyDict_GetItemString(m_global_dict, "include_directories");
    if (py_include_dirs) {
        // Supposed to be a list of string, where each entry is a new include directory

        if (! PyList_Check(py_include_dirs)) {
            throw std::runtime_error("The 'include_directories' variable is not a list");
        }

        size_t l = PyList_Size(py_include_dirs);

        for (size_t i = 0; i < l; i++) {
            PyObject* item = PyList_GetItem(py_include_dirs, i);
            if (! PyString_Check(item) ) {
                throw std::runtime_error("The items of the 'include_directories' list must be strings");
            }

            std::string directory = PyString_AsString(item);
            if (!fs::exists(directory)) {
                std::cout << "Warning: include directory '" << directory << "' does not exist" << std::endl;
            }

            m_build_customization.include_directories.emplace(directory);
        }
        std::cout << "    - " << m_build_customization.include_directories.size() << " include directories" << std::endl;
    }

    PyObject* py_headers = PyDict_GetItemString(m_global_dict, "headers");
    if (py_headers) {
        // Supposed to be a list of string, where each entry is a new header to include
        // In the template, it'll be resolved as '#include <STRING>'

        if (! PyList_Check(py_headers)) {
            throw std::runtime_error("The 'headers' variable is not a list");
        }

        size_t l = PyList_Size(py_headers);

        for (size_t i = 0; i < l; i++) {
            PyObject* item = PyList_GetItem(py_headers, i);
            if (! PyString_Check(item) ) {
                throw std::runtime_error("The items of the 'headers' list must be strings");
            }

            std::string header = PyString_AsString(item);
            m_build_customization.headers.emplace(header);
        }
        std::cout << "    - " << m_build_customization.headers.size() << " headers" << std::endl;
    }

    PyObject* py_sources = PyDict_GetItemString(m_global_dict, "sources");
    if (py_sources) {
        // Supposed to be a list of string, where each entry is a new source file to compile

        if (! PyList_Check(py_sources)) {
            throw std::runtime_error("The 'sources' variable is not a list");
        }

        size_t l = PyList_Size(py_sources);

        for (size_t i = 0; i < l; i++) {
            PyObject* item = PyList_GetItem(py_sources, i);
            if (! PyString_Check(item) ) {
                throw std::runtime_error("The items of the 'sources' list must be strings");
            }

            std::string source = PyString_AsString(item);
            if (!fs::exists(source)) {
                std::cout << "Warning: source file '" << source << "' does not exist" << std::endl;
            }

            m_build_customization.sources.emplace(source);
        }
        std::cout << "    - " << m_build_customization.sources.size() << " source files" << std::endl;
    }

    // List of libraries to link against
    PyObject* py_libs = PyDict_GetItemString(m_global_dict, "libraries");
    if (py_libs) {

        if (! PyList_Check(py_libs)) {
            throw std::runtime_error("The 'libraries' variable is not a list");
        }

        size_t l = PyList_Size(py_libs);

        for (size_t i = 0; i < l; i++) {
            PyObject* item = PyList_GetItem(py_libs, i);
            if (! PyString_Check(item) ) {
                throw std::runtime_error("The items of the 'libraries' list must be strings");
            }

            std::string library = PyString_AsString(item);
            m_build_customization.libraries.emplace(library);
        }

        std::cout << "    - " << m_build_customization.libraries.size() << " libraries" << std::endl;
    }

    // Where to find the libraries
    PyObject* py_library_dirs = PyDict_GetItemString(m_global_dict, "library_directories");
    if (py_library_dirs) {
        // Supposed to be a list of string, where each entry is a new directory in which libraries are looked for

        if (! PyList_Check(py_library_dirs)) {
            throw std::runtime_error("The 'library_directories' variable is not a list");
        }

        size_t l = PyList_Size(py_library_dirs);

        for (size_t i = 0; i < l; i++) {
            PyObject* item = PyList_GetItem(py_library_dirs, i);
            if (! PyString_Check(item) ) {
                throw std::runtime_error("The items of the 'library_directories' list must be strings");
            }

            std::string directory = PyString_AsString(item);
            if (!fs::exists(directory)) {
                std::cout << "Warning: library directory '" << directory << "' does not exist" << std::endl;
            }

            m_build_customization.library_directories.emplace(directory);
        }
        std::cout << "    - " << m_build_customization.library_directories.size() << " library directories" << std::endl;
    }

    // Retrieve list of additional branches
    PyObject* py_extra_branches = PyDict_GetItemString(m_global_dict, "extra_branches");
    if (py_extra_branches) {

        if (! PyList_Check(py_extra_branches)) {
            throw std::runtime_error("The 'extra_branches' variable is not a list");
        }

        size_t l = PyList_Size(py_extra_branches);

        for (size_t i = 0; i < l; i++) {
            PyObject* item = PyList_GetItem(py_extra_branches, i);
            if (! PyString_Check(item) ) {
                throw std::runtime_error("The items of the 'extra_branches' list must be strings");
            }

            m_extra_branches.emplace( PyString_AsString(item) );
        }
        std::cout << "    - " << m_extra_branches.size() << " extra branches" << std::endl;

    }

    // Extra code specified by the user
    PyObject* py_before_loop = PyDict_GetItemString(m_global_dict, "code_before_loop");
    if (py_before_loop) {
        if (! PyString_Check(py_before_loop)) {
            throw std::runtime_error("The 'before_loop' variable is not a string");
        }

        m_user_code.before_loop = PyString_AsString(py_before_loop);
        std::cout << "    - Has code before loop" << std::endl;
    }

    PyObject* py_in_loop = PyDict_GetItemString(m_global_dict, "code_in_loop");
    if (py_in_loop) {
        if (! PyString_Check(py_in_loop)) {
            throw std::runtime_error("The 'in_loop' variable is not a string");
        }

        m_user_code.in_loop = PyString_AsString(py_in_loop);
        std::cout << "    - Has code in loop" << std::endl;
    }

    PyObject* py_after_loop = PyDict_GetItemString(m_global_dict, "code_after_loop");
    if (py_after_loop) {
        if (! PyString_Check(py_after_loop)) {
            throw std::runtime_error("The 'after_loop' variable is not a string");
        }

        m_user_code.after_loop = PyString_AsString(py_after_loop);
        std::cout << "    - Has code after loop" << std::endl;
    }

    // Retrieve dict of sample weights
    // The key can be set in the sample json to indicate which sample weight to use
    // The value is any valid C++ code, which will be added in the global `getSampleWeight`
    // function.
    PyObject* py_sample_weights = PyDict_GetItemString(m_global_dict, "sample_weights");
    if (py_sample_weights) {
        if (! PyDict_Check(py_sample_weights)) {
            throw std::runtime_error("The 'sample_weights' variable is not a dictionnary");
        }

        PyObject* key, *value;
        Py_ssize_t pos = 0;
        while (PyDict_Next(py_sample_weights, &pos, &key, &value)) {
            if (! PyString_Check(key)) {
                throw std::runtime_error("Keys of 'sample_weights' dict must be strings");
            }

            if (! PyString_Check(value)) {
                throw std::runtime_error("Values of 'sample_weights' dict must be strings");
            }

            m_sample_weights.emplace(PyString_AsString(key), PyString_AsString(value));
        }
        std::cout << "    - " << m_sample_weights.size() << " sample weights" << std::endl;
    }

    // Remove any exit handler added by ROOT
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
}

Factory::~Factory() {
    Py_Finalize();
}

bool Factory::run() {
    if (! parse_config_file(m_global_dict))
        return false;

    std::cout << std::endl;

    std::set<std::string> identifiers;
    std::string beforeLoop, inLoop, afterLoop;
    create_templates(identifiers, beforeLoop, inLoop, afterLoop);

    // Update the list of identifiers with the extra branches requested by the user
    identifiers.insert(m_extra_branches.begin(), m_extra_branches.end());

    // Parse sample weights, there's maybe some branches used
    for (const auto& it: m_sample_weights) {
        if (! parser.parse(it.second, identifiers)) {
            std::cerr << "Warning: " << it.second << " failed to parse." << std::endl;
        }
    }

    // Collect the list of branches used by all formulas
    std::string branches;
    for (const auto& id: identifiers) {
        auto branch = m_tree_branches.find(id);
        if (branch == m_tree_branches.end())
            continue;

        branches += "const " + branch->second.type + "& " + branch->second.name + " = tree[\"" + branch->second.name + "\"].read<" + branch->second.type + ">();\n        ";
    }

    // Build includes
    std::string includes;
    for (const auto& h: m_build_customization.headers) {
        includes += "#include <" + h + ">\n";
    }

     // Create `getSampleWeight` function
    std::string sample_weight_function = "    if ((m_dataset.sample_weight_key.empty()) || (m_dataset.sample_weight_key == \"none\")) {\n        return 1.;\n    }\n";
    for (const auto& it: m_sample_weights) {
        sample_weight_function += R"(    if (m_dataset.sample_weight_key == ")" + it.first + R"(") {)" + "\n";
        sample_weight_function += "        return (" + it.second + ");\n";
        sample_weight_function += "    }\n";
    }

    sample_weight_function += "\n    return 1.;";

    std::string tree_read_all =  read_whole_tree() ? "true" : "false";

    std::string output;

    // Main source file
    ctemplate::TemplateDictionary source("source");
    source.SetValue("CLASS_NAME", name());
    source.SetValue("SUFFIX", suffix());
    source.SetValue("USER_INCLUDES", includes);
    source.SetValue("USER_CODE_BEFORE_LOOP", m_user_code.before_loop);
    source.SetValue("USER_CODE_IN_LOOP", m_user_code.in_loop);
    source.SetValue("USER_CODE_AFTER_LOOP", m_user_code.after_loop);
    source.SetValue("SAMPLE_WEIGHT_IMPL", sample_weight_function);
    source.SetValue("CODE_BEFORE_LOOP", beforeLoop);
    source.SetValue("CODE_IN_LOOP", inLoop);
    source.SetValue("CODE_AFTER_LOOP", afterLoop);
    source.SetValue("TREE_READ_ALL", tree_read_all);

    ctemplate::ExpandTemplate(get_template("Main.cc"), ctemplate::DO_NOT_STRIP, &source, &output);

    fs::ofstream out;

    out.open((m_output_dir / (name() + ".cc")));
    out << output;
    out.close();
    
    // Header file
    output.clear();
    ctemplate::TemplateDictionary header("header");
    header.SetValue("CLASS_NAME", name());
    header.SetValue("BRANCHES", branches);

    ctemplate::ExpandTemplate(get_template("Main.h"), ctemplate::DO_NOT_STRIP, &header, &output);

    out.open((m_output_dir / (name() + ".h")));
    out << output;
    out.close();

    // Customize CMakeLists.txt

    // Make external sources accessible to plotter
    std::string include_directories;
    for (const auto& d: m_build_customization.include_directories) {
        include_directories += "include_directories(\"" + d.string() + "\")\n";
    }
    
    std::string sources;
    for (const auto& s: m_build_customization.sources)
      sources += s + " ";

    std::string executable = name() + ".exe";
    std::transform(executable.begin(), executable.end(), executable.begin(), ::tolower);
    ctemplate::TemplateDictionary cmake("cmake");
    cmake.SetValue("NAME", name());
    cmake.SetValue("EXECUTABLE", executable);
    cmake.SetValue("USER_INCLUDES", include_directories);
    cmake.SetValue("USER_SOURCES", sources);

    if (!m_build_customization.library_directories.empty()) {
        cmake.ShowSection("HAS_LIBRARY_DIRECTORIES");
        for (const auto& d: m_build_customization.library_directories) {
            auto dict = cmake.AddSectionDictionary("LIBRARY_DIRECTORIES");
            dict->SetValue("LIBRARY_DIRECTORY", d);
        }
    }

    if (!m_build_customization.libraries.empty()) {
        for (const auto& lib: m_build_customization.libraries) {
            auto dict = cmake.AddSectionDictionary("USER_LIBRARIES");
            dict->SetValue("LIBRARY", lib);
        }
    }

    std::string cmakelists_content;
    ctemplate::ExpandTemplate(get_template("CMakeLists.txt"), ctemplate::DO_NOT_STRIP, &cmake, &cmakelists_content);

    out.open(m_output_dir / "CMakeLists.txt");
    out << cmakelists_content;
    out.close();

    std::cout << std::endl;
    std::cout << "All done. Generated code available in " << m_output_dir.native() << std::endl;

    return true;
}

std::string Factory::get_random_name() {

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

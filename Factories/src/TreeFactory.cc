#include <TreeFactory.h>

#include <iostream>

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
            branch.unique_name = Factory::get_random_name();
            tree.branches.push_back(branch);
        }
    }

    return true;    
}

bool TreeFactory::parse_config_file(PyObject* global_dict) {

    const std::string TREE_KEY_NAME = "tree";

    PyObject* py_tree = PyDict_GetItemString(m_global_dict, TREE_KEY_NAME.c_str());
    if (!py_tree) {
        std::cerr << "No '" << TREE_KEY_NAME << "' variable declared in python script" << std::endl;
        return false;
    }

    if (! PyDict_Check(py_tree)) {
        std::cerr << "The '" << TREE_KEY_NAME << "' variable is not a dictionary" << std::endl;
        return false;
    }

    bool ret = tree_from_PyObject(py_tree, m_tree);
    if (ret)
        std::cout << "    - " << m_tree.branches.size() << " branches declared" << std::endl;

    return ret;
}

bool TreeFactory::create_templates(std::set<std::string>& identifiers, std::string& beforeLoop, std::string& inLoop, std::string& afterLoop) {

    beforeLoop.clear();
    inLoop.clear();
    afterLoop.clear();

    beforeLoop = R"(    std::unique_ptr<TFile> outfile(TFile::Open(output_file.c_str(), "recreate"));
    TTree* output_tree_ = new TTree(")" + m_tree.name + R"(", "Skimmed tree");
    ROOT::TreeWrapper output_tree(output_tree_);
    float& sample_weight_branch = output_tree["sample_weight"].write<float>();
)";

    // Tree cut
    if (!parser.parse(m_tree.cut, identifiers))
        std::cerr << "Warning: " << m_tree.cut << " failed to parse." << std::endl;

    inLoop = "        if (! (" + m_tree.cut + ")) { continue; }\n";

    for (auto& b: m_tree.branches) {

        if (! parser.parse(b.variable, identifiers))
            std::cerr << "Warning: " << b.variable << " failed to parse." << std::endl;

        beforeLoop += "    " + b.type + "& " + b.unique_name + " = output_tree[\"" + b.name + "\"].write<" + b.type + ">();\n";
        inLoop += "        " + b.unique_name + " = (" + b.variable + ");\n";
    }

    inLoop += R"(        sample_weight_branch = getSampleWeight();

        output_tree.fill();
    )";

    afterLoop = R"(    outfile->cd();
    output_tree_->Write();
)";

    return true;
}

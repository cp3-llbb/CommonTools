#pragma once

#include <Factory.h>

#include <vector>

struct OutputBranch {
    std::string name;
    std::string unique_name;
    std::string variable;
    std::string type;
};

struct Tree {
    std::string name;
    std::string cut;
    bool clone;
    std::vector<OutputBranch> branches;
};

class TreeFactory: public Factory {
using Factory::Factory;

protected:
    virtual std::string name() const override {
        return "Skimmer";
    }

    virtual std::string suffix() const override {
        return "skim";
    }

    virtual bool read_whole_tree() const override {
        return m_tree.clone;
    }

    virtual bool parse_config_file(PyObject* global_dict) override;
    virtual bool create_templates(std::set<std::string>& identifiers, std::string& beforeLoop, std::string& inLoop, std::string& afterLoop) override;

private:
    Tree m_tree;
};

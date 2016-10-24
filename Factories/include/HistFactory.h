#pragma once

#include <Factory.h>

#include <vector>

struct Plot {
    std::string unique_name;
    std::string name;
    std::string variable;
    std::string cut;
    std::string weight;
    std::string binning;
    std::string normalize_to;
    std::string output_root_folder;

    std::string title;
    std::string x_axis;
    std::string y_axis;
    std::string z_axis;
};

class HistFactory: public Factory {
using Factory::Factory;

protected:
    virtual std::string name() const override {
        return "Plotter";
    }

    virtual std::string suffix() const override {
        return "histos";
    }

    virtual bool parse_config_file(PyObject* global_dict) override;
    virtual bool create_templates(std::set<std::string>& identifiers, std::string& beforeLoop, std::string& inLoop, std::string& afterLoop) override;

private:
    std::vector<Plot> m_plots;
};

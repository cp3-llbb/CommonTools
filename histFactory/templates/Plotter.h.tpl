// vim: syntax=cpp

#pragma once

#include <Rtypes.h>
#include <vector>
#include <string>
#include <map>
#include <Math/Vector4D.h>

// Generated automatically
#include <classes.h>

#include <cp3_llbb/TreeWrapper/interface/TreeWrapper.h>

// No other choices, as ROOT strips the 'std' namespace from types...
using namespace std;

template<typename T>
size_t Length$(const T& t) {
    return t.size();
}

struct Dataset {
    std::string name;
    std::string db_name;
    std::string output_name;
    std::string tree_name;
    std::string path;
    std::vector<std::string> files;
    std::string cut;
};

class Plotter {
    public:
        Plotter(const Dataset& dataset, ROOT::TreeWrapper& tree):
            m_dataset(dataset), tree(tree) {};
        virtual ~Plotter() {};

        void plot(const std::string&);

    private:
        Dataset m_dataset;
        ROOT::TreeWrapper& tree;

        // List of branches
        {{BRANCHES}}
};

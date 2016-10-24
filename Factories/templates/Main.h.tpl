// vim: syntax=cpp

#pragma once

#include <type_traits>
#include <vector>
#include <string>
#include <map>
#include <memory>

// ROOT
#include <Rtypes.h>
#include <TH1.h>
#include <TH2.h>
#include <TH3.h>
#include <TChain.h>
#include <TTreeFormula.h>
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

// Traits to check if a given typename is iterable

template<typename T> struct is_stl_container_like
{
    typedef typename std::remove_const<typename std::remove_reference<T>::type>::type test_type;

    template<typename A> static constexpr bool test(
            A * pt,
            A const * cpt = nullptr,
            decltype(pt->begin()) * = nullptr,
            decltype(pt->end()) * = nullptr,
            decltype(cpt->begin()) * = nullptr,
            decltype(cpt->end()) * = nullptr,
            typename A::iterator * pi = nullptr,
            typename A::const_iterator * pci = nullptr,
            typename A::value_type * pv = nullptr) {

        typedef typename A::iterator iterator;
        typedef typename A::const_iterator const_iterator;
        typedef typename A::value_type value_type;
        return  std::is_same<decltype(pt->begin()),iterator>::value &&
            std::is_same<decltype(pt->end()),iterator>::value &&
            std::is_same<decltype(cpt->begin()),const_iterator>::value &&
            std::is_same<decltype(cpt->end()),const_iterator>::value &&
            std::is_same<decltype(**pi),value_type &>::value &&
            std::is_same<decltype(**pci),value_type const &>::value;

    }

    template<typename A> static constexpr bool test(...) {
        return false;
    }

    static const bool value = test<test_type>(nullptr);
};

struct Dataset {
    std::string name;
    std::string db_name;
    std::string output_name;
    std::string tree_name;
    std::string path;
    std::vector<std::string> files;
    std::string cut;
    double cross_section;
    double event_weight_sum;
    std::map<std::string, double> extras_event_weight_sum;
    bool is_data;
    std::string sample_weight_key;
    uint64_t event_start = 0;
    uint64_t event_end;
    bool event_end_filled = false;
};

class {{CLASS_NAME}} {
    public:
        {{CLASS_NAME}}(const Dataset& dataset, TChain* ttree):
            m_dataset(dataset), tree(ttree), m_sample_cut(nullptr), raw_tree(ttree)
            {
                if(dataset.cut != "" && dataset.cut != "1"){
                    m_sample_cut = new TTreeFormula("sample_cut", dataset.cut.c_str(), ttree);
                    ttree->SetNotify(m_sample_cut);
                }

                tree.setEntry(dataset.event_start);
                tree.stopAt(dataset.event_end);
            };

        virtual ~{{CLASS_NAME}}() { delete m_sample_cut; };

        void work(const std::string&);

    private:

        // Helper functions to fill an histogram
        template<typename T, typename std::enable_if<!is_stl_container_like<T>::value, bool>::type = 0> void fill(TH1* h, const T& value, double weight) {
            h->Fill(value, weight);
        }

        template<typename T, typename std::enable_if<is_stl_container_like<T>::value, bool>::type = 0> void fill(TH1* h, const T& value, double weight) {
            for (const auto& v: value)
                h->Fill(v, weight);
        }

        // 2D
        template<typename T, typename U> void fill(TH2* h, const T& value_x, const U& value_y, double weight) {
            h->Fill(value_x, value_y, weight);
        }

        // 3D
        template<typename T, typename U, typename V> void fill(TH3* h, const T& value_x, const U& value_y, const V& value_z, double weight) {
            h->Fill(value_x, value_y, value_z, weight);
        }

        double getSampleWeight();

        Dataset m_dataset;
        ROOT::TreeWrapper tree;
        TTreeFormula* m_sample_cut;
        TChain* raw_tree;

        // List of branches
        {{BRANCHES}}
};

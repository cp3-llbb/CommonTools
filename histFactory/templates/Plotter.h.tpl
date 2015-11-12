// vim: syntax=cpp

#pragma once

#include <type_traits>
#include <vector>
#include <string>
#include <map>

// ROOT
#include <Rtypes.h>
#include <TH1.h>
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
};

class Plotter {
    public:
        Plotter(const Dataset& dataset, ROOT::TreeWrapper& tree):
            m_dataset(dataset), tree(tree) {};
        virtual ~Plotter() {};

        void plot(const std::string&);

    private:

        // Helper functions to fill an histogram
        template<typename T> typename std::enable_if<!is_stl_container_like<T>::value, bool>::type fill(TH1* h, const T& value, double weight) {
            h->Fill(value, weight);
        }

        template<typename T> typename std::enable_if<is_stl_container_like<T>::value, bool>::type fill(TH1* h, const T& value, double weight) {
            for (const auto& v: value)
                h->Fill(v, weight);
        }

        Dataset m_dataset;
        ROOT::TreeWrapper& tree;

        // List of branches
        {{BRANCHES}}
};

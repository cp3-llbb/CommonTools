#pragma once

#include <Python.h>

#include <regex>
#include <set>
#include <string>
#include <unordered_map>
#include <vector>

#include <formula_parser.h>
#include "config.h"

#include <boost/filesystem.hpp>

#include <ctemplate/template.h>

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

struct BuildCustomization {
    std::set<boost::filesystem::path> include_directories;
    std::set<std::string> headers;
    std::set<std::string> library_directories;
    std::set<std::string> libraries;
    std::set<std::string> sources;
};

struct UserCode {
    std::string before_loop;
    std::string in_loop;
    std::string after_loop;
};

struct Branch {
    std::string name;
    std::string type;
};

class Factory {
    public:
        Factory(const std::string& skeleton, const std::string& config_file);
        Factory(const std::string& skeleton, const std::string& config_file, const std::string& output_dir);

        virtual ~Factory();

        bool run();

        static std::string get_random_name();

    protected:
        inline std::string get_template(const std::string& name) {
            std::string p = TEMPLATE_PATH;
            p += "/" + name + ".tpl";

            return p;
        }

        virtual std::string name() const = 0;
        virtual std::string suffix() const = 0;

        virtual bool parse_config_file(PyObject* global_dict) = 0;
        virtual bool create_templates(std::set<std::string>& identifiers, std::string& beforeLoop, std::string& inLoop, std::string& afterLoop) = 0;

        PyObject* m_global_dict;

        parser::parser parser;
        BuildCustomization m_build_customization;
        UserCode m_user_code;
        std::set<std::string> m_extra_branches;
        std::unordered_map<std::string, std::string> m_sample_weights;

    private:
        boost::filesystem::path m_output_dir;
        std::unordered_map<std::string, Branch> m_tree_branches;
};

inline std::vector<std::string> split(const std::string& input, const std::string& regex) {
    std::regex re(regex);
    std::sregex_token_iterator
        first(input.begin(), input.end(), re, -1),
        last;

    return {first, last};
}

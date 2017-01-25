#include <HistFactory.h>

#include <iostream>

bool plot_from_PyObject(PyObject* value, Plot& plot) {
    static PyObject* PY_NAME = PyString_FromString("name");
    static PyObject* PY_VARIABLE = PyString_FromString("variable");
    static PyObject* PY_PLOT_CUT = PyString_FromString("plot_cut");
    static PyObject* PY_NORMALIZE_TO = PyString_FromString("normalize-to");
    static PyObject* PY_FOLDER = PyString_FromString("folder");
    static PyObject* PY_WEIGHT = PyString_FromString("weight");
    static PyObject* PY_BINNING = PyString_FromString("binning");
    static PyObject* PY_TITLE = PyString_FromString("title");
    static PyObject* PY_X_AXIS = PyString_FromString("x-axis");
    static PyObject* PY_Y_AXIS = PyString_FromString("y-axis");
    static PyObject* PY_Z_AXIS = PyString_FromString("z-axis");
    
    static PyObject* PY_WEIGHT_DATA = PyString_FromString("allow-weighted-data");

    if (! PyDict_Check(value)) {
        std::cerr << "Error: plots dictionnary value must be a dictionnary" << std::endl;
    }

    CHECK_AND_GET(plot.name, PY_NAME);
    CHECK_AND_GET(plot.variable, PY_VARIABLE);
    CHECK_AND_GET(plot.binning, PY_BINNING);

    plot.cut = "1";
    GET(plot.cut, PY_PLOT_CUT);
    
    plot.normalize_to = "nominal";
    GET(plot.normalize_to, PY_NORMALIZE_TO);

    plot.output_root_folder = "";
    GET(plot.output_root_folder, PY_FOLDER);

    plot.weight = "1.";
    GET(plot.weight, PY_WEIGHT);

    GET(plot.title, PY_TITLE);
    GET(plot.x_axis, PY_X_AXIS);
    GET(plot.y_axis, PY_Y_AXIS);
    GET(plot.z_axis, PY_Z_AXIS);

    plot.allow_weight_on_data = false;
    GET_BOOL(plot.allow_weight_on_data, PY_WEIGHT_DATA);

    return true;
}

std::string getHistogramTypeForDimension(size_t dimension) {
    switch (dimension) {
        case 1:
            return "TH1F";
        case 2:
            return "TH2F";
        case 3:
            return "TH3F";
        default:
            throw std::invalid_argument("Invalid dimension");
    }
}

std::string buildArrayForVariableBinning(std::string& binning, const size_t dimension, const std::string &name){
    std::string array;

    for(size_t dim_index = 0; dim_index < dimension; ++dim_index){
      size_t brace_start = binning.find_first_of("{");
      size_t brace_end = binning.find_first_of("}");

      if(brace_start == std::string::npos || brace_end == std::string::npos || brace_end < brace_start)
        continue;

      array += "double ";
    
      std::string array_name = name + "_" + std::to_string(dim_index);
      array += array_name + "[] " + binning.substr(brace_start, brace_end - brace_start + 1) + ";\n";

      binning.replace(brace_start, brace_end - brace_start + 1, std::string("&(") + array_name + "[0])");
  }

  return array;
}

bool HistFactory::parse_config_file(PyObject* global_dict) {

    // Retrieve list of plots
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
            plot.unique_name = get_random_name();
            m_plots.push_back(plot);
        }
    }

    std::cout << "    - " << m_plots.size() << " plots declared" << std::endl;

    // Other options
    PyObject* py_optimize = PyDict_GetItemString(global_dict, "optimize_plots");
    m_optimize = py_optimize && PyObject_IsTrue(py_optimize);

    if (m_optimize) {
        std::set<std::string> all_weights;
        std::set<std::string> all_cuts;
        for (const auto& plot: m_plots) {
            all_cuts.emplace(plot.cut);
            if (plot.weight.length() > 0) {
                all_weights.emplace(plot.weight);
            }
        }

        for (const auto& cut: all_cuts) {
            for (const auto& weight: all_weights) {
                Group group;
                group.weight = weight;
                group.cut = cut;

                bool allow_weight_on_data = false;
                bool first_plot = true;

                // Loop over plots, and find those which share the same weight and cut expression
                for (auto& plot: m_plots) {
                    if (plot.cut == cut && plot.weight == weight) {
                        if (first_plot) {
                            first_plot = false;
                            group.allow_weight_on_data = plot.allow_weight_on_data;
                        } else {
                            // Ensure all plots have the same value for allow_weight_on_data
                            if (group.allow_weight_on_data != plot.allow_weight_on_data) {
                                throw std::runtime_error("Some plots inside a group does not have the same value for 'allow_weight_on_data'. This is not supported for the moment.");
                            }
                        }

                        group.plots.push_back(plot);
                    }
                }

                // Don't care of groups with one plot
                if (group.plots.size() > 1) {
                    m_groups.push_back(group);

                    // Remove plots added to this group from the plot list
                    m_plots.erase(std::remove_if(
                                m_plots.begin(), m_plots.end(),
                                [&group](const Plot& plot) {
                                    auto it = std::find_if(
                                        group.plots.begin(), group.plots.end(),
                                        [&plot](const Plot& rhs) {
                                            return plot.unique_name == rhs.unique_name;
                                        });

                                    return it != group.plots.end();
                                }), m_plots.end());
                }
            }
        }

        std::cout << "After optimizations, found " << m_groups.size() << " groups of plot sharing the same weight and cut expression" << std::endl;

    }

    return true;
}

void HistFactory::render_plot(const Plot& p, std::set<std::string>& identifiers, std::string& beforeLoop, std::string& inLoop, std::string& afterLoop) {

    if (p.cut.length() > 0 && ! parser.parse(p.cut, identifiers))
        std::cerr << "Warning: " << p.cut << " failed to parse." << std::endl;

    if (p.weight.length() > 0 && !parser.parse(p.weight, identifiers))
        std::cerr << "Warning: " << p.weight << " failed to parse." << std::endl;

    std::vector<std::string> splitted_variables = split(p.variable, ":::");
    for (const std::string& variable: splitted_variables) {
        if (!parser.parse(variable, identifiers))
            std::cerr << "Warning: " << variable << " failed to parse." << std::endl;
    }

    std::string binning = p.binning;
    binning.erase(std::remove_if(binning.begin(), binning.end(), [](char chr) { return chr == '(' || chr == ')'; }), binning.end());

    // If a variable bin size is specified, declare array that will be passed as array to histogram constructor
    if (binning.find("{") != std::string::npos){
      std::string arrayString = buildArrayForVariableBinning(binning, splitted_variables.size(), p.name);
      beforeLoop = arrayString;
    }

    std::string title = p.title + ";" + p.x_axis + ";" + p.y_axis + ";" + p.z_axis;
    std::string histogram_type = getHistogramTypeForDimension(splitted_variables.size());

    beforeLoop += "    std::unique_ptr<" + histogram_type + "> " + p.unique_name + "(new " + histogram_type + "(\"" + p.unique_name + "\", \"" + title + "\", " + binning + ")); " + p.unique_name + "->SetDirectory(nullptr);\n";

    std::string variable_string;
    for (size_t i = 0; i < splitted_variables.size(); i++) {
        variable_string += splitted_variables[i];
        if (i != splitted_variables.size() - 1)
            variable_string += ", ";
    }

    ctemplate::TemplateDictionary plot("plot");
    plot.SetValueAndShowSection("CUT", p.cut, "HAS_CUT");
    plot.SetValueAndShowSection("WEIGHT", p.weight, "HAS_WEIGHT");
    plot.SetValue("VAR", variable_string);
    plot.SetValue("HIST", p.unique_name);

    if (! p.allow_weight_on_data)
        plot.ShowSection("NO_WEIGHTS_ON_DATA");

    ctemplate::ExpandTemplate(get_template("Plot"), ctemplate::DO_NOT_STRIP, &plot, &inLoop);
}

bool HistFactory::create_templates(std::set<std::string>& identifiers, std::string& beforeLoop, std::string& inLoop, std::string& afterLoop) {

    beforeLoop.clear();
    inLoop.clear();
    afterLoop.clear();

    std::set<std::string> normalize_to;

    if (!m_groups.empty()) {

        for (const auto& group: m_groups) {

            if (! parser.parse(group.cut, identifiers))
                std::cerr << "Warning: " << group.cut << " failed to parse." << std::endl;

            if (! parser.parse(group.weight, identifiers))
                std::cerr << "Warning: " << group.weight << " failed to parse." << std::endl;
        
            std::string group_plots;
            for (const auto& plot: group.plots) {
                Plot p = plot;
                
                // Remove cut and weight expression
                p.cut.clear();
                p.weight.clear();

                std::string plot_beforeLoop, plot_inLoop, plot_afterLoop;
                render_plot(p, identifiers, plot_beforeLoop, plot_inLoop, plot_afterLoop);

                beforeLoop += plot_beforeLoop;
                group_plots += plot_inLoop;
            }

            ctemplate::TemplateDictionary group_dict("group");
            group_dict.SetValue("CUT", group.cut);
            group_dict.SetValue("WEIGHT", group.weight);
            group_dict.SetValue("PLOTS", group_plots);

            if (! group.allow_weight_on_data)
                group_dict.ShowSection("NO_WEIGHTS_ON_DATA");

            std::string group_content;
            ctemplate::ExpandTemplate(get_template("Group"), ctemplate::DO_NOT_STRIP, &group_dict, &group_content);

            inLoop += group_content;
        }
    }

    size_t index = 0;
    for (auto& p: m_plots) {

        normalize_to.emplace(p.normalize_to);

        if ((index % 200) == 0)
            std::cout << "Parsing plot #" << index << " / " << m_plots.size() << std::endl;

        index++;

        std::string plot_beforeLoop;
        std::string plot_inLoop;
        std::string plot_afterLoop;

        render_plot(p, identifiers, plot_beforeLoop, plot_inLoop, plot_afterLoop);

        beforeLoop += plot_beforeLoop;
        inLoop += plot_inLoop;
    }

    std::cout << "Done." << std::endl;

    // Open output file, after the loop
    beforeLoop += R"(
    std::unique_ptr<TFile> outfile(TFile::Open(output_file.c_str(), "recreate"));
)";

    afterLoop += R"(
    outfile->cd();

)";

    std::vector<Plot> all_plots(m_plots);
    for (const auto& group: m_groups) {
        all_plots.insert(all_plots.end(), group.plots.begin(), group.plots.end());
    }

    for (const auto& p: all_plots) {
        ctemplate::TemplateDictionary save_plot("save_plot");
        save_plot.SetValue("UNIQUE_NAME", p.unique_name);
        save_plot.SetValue("PLOT_NAME", p.name);

        std::string sample_scale = "m_dataset.cross_section / m_dataset.extras_event_weight_sum[\"" + p.normalize_to + "\"]";
        save_plot.SetValue("SAMPLE_SCALE", sample_scale);
        if (! p.output_root_folder.empty()) {
            save_plot.ShowSection("IN_FOLDER");
            save_plot.SetValue("FOLDER", p.output_root_folder);
        }
        ctemplate::ExpandTemplate(get_template("SavePlot"), ctemplate::DO_NOT_STRIP, &save_plot, &afterLoop);
    }

    std::string text_ensure_normalization;
    for (auto& n: normalize_to) {
        ctemplate::TemplateDictionary d("d");
        d.SetValue("NAME", n);
        ctemplate::ExpandTemplate(get_template("EnsureNormalization"), ctemplate::DO_NOT_STRIP, &d, &text_ensure_normalization);
    }

    beforeLoop = text_ensure_normalization + "\n" + beforeLoop;

    return true;
}

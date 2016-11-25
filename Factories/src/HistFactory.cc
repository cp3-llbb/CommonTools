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

    if (! PyDict_Check(value)) {
        std::cerr << "Error: plots dictionnary value must be a dictionnary" << std::endl;
    }

    CHECK_AND_GET(plot.name, PY_NAME);
    CHECK_AND_GET(plot.variable, PY_VARIABLE);
    CHECK_AND_GET(plot.cut, PY_PLOT_CUT);
    CHECK_AND_GET(plot.binning, PY_BINNING);

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

    return true;
}

bool HistFactory::create_templates(std::set<std::string>& identifiers, std::string& beforeLoop, std::string& inLoop, std::string& afterLoop) {

    beforeLoop.clear();
    inLoop.clear();
    afterLoop.clear();

    std::set<std::string> normalize_to;
    size_t index = 0;
    for (auto& p: m_plots) {

        normalize_to.emplace(p.normalize_to);

        if ((index % 200) == 0)
            std::cout << "Parsing plot #" << index << " / " << m_plots.size() << std::endl;

        index++;

        // Create formulas
        if (! parser.parse(p.cut, identifiers))
            std::cerr << "Warning: " << p.cut << " failed to parse." << std::endl;
        if (! parser.parse(p.weight, identifiers))
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
          beforeLoop += arrayString;
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
        plot.SetValue("CUT", p.cut);
        plot.SetValue("WEIGHT", p.weight);
        plot.SetValue("VAR", variable_string);
        plot.SetValue("HIST", p.unique_name);

        ctemplate::ExpandTemplate(get_template("Plot"), ctemplate::DO_NOT_STRIP, &plot, &inLoop);
    }

    // Open output file, after the loop
    beforeLoop += R"(
    std::unique_ptr<TFile> outfile(TFile::Open(output_file.c_str(), "recreate"));
)";

    afterLoop += R"(
    outfile->cd();

)";

    for (auto& p: m_plots) {
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

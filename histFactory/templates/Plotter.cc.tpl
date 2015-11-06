// vim: syntax=cpp

#include <Plotter.h>

#include <memory>
#include <iostream>
#include <fstream>

#include <TChain.h>
#include <TH1F.h>
#include <TDirectory.h>
#include <TFile.h>

#include <json/json.h>
#include <tclap/CmdLine.h>

void Plotter::plot(const std::string& output_file) {

    {{HISTS_DECLARATION}}

    size_t index = 1;
    while (tree.next()) {

        if ((index - 1) % 1000 == 0)
            std::cout << "Processing entry " << index << " of " << tree.getEntries() << std::endl;

        double __weight = 0;

        {{PLOTS}}

        index++;
    }

    TDirectory* plots_directory = gDirectory;

    std::unique_ptr<TFile> outfile(TFile::Open(output_file.c_str(), "recreate"));
    {{SAVE_PLOTS}}
}

bool parse_datasets(const std::string& json_file, std::vector<Dataset>& datasets) {

    Json::Value root;
    {
        std::ifstream f(json_file);
        Json::Reader reader;
        if (! reader.parse(f, root, false)) {
            std::cerr << "Failed to parse '" << json_file << "'" << std::endl;
            return false;
        }
    }

    datasets.clear();

    // Looping over the different samples
    Json::Value::Members samples_str = root.getMemberNames();
    for (size_t index = 0; index < root.size(); index++) {

        const Json::Value& sample = root[samples_str[index]];
        Dataset dataset;

        // Mandatory fields
        dataset.name = samples_str[index];
        dataset.db_name = sample["db_name"].asString();
        dataset.cut = sample.get("sample_cut", "1").asString();
        dataset.tree_name = sample.get("tree_name", "t").asString();

        //dataset.output_name
        if (sample.isMember("output_name")) {
            dataset.output_name = sample["output_name"].asString();
        } else {
            dataset.output_name = dataset.db_name + "_histos";
        }

        // If a list of files is specified, only use those
        if (sample.isMember("files")) {
            Json::Value files = sample["files"];

            for(auto it = files.begin(); it != files.end(); ++it) {
                dataset.files.push_back((*it).asString());
            }
        } else if (sample.isMember("path")) {
            dataset.path = sample["path"].asString();
            dataset.files.push_back(dataset.path + "/*.root");
        }

        datasets.push_back(dataset);
    }

    return true;
}

int main(int argc, char** argv) {


    try {

        TCLAP::CmdLine cmd("Create histograms from trees", ' ', "0.2.0");

        TCLAP::ValueArg<std::string> datasetArg("d", "dataset", "JSON file describing the dataset to run on", true, "", "JSON file", cmd);
        TCLAP::ValueArg<std::string> outputArg("o", "output", "Output directory", false, "", "FOLDER", cmd);

        cmd.parse(argc, argv);

        std::vector<Dataset> datasets;
        parse_datasets(datasetArg.getValue(), datasets);

        std::string output_dir = outputArg.getValue();
        if (output_dir.empty())
            output_dir = ".";

        for (const Dataset& d: datasets) {
            std::cout << "Creating plots for dataset '" << d.name << "'" << std::endl;
            std::unique_ptr<TChain> t(new TChain(d.tree_name.c_str()));
            for (const std::string& file: d.files)
                t->Add(file.c_str());

            std::string output_file = output_dir + "/" + d.output_name + ".root";

            ROOT::TreeWrapper wrapped_tree(t.get());

            Plotter p(d, wrapped_tree);
            p.plot(output_file);
            std::cout << "Done. Output saved as '" << output_file << "'" << std::endl;
        }

    } catch (TCLAP::ArgException &e) {
        std::cerr << "error: " << e.error() << " for arg " << e.argId() << std::endl;
        return 1;
    }

    return 0;
}

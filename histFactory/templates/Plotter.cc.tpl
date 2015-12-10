// vim: syntax=cpp

#include <Plotter.h>

#include <memory>
#include <iostream>
#include <fstream>
#include <signal.h>

#include <TChain.h>
#include <TH1F.h>
#include <TH2F.h>
#include <TH3F.h>
#include <TFile.h>

#include <json/json.h>
#include <tclap/CmdLine.h>

volatile bool MUST_STOP = false;

void Plotter::plot(const std::string& output_file) {

{{HISTS_DECLARATION}}

    size_t index = 1;
    while (tree.next()) {

        if (MUST_STOP) {
            break;
        }

        if (m_sample_cut){
          if( !m_sample_cut->EvalInstance() )
            continue;
        }

        if ((index - 1) % 1000 == 0)
            std::cout << "Processing entry " << index << " of " << tree.getEntries() << std::endl;

        bool __cut = false;
        double __weight = 0;

{{PLOTS}}

        index++;
    }

    std::unique_ptr<TFile> outfile(TFile::Open(output_file.c_str(), "recreate"));

    double sample_scale = m_dataset.cross_section / m_dataset.event_weight_sum;
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

        if (sample.isMember("output_name")) {
            dataset.output_name = sample["output_name"].asString();
        } else {
            dataset.output_name = dataset.db_name + "_histos";
            if(sample.isMember("suffix"))
                dataset.output_name += sample["suffix"].asString();
        }
        
        if( std::find_if(datasets.begin(), datasets.end(), [&](const Dataset &d){ return d.output_name == dataset.output_name; }) != datasets.end() ){
            std::cout << "Warning: output name " << dataset.output_name << " already present.\n";
            std::cout << "Appending \"_" << index << "\" to avoid collision." << std::endl;
            dataset.output_name += "_" + std::to_string(index);
        }

        if (sample.isMember("cross-section")) {
            dataset.cross_section = sample["cross-section"].asDouble();
        } else {
            dataset.cross_section = 1.;
        }

        if (sample.isMember("event-weight-sum")) {
            dataset.event_weight_sum = sample["event-weight-sum"].asDouble();
        } else {
            dataset.event_weight_sum = 1.;
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

        // Register CTRL+C signal handler
        struct sigaction sigIntHandler;

        sigIntHandler.sa_handler = [](int signal) { MUST_STOP = true; };
        sigemptyset(&sigIntHandler.sa_mask);
        sigIntHandler.sa_flags = 0;

        sigaction(SIGINT, &sigIntHandler, NULL);

        for (const Dataset& d: datasets) {
            if (MUST_STOP)
                break;

            std::cout << "Creating plots for dataset '" << d.name << "'" << std::endl;
            std::unique_ptr<TChain> t(new TChain(d.tree_name.c_str()));
            bool fail_if_open_error = d.path.length() == 0;
            size_t n_files = 0;
            for (const std::string& file: d.files)
                n_files += t->Add(file.c_str(), 0);

            if ((fail_if_open_error) && (n_files != d.files.size())) {
                std::cerr << "Error: some files failed to open" << std::endl;
                return 2;
            }

            std::string output_file = output_dir + "/" + d.output_name + ".root";

            // Set cache size to 10 MB
            t->SetCacheSize(10 * 1024 * 1024);
            // Learn tree structure from the first 10 entries
            t->SetCacheLearnEntries(10);

            Plotter p(d, t.get());
            p.plot(output_file);
            std::cout << "Done. Output saved as '" << output_file << "'" << std::endl;
        }

    } catch (TCLAP::ArgException &e) {
        std::cerr << "error: " << e.error() << " for arg " << e.argId() << std::endl;
        return 1;
    }

    return 0;
}

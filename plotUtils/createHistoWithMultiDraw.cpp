// Read some trees, output an histos
// A. Mertens (September 2015)

#include <json/json.h>

#include <iostream>
#include <fstream>
#include <memory>

#include <TVirtualTreePlayer.h>
#include <TMultiDrawTreePlayer.h>
#include <TChain.h>
#include <TTree.h>
#include <TFile.h>
#include <TDirectory.h>

#include <tclap/CmdLine.h>

struct Plot {
    std::string name;
    std::string variable;
    std::string plot_cut;
    std::string binning;
};

bool execute(const std::string& datasets_json, const std::vector<std::string>& plots_json) {
    // Setting the TVirtualTreePlayer
    TVirtualTreePlayer::SetPlayer("TMultiDrawTreePlayer");

    // Getting the list of samples    
    Json::Value samplesroot;
    {
        std::ifstream config_doc(datasets_json);

        Json::Reader samplesreader;
        bool parsingSuccessful = samplesreader.parse(config_doc, samplesroot, false);
        if (!parsingSuccessful) {
            std::cerr << "Failed to parse '" << datasets_json << "'" << std::endl;
            return false;
        }
    }

    // Get the list of plots to draw
    std::vector<Plot> plots;
    for (const auto& plot_json_file: plots_json) {
        std::ifstream f(plot_json_file);

        Json::Value root;
        Json::Reader reader;
        if (! reader.parse(f, root)) {
            std::cerr << "Failed to parse '" << plot_json_file << "'." << std::endl;
            return false;
        }

        for (auto it = root.begin(); it != root.end(); it++) {
            Plot p = {it.name(), (*it)["variable"].asString(), (*it)["plot_cut"].asString(), (*it)["binning"].asString()};
            plots.push_back(p);
        }
    }

    std::cout << "List of requested plots: ";
    for (size_t i = 0; i < plots.size(); i++) {
        std::cout << "'" << plots[i].name << "'";
        if (i != plots.size() - 1)
            std::cout << ", ";
    }

    std::cout << std::endl << std::endl;

    // Looping over the different samples
    Json::Value::Members samples_str = samplesroot.getMemberNames();
    for (unsigned int index = 0; index < samplesroot.size(); index++){    

        const Json::Value samplearray = samplesroot[samples_str.at(index)];

        std::string tree_name = samplearray.get("tree_name","ASCII").asString();
        std::string path = samplearray.get("path","ASCII").asString();
        std::string db_name = samplearray.get("db_name","ASCII").asString();
        std::string sample_cut = samplearray.get("sample_cut","ASCII").asString();

        std::cout << "Running on sample '" << samples_str.at(index) << "'" << std::endl;

        std::unique_ptr<TChain> t(new TChain(tree_name.c_str()));

        std::string infiles = path+"/*.root";

        t->Add(infiles.c_str());

        std::unique_ptr<TFile> outfile(TFile::Open((db_name+"_histos.root").c_str(), "recreate"));

        TMultiDrawTreePlayer* player = dynamic_cast<TMultiDrawTreePlayer*>(t->GetPlayer());

        // Looping over the different plots
        for (auto& p: plots) {
            std::string plot_var = p.variable + ">>" + p.name + p.binning;
            player->queueDraw(plot_var.c_str(), p.plot_cut.c_str());
        }

        player->execute();

        for (auto& p: plots) {
            gDirectory->Get(p.name.c_str())->Write();
        }

        outfile->Write();
    }

    return true;
}


int main( int argc, char* argv[]) {

    try {

        TCLAP::CmdLine cmd("Create histograms from trees", ' ', "0.1.0");

        TCLAP::ValueArg<std::string> datasetArg("d", "dataset", "Input datasets", true, "", "JSON file", cmd);
        TCLAP::UnlabeledMultiArg<std::string> plotsArg("plots", "List of plots", true, "JSON file", cmd);

        cmd.parse(argc, argv);

        return (execute(datasetArg.getValue(), plotsArg.getValue()) ? 0 : 1);

    } catch (TCLAP::ArgException &e) {
        std::cerr << "error: " << e.error() << " for arg " << e.argId() << std::endl;
        return 1;
    }

    return 0;
}


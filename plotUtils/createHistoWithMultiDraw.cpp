// Read some trees, output an histos
// A. Mertens (September 2015)

#include <json/json.h>

#include <iostream>
#include <fstream>


#include <TVirtualTreePlayer.h>
#include <TMultiDrawTreePlayer.h>
#include <TChain.h>
#include <TTree.h>
#include <TFile.h>
#include <TDirectory.h>

#include <tclap/CmdLine.h>

bool execute(const std::string& datasets_json, const std::string& plots_json) {
    // Setting the TVirtualTreePlayer
    TVirtualTreePlayer::SetPlayer("TMultiDrawTreePlayer");

    // Getting the list of samples    
    Json::Value samplesroot;
    std::ifstream config_doc(datasets_json, std::ifstream::binary);

    Json::Reader samplesreader;
    bool parsingSuccessful = samplesreader.parse(config_doc, samplesroot, false);
    if (!parsingSuccessful) { return false;}
    // Let's extract the array contained in the root object
    Json::Value::Members samples_str = samplesroot.getMemberNames();

    // Looping over the different samples
    for (unsigned int index = 0; index < samplesroot.size(); index++){    

        const Json::Value samplearray = samplesroot[samples_str.at(index)];

        std::string tree_name = samplearray.get("tree_name","ASCII").asString();
        std::string path = samplearray.get("path","ASCII").asString();
        std::string db_name = samplearray.get("db_name","ASCII").asString();
        std::string sample_cut = samplearray.get("sample_cut","ASCII").asString();

        std::cout << "running on sample : " << samples_str.at(index) << std::endl;

        TChain* t = new TChain(tree_name.c_str());

        std::string infiles = path+"/*.root";

        t->Add(infiles.c_str());

        TFile* outfile = new TFile((db_name+"_histos.root").c_str(),"recreate");

        TMultiDrawTreePlayer* p = dynamic_cast<TMultiDrawTreePlayer*>(t->GetPlayer());

        // extracting the plots to draw
        Json::Value plotsroot;
        std::ifstream config_doc(plots_json, std::ifstream::binary);
        Json::Reader plotsreader;
        bool parsingSuccessful = plotsreader.parse(config_doc, plotsroot, false);
        if (!parsingSuccessful) { return false;}
        // Let's extract the array contained in the root object
        Json::Value::Members plots_str = plotsroot.getMemberNames();

        // Looping over the different plots
        std::cout << "    plotting : ";

        for (unsigned int index_plot = 0; index_plot < plotsroot.size(); index_plot++){

             const Json::Value array = plotsroot[plots_str.at(index_plot)];
             std::string variable = array.get("variable","ASCII").asString();
             std::string plotCuts = array.get("plot_cut","ASCII").asString();
             std::string binning = array.get("binning","ASCII").asString();

             std::cout << plots_str.at(index_plot) << " , " ;
             std::string plot_var = variable+">>"+plots_str.at(index_plot)+binning;
             p->queueDraw(plot_var.c_str(), plotCuts.c_str());

        }
        std::cout << std::endl;

        p->execute();
        for (unsigned int index_plot = 0; index_plot < plotsroot.size(); index_plot++){
            gDirectory->Get(plots_str.at(index_plot).c_str())->Write();
        }

        outfile->Write();
        delete outfile;
    }

    return true;
}


int main( int argc, char* argv[]) {

    try {

        TCLAP::CmdLine cmd("Create histograms from trees", ' ', "0.1.0");

        TCLAP::ValueArg<std::string> datasetArg("d", "dataset", "Input datasets", true, "", "JSON file", cmd);
        TCLAP::UnlabeledValueArg<std::string> plotsArg("plots", "List of plots", true, "", "JSON file", cmd);

        cmd.parse(argc, argv);

        return (execute(datasetArg.getValue(), plotsArg.getValue()) ? 0 : 1);

    } catch (TCLAP::ArgException &e) {
        std::cerr << "error: " << e.error() << " for arg " << e.argId() << std::endl;
        return 1;
    }

    return 0;
}


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
#include <TParameter.h>
#include <TSystemDirectory.h>

int main( int argc, char* argv[]){

    if (argc != 2) {
        std::cerr << "use as ./countProcessedEvents files.json\n";
        return 0;
    }


    const char* sample_json = argv[1];
    
    std::cout << "Using json file: " << sample_json << std::endl;

    Json::Value samplesroot;;
    std::ifstream config_doc(sample_json, std::ifstream::binary);
    Json::Reader samplesreader;
    bool parsingSuccessful = samplesreader.parse(config_doc, samplesroot, false);
    if (!parsingSuccessful) { std::cout << "Parsing of the json file failed" << std::endl; return 0;}
    // Let's extract the array contained in the root object
    Json::Value::Members samples_str = samplesroot.getMemberNames();


    // Declaring 
    Double_t sumW = 0;

    // Looping over the different samples
    for (unsigned int index = 0; index < samplesroot.size(); index++){    

        const Json::Value samplearray = samplesroot[samples_str.at(index)];

        std::string tree_name = samplearray.get("tree_name","ASCII").asString();
        std::string path = samplearray.get("path","ASCII").asString();
        std::string db_name = samplearray.get("db_name","ASCII").asString();
        std::string sample_cut = samplearray.get("sample_cut","ASCII").asString();

        std::cout << "running on sample : " << samples_str.at(index) << std::endl;

        sumW = 0;        
 
        TSystemDirectory dir(path.c_str(), path.c_str());
        TList *files = dir.GetListOfFiles();

        if (files) {
            TSystemFile *file;
            TString fname;
            TIter next(files);
            while ((file=(TSystemFile*)next())) {
                fname = file->GetName();
                if (!file->IsDirectory() && fname.EndsWith(".root")) {
                    //std::cout << fname.Data() << std::endl;
                    TString infile_path = path+fname.Data();
                    //std::cout << infile_path << std::endl;
                    TFile infile(infile_path,"r");
                    TParameter<float>* par = (TParameter<float>*) infile.Get("event_weight_sum");
                    //std::cout << par << std::endl;
                    sumW += par->GetVal();
                    //std::cout << sumW << std::endl;
                }
            }
        }
        std::cout << " N_weight_sum : " << sumW << std::endl;
    }
}


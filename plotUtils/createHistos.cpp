// Read some trees, output an histos
// A. Mertens (September 2015)

#include <json/json.h>

#include <iostream>
#include <fstream>





void readPlotJson(const char* plots_json, std::string& variable, std::string& plotCuts, std::string& binning){
    Json::Value root;   // will contains the root value after parsing.
    std::ifstream config_doc(plots_json, std::ifstream::binary);
    // config_doc >> root;



    Json::Reader reader;
    bool parsingSuccessful = reader.parse(config_doc, root, false);
    if (parsingSuccessful)
    {
        // Let's extract the array contained in the root object
        const Json::Value array = root["missing_Et"];

        std::cout << "size : " << array.size() << std::endl;

        // Iterate over sequence elements and print its values

        variable = array.get("variable","ASCII").asString();
        //variable = variable_str.c_str();

        plotCuts = array.get("plot_cut","ASCII").asString();
        //plotCuts  = (char*) plotCuts_str.c_str();

        binning = array.get("binning","ASCII").asString();
        //binning   = (char*) binning_str.c_str();

        std::cout << variable << std::endl;
        std::cout << plotCuts << std::endl;
        std::cout << binning  << std::endl;

    }
return;
}


void readSampleJson(const char* sample_json, std::string& tree_name, std::string& path, std::string& db_name, std::string& sample_cut){
    Json::Value root;   // will contains the root value after parsing.
    std::ifstream config_doc(sample_json, std::ifstream::binary);

    Json::Reader reader;
    bool parsingSuccessful = reader.parse(config_doc, root, false);

    std::cout << "root size " << root.size() << std::endl;

    if (parsingSuccessful)
    {
        // Let's extract the array contained in the root object
        const Json::Value array = root["DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX_Asympt25ns_15c5fa1_c106444"];

        std::cout << "size : " << array.size() << std::endl;

        // Iterate over sequence elements and print its values

        tree_name = array.get("tree_name","ASCII").asString();
        path = array.get("path","ASCII").asString();
        db_name = array.get("db_name","ASCII").asString();
        sample_cut = array.get("sample_cut","ASCII").asString();

    }
return;
}



int main( int argc, char* argv[]){

    if (argc != 3) {
        //std::cerr << "use as ./createHisto files.json plots.json\n";
        return 0;
    }

    std::cout << argc <<  argv[0] << argv[1] << argv[2] << std::endl;

    const char* plots_json = argv[1];
    const char* sample_json = argv[2];

    std::string variable ; 
    std::string plotCuts ;
    std::string binning ;

    std::string tree_name ;
    std::string path;
    std::string db_name;
    std::string sample_cut;


    readPlotJson(plots_json, variable, plotCuts, binning);

    readSampleJson(sample_json, tree_name, path, db_name, sample_cut);




    std::cout <<"variable : " <<  variable << std::endl;
    std::cout <<"plotCuts : " <<  plotCuts << std::endl;
    std::cout <<"binning : " << binning  << std::endl;
    std::cout <<"tree_name : "<<  tree_name << std::endl;
    std::cout <<"path : " << path << std::endl;
    std::cout <<"db_name : " << db_name  << std::endl;
    std::cout <<"sample_cut : " <<  sample_cut  << std::endl;

/*
    // looping over the files with the trees to read.
    for (files ...){
        // creation of the histos
        for (plots){
        
        }

        // Filling of the histos
        for (entry ...){
      
        }

    }
*/
}

/*
    for ksample in samples:
        print 'Treating sample', ksample
        name = str(ksample)
        dbname = samples[ksample]["db_name"]
        dirpath = samples[ksample]["path"]
        file = "output*root"
        tree = str(samples[ksample]["tree_name"])
        sample_cut = str(samples[ksample]["sample_cut"])
        outfile = ROOT.TFile(dbname + "_histos.root", "recreate")
        for kplot in plots:
            print "\tNow taking care of plot", kplot
            name2 = str(kplot)
            variable = str(plots[kplot]["variable"])
            plot_cut = str(plots[kplot]["plot_cut"])
            binning = str(plots[kplot]["binning"])
            xnbin, xlow, xhigh = map(float, binning.strip().strip("()").split(","))
            chain = TChain(tree)
            chain.Add( os.path.join(dirpath, "output*root") )
            total_cut = plot_cut
            if sample_cut == "": sample_cut = "1"
            total_cut = "(" + plot_cut + ") * event_weight * (" + sample_cut + ")"
            chain.Draw(variable + ">>h_tmp" + binning, total_cut)
            h = ROOT.gDirectory.Get("h_tmp")
            h.Sumw2()
            h.SetName(name2)
            h.Write()
        outfile.Write()
        outfile.Close()

}

if __name__ == '__main__':
    options = get_options()
    print "##### Read samples to be processed"
    samples = {}
    for sample in options.samples:
        print "opening sample file", sample
        with open(sample) as f:
            samples.update(json.load(f))
    print "##### Read plots to be processed"
    plots = {}
    for plot in options.plots:
        with open(plot) as f:
            plots.update(json.load(f))
    print "##### Now creating the histos"
    main(samples, plots)

*/

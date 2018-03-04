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
#include <TError.h>

{{INCLUDES}}

volatile bool MUST_STOP = false;

void Plotter::plot(const std::string& output_file) {

{{BEFORE_LOOP}}

    size_t index = 1;
    while (tree.next()) {

        if (MUST_STOP) {
            break;
        }

        if (m_sample_cut){
          if( !m_sample_cut->EvalInstance() )
            continue;
        }

        const std::string filename = raw_tree->GetFile()->GetName();
        const bool runOnElEl = filename.find("DoubleEG") != std::string::npos;
        const bool runOnMuMu = filename.find("DoubleMuon") != std::string::npos;
        const bool runOnMuEl = filename.find("MuonEG") != std::string::npos;
        const bool runOnElMu = runOnMuEl;
        const bool runOnMC = !(runOnElEl || runOnMuMu || runOnMuEl);

        if ((index - 1) % 1000 == 0)
            std::cout << "Processing entry " << index << " of " << tree.getEntries() << std::endl;

        bool __cut = false;
        double __weight = 0;

{{IN_LOOP}}

        index++;
    }

    std::unique_ptr<TFile> outfile(TFile::Open(output_file.c_str(), "recreate"));

{{AFTER_LOOP}}
}

int main(int argc, char** argv) {

    gErrorIgnoreLevel = kWarning + 1;

    // very basic command-line argument parsing
    // 1: name of the output file
    // 2: name of the input tree
    // 3: selection cut for the TChain
    // 4-...: names of input files
    if ( argc < 5 ) { // FIXME check if the first one is special indeed
        std::cout << "Not enough arguments to do anything meaningful -> exiting" << std::endl;
        std::cout << "Command line arguments should be : outFileName, inTreeName, sampleCut, inFile1 [inFile2...]" << std::endl;
    } else {
        std::string output_file{argv[1]};// FIXME
        TChain t{argv[2]}; // FIXME
        std::string cut{argv[3]};
        std::size_t n_files{0};
        for ( std::size_t idx{4}; argc != idx; ++idx ) { // FIXME
            n_files += t.Add(argv[idx], 0);
        }
        if ( n_files != (argc-4) ) { // FIXME
            std::cerr << "Error: some files failed to open" << std::endl;
            return 2;
        }

        // Register CTRL+C signal handler
        struct sigaction sigIntHandler;
        sigIntHandler.sa_handler = [](int signal) { MUST_STOP = true; };
        sigemptyset(&sigIntHandler.sa_mask);
        sigIntHandler.sa_flags = 0;
        sigaction(SIGINT, &sigIntHandler, NULL);

        // Set cache size to 10 MB
        t.SetCacheSize(10 * 1024 * 1024);
        // Learn tree structure from the first 10 entries
        t.SetCacheLearnEntries(10);

        TH1::SetDefaultSumw2(kTRUE);

        Plotter p(cut, &t);
        p.plot(output_file);
        std::cout << "Done. Output saved as '" << output_file << "'" << std::endl;
    }
    return 0;
}

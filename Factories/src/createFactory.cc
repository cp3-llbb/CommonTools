#include <HistFactory.h>
#include <TreeFactory.h>

#include <TApplication.h>
#include <TROOT.h>

#include <tclap/CmdLine.h>

int main( int argc, char* argv[]) {

    try {

        TCLAP::CmdLine cmd("Create histograms or trees from trees", ' ', "1.0.0");

        TCLAP::ValueArg<std::string> skeletonArg("i", "input", "Input file containing a skeleton tree", true, "", "ROOT file", cmd);
        TCLAP::ValueArg<std::string> outputArg("o", "output", "Output directory", false, "", "FOLDER", cmd);
        TCLAP::UnlabeledValueArg<std::string> configArg("config", "A python script which will be executed and should returns a list of plots", true, "", "Python script", cmd);

        cmd.parse(argc, argv);

        /*
         * When PyROOT is loaded, it creates its own ROOT application ([1] and [2]). We do not want this to happen,
         * because it messes with our already loaded ROOT.
         *
         * To prevent this, we create here our own application (which does nothing), just to prevent `CreatePyROOTApplication`
         * to do anything.
         *
         * [1] https://github.com/root-mirror/root/blob/0a62e34aa86b812651cfcf9526ba03b975adaa5c/bindings/pyroot/ROOT.py#L476
         * [2] https://github.com/root-mirror/root/blob/0a62e34aa86b812651cfcf9526ba03b975adaa5c/bindings/pyroot/src/TPyROOTApplication.cxx#L117
         */

        gROOT->SetBatch(true);
        std::unique_ptr<TApplication> app(new TApplication("dummy", 0, NULL));

        std::string executable = argv[0];
        std::unique_ptr<Factory> factory;
        if (executable.find("histFactory") != std::string::npos) {
            factory.reset(new HistFactory(skeletonArg.getValue(), configArg.getValue(), outputArg.getValue()));
        } else if (executable.find("treeFactory") != std::string::npos) {
            factory.reset(new TreeFactory(skeletonArg.getValue(), configArg.getValue(), outputArg.getValue()));
        } else {
            throw std::runtime_error("Unsupported executable name");
        }

        bool ret = factory->run();

        return (ret ? 0 : 1);

    } catch (TCLAP::ArgException &e) {
        std::cerr << "error: " << e.error() << " for arg " << e.argId() << std::endl;
        return 1;
    }

    return 0;
}

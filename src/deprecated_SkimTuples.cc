#include "../lib/SkimTuples.h"
#include <TStopwatch.h>

int main(int argc, char *argv[]) {

    if (argc != 6) {
        std::cerr << "Please give 5 arguments: input file, output file, era, "
                     "channel, is_data(T/F)"
                  << std::endl;
        return -1;
    }

    TString input(argv[1]);
    TString output(argv[2]);
    TString era(argv[3]);
    TString channel(argv[4]);
    const bool is_data = *argv[5] == 'T';

    std::cout << "Input: " << input << std::endl;
    std::cout << "Output: " << output << std::endl;
    std::cout << "Era: " << era << std::endl;
    std::cout << "Channel: " << channel << std::endl;
    std::cout << std::boolalpha;
    std::cout << "Is data? " << is_data << std::endl;

    // TStopwatch timer = TStopwatch();
    // timer.Start();
    TStopwatch timer;
    timer.Start();

    SkimTuples skin_tuples = SkimTuples(input, output, era, channel, is_data);

    skin_tuples.setBranchesAddresses();
    skin_tuples.fillTree();
    skin_tuples.saveFile();
    timer.Print();
    // return 0;
}

#include "../lib/CreateTuple.h"
#include <TStopwatch.h>

int main(int argc, char *argv[]) {

    if (argc != 8) {
        std::cerr << "Please give 5 arguments: input file, weight file, output file, era, "
                     "channel, is_data(T/F), is_signal(T/F)"
                  << std::endl;
        return -1;
    }

    TString input(argv[1]);
    TString weightFile(argv[2]);
    TString output(argv[3]);
    TString era(argv[4]);
    TString channel(argv[5]);
    const bool is_data = *argv[6] == 'T';
    const bool is_signal = *argv[7] == 'T';

    std::cout << "Input: " << input << std::endl;
    std::cout << "Weight: " << weightFile << std::endl;
    std::cout << "Output: " << output << std::endl;
    std::cout << "Era: " << era << std::endl;
    std::cout << "Channel: " << channel << std::endl;
    std::cout << std::boolalpha;
    std::cout << "Is data? " << is_data << std::endl;
    std::cout << "Is signal? " << is_signal << std::endl;

    // TStopwatch timer = TStopwatch();
    // timer.Start();
    TStopwatch timer;
    timer.Start();

    CreateTuple create_tuple =
        CreateTuple(input, weightFile, output, era, channel, is_data, is_signal);

    create_tuple.setBranchesAddressesInput();
    create_tuple.setBranchesAddressesOutput();
    create_tuple.fillOutputTree();
    create_tuple.saveTree();
    timer.Print();
    return 0;
}

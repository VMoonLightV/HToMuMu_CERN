//////////////////////////////////////////////////////////
//
// Original Author : Irene Dutta
//                   Caltech
// Date Created    : Mon 27 Aug, 2018
//////////////////////////////////////////////////////////
#define MainEvent_cxx

#include "../lib/MainEvent.h"
#include <TH2.h>
#include <TStyle.h>
//#include <iostream>

double MainEvent::DeltaPhi(double phi1, double phi2) {
    double result = phi1 - phi2;
    while (result > M_PI)
        result -= 2 * M_PI;
    while (result <= -M_PI)
        result += 2 * M_PI;
    return result;
}

double MainEvent::DeltaR(double eta1, double phi1, double eta2, double phi2) {
    double deta = eta1 - eta2;
    double dphi = DeltaPhi(phi1, phi2);
    return std::sqrt(deta * deta + dphi * dphi);
}
// -------------------- modify following functions according to code
// -------------------
//int MainEvent::FindMom(
    //double dau, double mom,
    //int i) { // this logic works here because we haven't saved a particle for
             //// which id=dau id. So no need for recursion.In general there has
             //// to be a recursive function.
//}

double MainEvent::HT(std::vector<TLorentzVector> vjets) {
    double ht = 0.0;
    for (unsigned int ijet = 0; ijet < vjets.size(); ijet++) {
        // if( vjets[ijet].Pt()>50.0 && std::abs(vjets[ijet].Eta())<2.5 )
        ht += vjets[ijet].Pt();
    }
    return ht;
}
TLorentzVector MainEvent::MHT(std::vector<TLorentzVector> vjets) {
    ;
    TLorentzVector mht(0.0, 0.0, 0.0, 0.0);
    for (unsigned int ijet = 0; ijet < vjets.size(); ijet++) {
        if (vjets[ijet].Pt() > 30.0 && std::abs(vjets[ijet].Eta()) < 5.0)
            mht -= vjets[ijet];
    }

    return mht;
}

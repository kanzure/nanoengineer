// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "Nanorex/Utility/NXUtility.h"

namespace Nanorex {

/***************** NXUtility *****************/

/* FUNCTION: itos */
/**
 * Returns a std::string for the given int.
 */
std::string NXUtility::itos(int i) {
	char buffer[20];
	sprintf(buffer, "%d", i);
	std::string s = buffer;

	return s;
}
/**
 * Returns a std::string for the given unsigned int.
 */
std::string NXUtility::itos(unsigned int i) {
	char buffer[20];
	sprintf(buffer, "%u", i);
	std::string s = buffer;

	return s;
}
/**
 * Returns a std::string for the given unsigned long.
 */
std::string NXUtility::itos(unsigned long i) {
	char buffer[40];
	sprintf(buffer, "%u", i);
	std::string s = buffer;

	return s;
}


/* FUNCTION: PaddedString */
/**
 * Returns the string representation of the given integer padded out to the
 * specified length.
 */
std::string NXUtility::PaddedString(int i, int length) {
	int iLength;
	std::string bufferStr = "";
	if (i > 0)
		iLength = (int)(log10((float) i)) + 1;
	else if (i == 0)
		iLength = 1;
	else {
		bufferStr = "-";
		i = -i;
		iLength = (int)(log10((float) i)) + 1;
	}
	int padZeros = length - iLength;
	for (int index = 0; index < padZeros; index++)
		bufferStr += "0";
	bufferStr += itos(i);
	return bufferStr;
}


AtomicDataMap* NXUtility::atomicDataMap = new AtomicDataMap();

/* FUNCTION: AtomicNumber */
/**
 * Returns the atomic number for the atom type specified by the given symbol.
 */
int NXUtility::AtomicNumber(const std::string& symbol) {
	return atomicDataMap->getNumber(symbol);
}


/* FUNCTION: AtomicWeight */
/**
 * Returns the atomic weight for the atom type specified by the given symbol.
 */
double NXUtility::AtomicWeight(const std::string& symbol) {
	return atomicDataMap->getWeight(symbol);
}


/* FUNCTION: ElementSymbol */
/**
 * Copies the symbol for the given atomic number into the given char pointer.
 */
void NXUtility::ElementSymbol(int atomicNumber, char* symbol) {
	atomicDataMap->getSymbol(atomicNumber, symbol);
}


/* FUNCTION: GetNSPR_MeaningForCode */
/**
 * Returns a human-readable string for the given NSPR code.
 */
std::string NXUtility::GetNSPR_MeaningForCode(PRErrorCode errorCode) {
	std::string meaning;
	if ((errorCode < (-6000L)) || (errorCode > (-5926L)))
		meaning =
			std::string("Unknown error code (").append(itos(errorCode))
			.append(")");

	else
		meaning = std::string(NSPRcodeToMeaning[errorCode + 6000]);
	return meaning;
}


/***************** AtomicDataMap *****************/

/* CONSTRUCTOR */
AtomicDataMap::AtomicDataMap() {
	symbolVector.push_back(""); // To start indexing at 1
	atomicData["H"].number = 1;		atomicData["H"].weight = 1.007825037;
	symbolVector.push_back("H");
	atomicData["He"].number = 2;	atomicData["He"].weight = 4.002603250;
	symbolVector.push_back("He");
	atomicData["Li"].number = 3;	atomicData["Li"].weight = 7.016004500;
	symbolVector.push_back("Li");
	atomicData["Be"].number = 4;	atomicData["Be"].weight = 9.012182500;
	symbolVector.push_back("Be");
	atomicData["B"].number = 5;		atomicData["B"].weight = 11.009305300;
	symbolVector.push_back("B");
	atomicData["C"].number = 6;		atomicData["C"].weight = 12.0107;
	symbolVector.push_back("C");
	atomicData["N"].number = 7;		atomicData["N"].weight = 14.003074008;
	symbolVector.push_back("N");
	atomicData["O"].number = 8;		atomicData["O"].weight = 15.994914640;
	symbolVector.push_back("O");
	atomicData["F"].number = 9;		atomicData["F"].weight = 18.998403250;
	symbolVector.push_back("F");
	atomicData["Ne"].number = 10;	atomicData["Ne"].weight = 19.992439100;
	symbolVector.push_back("Ne");
	atomicData["Na"].number = 11;	atomicData["Na"].weight = 22.989769700;
	symbolVector.push_back("Na");
	atomicData["Mg"].number = 12;	atomicData["Mg"].weight = 23.985045000;
	symbolVector.push_back("Mg");
	atomicData["Al"].number = 13;	atomicData["Al"].weight = 26.981541300;
	symbolVector.push_back("Al");
	atomicData["Si"].number = 14;	atomicData["Si"].weight = 27.976928400;
	symbolVector.push_back("Si");
	atomicData["P"].number = 15;	atomicData["P"].weight = 30.973763400;
	symbolVector.push_back("P");
	atomicData["S"].number = 16;	atomicData["S"].weight = 31.972071800;
	symbolVector.push_back("S");
	atomicData["Cl"].number = 17;	atomicData["Cl"].weight = 34.968852729;
	symbolVector.push_back("Cl");
	atomicData["Ar"].number = 18;	atomicData["Ar"].weight = 39.962383100;
	symbolVector.push_back("Ar");
	atomicData["K"].number = 19;	atomicData["K"].weight = 38.963707900;
	symbolVector.push_back("K");
	atomicData["Ca"].number = 20;	atomicData["Ca"].weight = 39.962590700;
	symbolVector.push_back("Ca");
	atomicData["Sc"].number = 21;	atomicData["Sc"].weight = 44.955913600;
	symbolVector.push_back("Sc");
	atomicData["Ti"].number = 22;	atomicData["Ti"].weight = 47.947946700;
	symbolVector.push_back("Ti");
	atomicData["V"].number = 23;	atomicData["V"].weight = 50.943962500;
	symbolVector.push_back("V");
	atomicData["Cr"].number = 24;	atomicData["Cr"].weight = 51.940509700;
	symbolVector.push_back("Cr");
	atomicData["Mn"].number = 25;	atomicData["Mn"].weight = 54.938046300;
	symbolVector.push_back("Mn");
	atomicData["Fe"].number = 26;	atomicData["Fe"].weight = 55.934939300;
	symbolVector.push_back("Fe");
	atomicData["Co"].number = 27;	atomicData["Co"].weight = 58.933197800;
	symbolVector.push_back("Co");
	atomicData["Ni"].number = 28;	atomicData["Ni"].weight = 57.935347100;
	symbolVector.push_back("Ni");
	atomicData["Cu"].number = 29;	atomicData["Cu"].weight = 62.929599200;
	symbolVector.push_back("Cu");
	atomicData["Zn"].number = 30;	atomicData["Zn"].weight = 63.929145400;
	symbolVector.push_back("Zn");
	atomicData["Ga"].number = 31;	atomicData["Ga"].weight = 68.925580900;
	symbolVector.push_back("Ga");
	atomicData["Ge"].number = 32;	atomicData["Ge"].weight = 73.921178800;
	symbolVector.push_back("Ge");
	atomicData["As"].number = 33;	atomicData["As"].weight = 74.921595500;
	symbolVector.push_back("As");
	atomicData["Se"].number = 34;	atomicData["Se"].weight = 79.916520500;
	symbolVector.push_back("Se");
	atomicData["Br"].number = 35;	atomicData["Br"].weight = 78.918336100;
	symbolVector.push_back("Br");
	atomicData["Kr"].number = 36;	atomicData["Kr"].weight = 83.911506400;
	symbolVector.push_back("Kr");
	atomicData["Rb"].number = 37;	atomicData["Rb"].weight = 85.4678;
	symbolVector.push_back("Rb");
	atomicData["Sr"].number = 38;	atomicData["Sr"].weight = 87.6200;
	symbolVector.push_back("Sr");
	atomicData["Y"].number = 39;	atomicData["Y"].weight = 88.9059;
	symbolVector.push_back("Y");
	atomicData["Zr"].number = 40;	atomicData["Zr"].weight = 91.2200;
	symbolVector.push_back("Zr");
	atomicData["Nb"].number = 41;	atomicData["Nb"].weight = 92.9064;
	symbolVector.push_back("Nb");
	atomicData["Mo"].number = 42;	atomicData["Mo"].weight = 95.9400;
	symbolVector.push_back("Mo");
	atomicData["Tc"].number = 43;	atomicData["Tc"].weight = 98.0000;
	symbolVector.push_back("Tc");
	atomicData["Ru"].number = 44;	atomicData["Ru"].weight = 101.0700;
	symbolVector.push_back("Ru");
	atomicData["Rh"].number = 45;	atomicData["Rh"].weight = 102.9055;
	symbolVector.push_back("Rh");
	atomicData["Pd"].number = 46;	atomicData["Pd"].weight = 106.4000;
	symbolVector.push_back("Pd");
	atomicData["Ag"].number = 47;	atomicData["Ag"].weight = 107.8680;
	symbolVector.push_back("Ag");
	atomicData["Cd"].number = 48;	atomicData["Cd"].weight = 112.4100;
	symbolVector.push_back("Cd");
	atomicData["In"].number = 49;	atomicData["In"].weight = 114.8200;
	symbolVector.push_back("In");
	atomicData["Sn"].number = 50;	atomicData["Sn"].weight = 118.6900;
	symbolVector.push_back("Sn");
	atomicData["Sb"].number = 51;	atomicData["Sb"].weight = 121.7500;
	symbolVector.push_back("Sb");
	atomicData["Te"].number = 52;	atomicData["Te"].weight = 127.6000;
	symbolVector.push_back("Te");
	atomicData["I"].number = 53;	atomicData["I"].weight = 126.9045;
	symbolVector.push_back("I");
	atomicData["Xe"].number = 54;	atomicData["Xe"].weight = 131.3000;
	symbolVector.push_back("Xe");
	atomicData["Cs"].number = 55;	atomicData["Cs"].weight = 132.9054;
	symbolVector.push_back("Cs");
	atomicData["Ba"].number = 56;	atomicData["Ba"].weight = 137.3300;
	symbolVector.push_back("Ba");
	atomicData["La"].number = 57;	atomicData["La"].weight = 138.9055;
	symbolVector.push_back("La");
	atomicData["Ce"].number = 58;	atomicData["Ce"].weight = 140.1200;
	symbolVector.push_back("Ce");
	atomicData["Pr"].number = 59;	atomicData["Pr"].weight = 140.9077;
	symbolVector.push_back("Pr");
	atomicData["Nd"].number = 60;	atomicData["Nd"].weight = 144.2400;
	symbolVector.push_back("Nd");
	atomicData["Pm"].number = 61;	atomicData["Pm"].weight = 145.0000;
	symbolVector.push_back("Pm");
	atomicData["Sm"].number = 62;	atomicData["Sm"].weight = 150.4000;
	symbolVector.push_back("Sm");
	atomicData["Eu"].number = 63;	atomicData["Eu"].weight = 151.9600;
	symbolVector.push_back("Eu");
	atomicData["Gd"].number = 64;	atomicData["Gd"].weight = 157.2500;
	symbolVector.push_back("Gd");
	atomicData["Tb"].number = 65;	atomicData["Tb"].weight = 158.9254;
	symbolVector.push_back("Tb");
	atomicData["Dy"].number = 66;	atomicData["Dy"].weight = 162.5000;
	symbolVector.push_back("Dy");
	atomicData["Ho"].number = 67;	atomicData["Ho"].weight = 164.9304;
	symbolVector.push_back("Ho");
	atomicData["Er"].number = 68;	atomicData["Er"].weight = 167.2600;
	symbolVector.push_back("Er");
	atomicData["Tm"].number = 69;	atomicData["Tm"].weight = 168.9342;
	symbolVector.push_back("Tm");
	atomicData["Yb"].number = 70;	atomicData["Yb"].weight = 173.0400;
	symbolVector.push_back("Yb");
	atomicData["Lu"].number = 71;	atomicData["Lu"].weight = 174.9670;
	symbolVector.push_back("Lu");
	atomicData["Hf"].number = 72;	atomicData["Hf"].weight = 178.4900;
	symbolVector.push_back("Hf");
	atomicData["Ta"].number = 73;	atomicData["Ta"].weight = 180.9479;
	symbolVector.push_back("Ta");
	atomicData["W"].number = 74;	atomicData["W"].weight = 183.8500;
	symbolVector.push_back("W");
	atomicData["Re"].number = 75;	atomicData["Re"].weight = 186.2070;
	symbolVector.push_back("Re");
	atomicData["Os"].number = 76;	atomicData["Os"].weight = 190.2000;
	symbolVector.push_back("Os");
	atomicData["Ir"].number = 77;	atomicData["Ir"].weight = 192.2200;
	symbolVector.push_back("Ir");
	atomicData["Pt"].number = 78;	atomicData["Pt"].weight = 195.0900;
	symbolVector.push_back("Pt");
	atomicData["Au"].number = 79;	atomicData["Au"].weight = 196.9665;
	symbolVector.push_back("Au");
	atomicData["Hg"].number = 80;	atomicData["Hg"].weight = 200.5900;
	symbolVector.push_back("Hg");
	atomicData["Tl"].number = 81;	atomicData["Tl"].weight = 204.3700;
	symbolVector.push_back("Tl");
	atomicData["Pb"].number = 82;	atomicData["Pb"].weight = 207.2000;
	symbolVector.push_back("Pb");
	atomicData["Bi"].number = 83;	atomicData["Bi"].weight = 208.9804;
	symbolVector.push_back("Bi");
	atomicData["Po"].number = 84;	atomicData["Po"].weight = 209.0000;
	symbolVector.push_back("Po");
	atomicData["At"].number = 85;	atomicData["At"].weight = 210.0000;
	symbolVector.push_back("At");
	atomicData["Rn"].number = 86;	atomicData["Rn"].weight = 222.0000;
	symbolVector.push_back("Rn");
	atomicData["Fr"].number = 87;	atomicData["Fr"].weight = 223.0000;
	symbolVector.push_back("Fr");
	atomicData["Ra"].number = 88;	atomicData["Ra"].weight = 226.0254;
	symbolVector.push_back("Ra");
	atomicData["Ac"].number = 89;	atomicData["Ac"].weight = 227.0278;
	symbolVector.push_back("Ac");
	atomicData["Th"].number = 90;	atomicData["Th"].weight = 232.0381;
	symbolVector.push_back("Th");
	atomicData["Pa"].number = 91;	atomicData["Pa"].weight = 231.0359;
	symbolVector.push_back("Pa");
	atomicData["U"].number = 92;	atomicData["U"].weight = 238.0290;
	symbolVector.push_back("U");
	atomicData["Np"].number = 93;	atomicData["Np"].weight = 237.0482;
	symbolVector.push_back("Np");
	atomicData["Pu"].number = 94;	atomicData["Pu"].weight = 244.0000;
	symbolVector.push_back("Pu");
	atomicData["Am"].number = 95;	atomicData["Am"].weight = 243.0000;
	symbolVector.push_back("Am");
	atomicData["Cm"].number = 96;	atomicData["Cm"].weight = 247.0000;
	symbolVector.push_back("Cm");
	atomicData["Bk"].number = 97;	atomicData["Bk"].weight = 247.0000;
	symbolVector.push_back("Bk");
	atomicData["Cf"].number = 98;	atomicData["Cf"].weight = 251.0000;
	symbolVector.push_back("Cf");
	atomicData["Es"].number = 99;	atomicData["Es"].weight = 254.0000;
	symbolVector.push_back("Es");
	atomicData["Fm"].number = 100;	atomicData["Fm"].weight = 257.0000;
	symbolVector.push_back("Fm");
	atomicData["Md"].number = 101;	atomicData["Md"].weight = 258.0000;
	symbolVector.push_back("Md");
	atomicData["No"].number = 102;	atomicData["No"].weight = 259.0000;
	symbolVector.push_back("No");
	atomicData["Lr"].number = 103;	atomicData["Lr"].weight = 260.0000;
	symbolVector.push_back("Lr");
	atomicData["Rf"].number = 104;	atomicData["Rf"].weight = 260.0000;
	symbolVector.push_back("Rf");
	atomicData["Db"].number = 105;	atomicData["Db"].weight = 260.0000;
	symbolVector.push_back("Db");
	atomicData["Sg"].number = 106;	atomicData["Sg"].weight = 260.0000;
	symbolVector.push_back("Sg");
	atomicData["Bh"].number = 107;	atomicData["Bh"].weight = 260.0000;
	symbolVector.push_back("Bh");
	atomicData["Hs"].number = 108;	atomicData["Hs"].weight = 260.0000;
	symbolVector.push_back("Hs");
	atomicData["Mt"].number = 109;	atomicData["Mt"].weight = 260.0000;
	symbolVector.push_back("Mt");
	atomicData["Ds"].number = 110;	atomicData["Ds"].weight = 260.0000;
	symbolVector.push_back("Ds");
}


/* FUNCTION: getNumber */
int AtomicDataMap::getNumber(const std::string& symbol) {
	return atomicData[symbol].number;
}


/* FUNCTION: getWeight */
double AtomicDataMap::getWeight(const std::string& symbol) {
	return atomicData[symbol].weight;
}


/* FUNCTION: getSymbol */
void AtomicDataMap::getSymbol(int atomicNumber, char* symbol) {
	strcpy(symbol, symbolVector[atomicNumber]);
}

} // Nanorex::

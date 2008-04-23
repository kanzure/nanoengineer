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
	sprintf(buffer, "%lu", i);
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

/**
 * Returns a std::string for the given double
 */
std::string NXUtility::dtos(double d) {
	char buffer[20];
	sprintf(buffer, "%lf", d);
	std::string s = buffer;
	
	return s;
}

} // Nanorex::

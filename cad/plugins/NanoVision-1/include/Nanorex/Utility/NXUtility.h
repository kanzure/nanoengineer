// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_UTILITY_H
#define NX_UTILITY_H

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#ifdef WIN32
#	ifdef _MSC_VER
#		pragma warning(disable:4786)
#	endif
#endif

#include <map>
#include <vector>
#include <string>
#include <iostream>
#include <algorithm>

namespace Nanorex {


/* CLASS: AtomicDataMap */
/**
 * Used internally by the NXUtility::AtomicNumber/Weight functions - use those
 * instead.
 */
struct AtomicData {
	int number;
	double weight;
};
/**
 * Used internally by the NXUtility::AtomicNumber/Weight functions - use those
 * instead.
 */
class AtomicDataMap {
	public:
		AtomicDataMap();
		int getNumber(const std::string& symbol);
		double getWeight(const std::string& symbol);
		void getSymbol(int atomicNumber, char* symbol);
	
	private:
		std::map<std::string, AtomicData> atomicData;
		std::vector<char*> symbolVector;
};

	
/* CLASS: NXUtility */
/**
 * Miscellaneous utility functions.
 * @ingroup NanorexUtility
 */
class NXUtility {
	public:
		static std::string itos(int i);
		static std::string itos(unsigned int i);
		static std::string itos(unsigned long i);
		static std::string PaddedString(int i, int length);

		static int AtomicNumber(const std::string& symbol);
		static double AtomicWeight(const std::string& symbol);
		static void ElementSymbol(int atomicNumber, char* symbol);

	private:
		static AtomicDataMap* atomicDataMap;
};


/* CLASS: NXException */
/**
 * A simple exception class.
 * @ingroup NanorexUtility
 */
class NXException {
	public:
		NHException() {};
		NHException(const std::string& message) { this->message = message; }
		const std::string& getMessage() const { return message; }

	private:
		std::string message;
};


} // Nanorex::

#endif

// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_NUMBERS_H
#define NX_NUMBERS_H

#ifdef WIN32
#	ifdef _MSC_VER
#		pragma warning(disable:4786)
#	endif
#endif

#include <vector>
#include <iostream>

#include "math.h"
#include <stdio.h>
#include <stdlib.h>

namespace Nanorex {

typedef signed		char	NXInt8;		// 8-bit signed integer
typedef unsigned	char	NXUint8;	// 8-bit unsigned integer
typedef signed		short	NXInt16;	// 16-bit signed integer
typedef unsigned	short	NXUint16;	// 16-bit unsigned integer
typedef signed		int		NXInt32;	// 32-bit signed integer
typedef unsigned	int		NXUint32;	// 32-bit unsigned integer
typedef signed		long	NXInt64;	// 64-bit signed integer
typedef unsigned	long	NXUint64;	// 64-bit unsigned integer

// 32 bit IEEE float (1 sign, 8 exponent bits, 23 fraction bits)
typedef float NXFloat32;

// 64 bit IEEE float (1 sign, 11 exponent bits, 52 fraction bits)
typedef double NXFloat64;

// For counting NXAtoms, NXBonds, and NXMolecules
//typedef NXUint32 NXABMInt;
typedef std::vector<unsigned int>::size_type NXABMInt;

// For counting MoleculeSets
//typedef NXUint16 NXMSInt;
typedef std::vector<unsigned int>::size_type NXMSInt;

// For measurements and calculations
typedef NXFloat32 NXReal;


/* CLASS: RealUtils */
/**
 * Utilities to manipulate Real numbers.
 * @ingroup ChemistryDataModel, NanorexInterface
 */
class NXRealUtils {
	public:
		typedef enum {
			YOTTA = 24, ZETTA = 21, EXA = 18, PETA = 15, TERA = 12, GIGA = 9,
			MEGA = 6, KILO = 3, HECTO = 2, DECA = 1, NONE = 0, DECI = -1,
			CENTI = -2, MILLI = -3, MICRO = -6, NANO = -9, PICO = -12,
			FEMTO = -15, ATTO = -18, ZEPTO = -21, YOCTO = -24,
			ANGSTROM = -10
		} Scale;

		static NXReal ToReal(const char* realChars);
		static NXReal ToReal(const char* realChars, char* scaleString);
		static void ToChar(const NXReal& number,
						   char* charBuffer,
						   int precision = 5);
		static NXRealUtils::Scale ScaleStringToEnum(const char* scaleString);
};

} // Nanorex::

#endif

// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "Nanorex/Interface/NXNumbers.h"

namespace Nanorex {


/* FUNCTION: ToReal */
/** Returns a NXReal constructed from the given string. */
NXReal NXRealUtils::ToReal(const char* realChars) {
	return atof(realChars);
}
/**
 Returns a real constructed from the given realChars and scaleString.
 The scaleString is one of:
 "Y" (10<sup>24</sup>),
 "Z" (10<sup>21</sup>),
 "E" (10<sup>18</sup>),
 "P" (10<sup>15</sup>),
 "T" (10<sup>12</sup>),
 "G" (10<sup>9</sup>),
 "M" (10<sup>6</sup>),
 "k" (10<sup>3</sup>),
 "h" (10<sup>2</sup>),
 "da" (10<sup>1</sup>),
 "d" (10<sup>-1</sup>),
 "c" (10<sup>-2</sup>),
 "m" (10<sup>-3</sup>),
 "u" (10<sup>-6</sup>),
 "n" (10<sup>-9</sup>),
 "A" (10<sup>-10</sup>),
 "p" (10<sup>-12</sup>),
 "f" (10<sup>-15</sup>),
 "a" (10<sup>-18</sup>),
 "z" (10<sup>-21</sup>), or
 "y" (10<sup>-24</sup>)

 */
NXReal NXRealUtils::ToReal(const char* realChars, char* scaleString) {
	NXReal result = pow(10, ScaleStringToEnum(scaleString));
	result *= atof(realChars);
	return result;
}


/* FUNCTION: ToChar */
/** 
 * Puts a string representing the given NXReal with the given precision into the
 * given buffer. Make sure your buffer is large enough to handle the resulting
 * string.
 */
void NXRealUtils::ToChar(const NXReal& number, char* charBuffer,
						 int precision) {
	sprintf(charBuffer, "%.*g", precision, number);
}


/* FUNCTION: ScaleStringToEnum */
/** Returns the scale for the given string. */
NXRealUtils::Scale NXRealUtils::ScaleStringToEnum(const char* scaleString) {
	if (strcmp(scaleString, "Y") == 0) return YOTTA;
	else if (strcmp(scaleString, "Z") == 0) return ZETTA;
	else if (strcmp(scaleString, "E") == 0) return EXA;
	else if (strcmp(scaleString, "P") == 0) return PETA;
	else if (strcmp(scaleString, "T") == 0) return TERA;
	else if (strcmp(scaleString, "G") == 0) return GIGA;
	else if (strcmp(scaleString, "M") == 0) return MEGA;
	else if (strcmp(scaleString, "k") == 0) return KILO;
	else if (strcmp(scaleString, "h") == 0) return HECTO;
	else if (strcmp(scaleString, "da") == 0) return DECA;
	else if (strcmp(scaleString, "d") == 0) return DECI;
	else if (strcmp(scaleString, "c") == 0) return CENTI;
	else if (strcmp(scaleString, "m") == 0) return MILLI;
	else if (strcmp(scaleString, "u") == 0) return MICRO;
	else if (strcmp(scaleString, "n") == 0) return NANO;
	else if (strcmp(scaleString, "p") == 0) return PICO;
	else if (strcmp(scaleString, "f") == 0) return FEMTO;
	else if (strcmp(scaleString, "a") == 0) return ATTO;
	else if (strcmp(scaleString, "z") == 0) return ZEPTO;
	else if (strcmp(scaleString, "y") == 0) return YOCTO;
	else if (strcmp(scaleString, "A") == 0) return ANGSTROM;
	else return NONE;
}

} // Nanorex::

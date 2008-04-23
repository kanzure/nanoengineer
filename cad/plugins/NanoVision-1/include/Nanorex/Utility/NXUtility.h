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

#include <string>
#include <iostream>

namespace Nanorex {

	
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
		static std::string dtos(double d);
	private:
};


/* CLASS: NXException */
/**
 * A simple exception class.
 * @ingroup NanorexUtility
 */
class NXException {
	public:
		NXException() {};
		NXException(const std::string& message) { this->message = message; }
		const std::string& getMessage() const { return message; }

	private:
		std::string message;
};


} // Nanorex::

#endif

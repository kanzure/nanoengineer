// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_STRINGTOKENIZER_H
#define NX_STRINGTOKENIZER_H

#ifdef WIN32
#	ifdef _MSC_VER
#		pragma warning(disable:4786)
#	endif
#endif

#include <string>

namespace Nanorex {


/* CLASS: NXStringTokenizer */
/**
 * Breaks delimited strings up into accessible tokens. Here is an example
 * usage:
 * \code
 std::string colors = "red,green,blue";
 nanohive::StringTokenizer tokenizer(colors, ",");
 while (tokenizer.hasMoreTokens())
	std::cout << tokenizer.getNextToken() << std::endl;
 * \endcode
 * This example would print:
 * \code
 red
 green
 blue
 * \endcode
 *
 * @ingroup NanoHiveUtil
 */
class NXStringTokenizer {
	public:
		NXStringTokenizer(const std::string& line,
						const std::string& delimiters = " ");
		std::string getNextToken();
		bool hasMoreTokens();

	private:
		std::string inString, delimiters;
		int inStringLength, position;
};

} // Nanorex::

#endif

// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "Nanorex/Utility/NXStringTokenizer.h"

namespace Nanorex {


/* CONSTRUCTOR */
/**
 * Constructs a tokenizer for the given line delimited with the given
 * delimiters. For example, the string foo;bar;baz; has three tokens
 * delimited with semi-colons.
 */
NXStringTokenizer::NXStringTokenizer(const std::string& line,
									 const std::string& delimiters) {
	inString = line;
	this->delimiters = delimiters;

	inStringLength = inString.length();
	position = 0;
}


/* FUNCTION: getNextToken */
/**
 * Returns the next token encountered in the string.
 */
std::string NXStringTokenizer::getNextToken() {

	int tokenStart = position;
	int tokenLength = 0;
	while ((delimiters.find(inString[position]) == std::string::npos) &&
		   (position < inStringLength)) {
		tokenLength++;
		position++;
	}
	std::string token = inString.substr(tokenStart, tokenLength);
	position++;

	return token;
}


/* FUNCTION: hasMoreTokens */
/**
 * Returns whether or not there are more tokens in the string.
 */
bool NXStringTokenizer::hasMoreTokens() {
	int index = position;

	if (index < inStringLength)
		return true;
	else
		return false;
}

} // Nanorex::

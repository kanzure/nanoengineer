// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "Nanorex/Utility/NXCommandResult.h"

namespace Nanorex {


/* CONSTRUCTOR */
NXCommandResult::NXCommandResult() {
	resultId = -2;	// -2 is the code for "No code set"
}


/* ACCESSORS */
/** Sets the result code for this result. */
void NXCommandResult::setResult(int resultId) { this->resultId = resultId; }
/** Returns the result code for this result. */
int NXCommandResult::getResult() const { return resultId; }

/** Sets the vector of additional explanatory data for this result. */
void NXCommandResult::setParamVector(std::vector<QString> const& paramVector) {
	this->paramVector = paramVector;
}
/** Returns the vector of additional explanatory data for this result. */
const std::vector<QString>& NXCommandResult::getParamVector() const {
	return paramVector;
}


} // Nanorex::

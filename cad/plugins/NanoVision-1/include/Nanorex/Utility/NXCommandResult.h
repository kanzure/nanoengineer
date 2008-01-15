// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_COMMANDRESULT_H
#define NX_COMMANDRESULT_H

#ifdef WIN32
#	ifdef _MSC_VER
#		pragma warning(disable:4786)
#	endif
#endif

#include <string>
#include <vector>

//#include "NanoHiveUtil/Utility.h"

namespace Nanorex {

/* CLASS: NXCommandResult */
/**
 * Encapsulates the results of a command execution. Use the
 * \c data/local/*_resultCodes.txt file to decode the result codes and
 * informational vector into human readable results.
 * @ingroup NanorexUtility
 */
class NXCommandResult {
	public:
		NXCommandResult();
		void setResult(int resultId);
		int getResult();
		void setParamVector(std::vector<std::string>& paramVector);
		const std::vector<std::string>& getParamVector() const;

	private:
		int resultId;
		std::vector<std::string> paramVector;
};

} // Nanorex::

#endif

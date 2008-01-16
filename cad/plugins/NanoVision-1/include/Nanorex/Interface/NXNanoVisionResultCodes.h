// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_NANOVISIONRESULTCODES_H
#define NX_NANOVISIONRESULTCODES_H

#ifdef WIN32
#	ifdef _MSC_VER
#		pragma warning(disable:4786)
#	endif
#endif

#include <vector>
#include <QString>

namespace Nanorex {

typedef enum {
	NX_NO_CODE = -2,
	NX_INTERNAL_ERROR = -1,				NX_CMD_SUCCESS = 0,
	NX_FILE_NOT_FOUND = 1,				NX_PLUGIN_NOT_FOUND = 2,
	NX_PLUGIN_CAUSED_ERROR = 3,			NX_PLUGIN_REPORTS_ERROR = 4
} NXResultCode;


static QString GetNV1ResultCodeString(NXCommandResult* commandResult) {
	std::vector<QString> paramVector = commandResult->getParamVector();
	switch (commandResult->getResult()) {
	
		case NX_NO_CODE:
			return tr("Internal error: NXCommandResult not populated.");
			break;
			
		case NX_INTERNAL_ERROR:
			return tr("Internal error: %1").arg(paramVector[0]);
			break;
			
		case NX_CMD_SUCCESS:
			return tr("Ok");
			break;
			
		case NX_FILE_NOT_FOUND:
			// %1 Who is reporting
			// %2 The name of the file that was not found
			// %3 Why the file was not found
			return tr("%1 reports that a file was not found: %2: %3")
					.arg(paramVector[0].arg(paramVector[1])
					.arg(paramVector[2]);
			break;
			
		case NX_PLUGIN_NOT_FOUND:
			// %1 Who is reporting
			// %2 The name of the plugin that was not found
			// %3 Why the plugin was not found
			return tr("%1 reports that a plugin was not found: %2: %3")
					.arg(paramVector[0].arg(paramVector[1])
					.arg(paramVector[2]);
			break;
					
		case NX_PLUGIN_CAUSED_ERROR:
			// %1 Who is reporting
			// %2 The name of the plugin that caused the error
			// %3 A description of the error
			return tr("%1 reports that a plugin has caused an error: %2: %3")
					.arg(paramVector[0].arg(paramVector[1])
					.arg(paramVector[2]);
			break;
					
		case NX_PLUGIN_REPORTS_ERROR:
			// %1 The plugin that is reporting
			// %2 A description of the error
			return tr("%1 reports an error: %2")
					.arg(paramVector[0].arg(paramVector[1]);
			break;
			
		default:
			return tr("Internal error: Bad NXCommandResult code: %1")
					.arg(commandResult->getResult());
	}
}

} // Nanorex::

#endif

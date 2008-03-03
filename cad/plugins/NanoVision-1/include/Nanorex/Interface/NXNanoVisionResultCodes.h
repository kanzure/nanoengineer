// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_NANOVISIONRESULTCODES_H
#define NX_NANOVISIONRESULTCODES_H

#ifdef WIN32
#	ifdef _MSC_VER
#		pragma warning(disable:4786)
#	endif
#endif

#include <vector>
#include <QObject>
#include <QString>

#include "Nanorex/Utility/NXCommandResult.h"

namespace Nanorex {

typedef enum {
    NX_NO_CODE = -2,
    NX_INTERNAL_ERROR = -1,         NX_CMD_SUCCESS = 0,
    NX_FILE_NOT_FOUND = 1,          NX_PLUGIN_NOT_FOUND = 2,
    NX_PLUGIN_CAUSED_ERROR = 3,     NX_PLUGIN_REPORTS_ERROR = 4,
    NX_PLUGIN_REPORTS_WARNING = 5,  NX_INITIALIZATION_ERROR = 6
} NXResultCode;

extern QString GetNV1ResultCodeString(NXCommandResult* commandResult);

} // Nanorex::

#endif

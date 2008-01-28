
// Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 

#include "Nanorex/Interface/NXNanoVisionResultCodes.h"

namespace Nanorex {


/* FUNCTION: GetNV1ResultCodeString */
QString GetNV1ResultCodeString(NXCommandResult* commandResult) {
    std::vector<QString> paramVector = commandResult->getParamVector();
    QString returnString;
    switch (commandResult->getResult()) {
        
    case NX_NO_CODE:
        returnString =
            QObject::tr("Internal error: NXCommandResult not populated.");
        break;
        
    case NX_INTERNAL_ERROR:
        returnString = QObject::tr("Internal error: %1").arg(paramVector[0]);
        break;
        
    case NX_CMD_SUCCESS:
        returnString = QObject::tr("Ok");
        break;
        
    case NX_FILE_NOT_FOUND:
                        // %1 Who is reporting
                        // %2 The name of the file that was not found
                        // %3 Why the file was not found
        returnString = 
            QObject::tr("%1 reports that a file was not found: %2: %3")
            .arg(paramVector[0]).arg(paramVector[1])
            .arg(paramVector[2]);
        break;
        
    case NX_PLUGIN_NOT_FOUND:
                        // %1 Who is reporting
                        // %2 The name of the plugin that was not found
                        // %3 Why the plugin was not found
        returnString =
            QObject::tr("%1 reports that a plugin was not found: %2: %3")
            .arg(paramVector[0]).arg(paramVector[1])
            .arg(paramVector[2]);
        break;
        
    case NX_PLUGIN_CAUSED_ERROR:
                        // %1 Who is reporting
                        // %2 The name of the plugin that caused the error
                        // %3 A description of the error
        returnString =
            QObject::tr("%1 reports that a plugin has caused an error: %2: %3")
            .arg(paramVector[0]).arg(paramVector[1])
            .arg(paramVector[2]);
        break;
        
    case NX_PLUGIN_REPORTS_ERROR:
                        // %1 The plugin that is reporting
                        // %2 A description of the error
        returnString = QObject::tr("%1 reports an error: %2")
            .arg(paramVector[0]).arg(paramVector[1]);
        break;
        
    default:
        returnString =
            QObject::tr("Internal error: Bad NXCommandResult code: %1")
            .arg(commandResult->getResult());
        break;
    }
    return returnString;
}


} // Nanorex::

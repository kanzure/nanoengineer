// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_MMPIMPORTEXPORT_H
#define NX_MMPIMPORTEXPORT_H

#include "Nanorex/Interface/NXDataImportExportPlugin.h"

/* CLASS: NanorexMMPImportExport */
class NanorexMMPImportExport : public QObject, public NXDataImportExportPlugin
{
    Q_OBJECT
        Q_INTERFACES(Nanorex::NXDataImportExportPlugin)
        
public:
        
     NanorexMMPImportExport();
    ~NanorexMMPImportExport();
};

#endif // NX_MMPIMPORTEXPORT_H

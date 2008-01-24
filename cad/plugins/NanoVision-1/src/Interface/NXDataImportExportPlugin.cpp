// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "Nanorex/Interface/NXDataImportExportPlugin.h"

namespace Nanorex {

/* CONSTRUCTOR */
NXDataImportExportPlugin::NXDataImportExportPlugin() {
}


/* DESTRUCTOR */
NXDataImportExportPlugin::~NXDataImportExportPlugin() {
}


/* FUNCTION: setEntityManager 
void NXDataImportExportPlugin::setEntityManager
		(NXEntityManager* entityManager) {
	this->entityManager = entityManager;
}
*/

/* FUNCTION: setMode */
void NXDataImportExportPlugin::setMode(const string& mode) {
	this->mode = mode;
}


} // Nanorex::

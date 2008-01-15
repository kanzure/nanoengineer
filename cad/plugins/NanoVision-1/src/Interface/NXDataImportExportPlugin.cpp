// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "Nanorex/Interface/NXDataImportExportPlugin.h"

namespace Nanorex {

/* CONSTRUCTOR */
NXDataImportExportPlugin::NXDataImportExportPlugin() {
}


/* DESTRUCTOR */
NXDataImportExportPlugin::~NXDataImportExportPlugin() {
}


/* FUNCTION: setMode */
void NXDataImportExportPlugin::setMode(const std::string& mode) {
	this->mode = mode;
}


/* ACCESSORS */
void NXDataImportExportPlugin::setEntityManager
		(NXEntityManagerPlugin* entityManager) {
	this->entityManager = entityManager;
}


} // Nanorex::

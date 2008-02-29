// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_OPENBABELIMPORTEXPORT_H
#define NX_OPENBABELIMPORTEXPORT_H

#include <QDir>
#include <QFile>
#include <QString>
#include <QObject>

#include <openbabel/obconversion.h>

#include "Nanorex/Utility/NXLogger.h"
#include "Nanorex/Utility/NXCommandResult.h"
#include "Nanorex/Interface/NXMoleculeSet.h"
#include "Nanorex/Interface/NXNanoVisionResultCodes.h"
#include "Nanorex/Interface/NXDataImportExportPlugin.h"
using namespace Nanorex;

#include <vector>
#include <fstream>
#include <sstream>
#include <set>
#include <map>
#include <stack>
#include <cassert>
using namespace std;


/* CLASS: OpenBabelImportExport */
class OpenBabelImportExport : public QObject, public NXDataImportExportPlugin {
	Q_OBJECT
	Q_INTERFACES(Nanorex::NXDataImportExportPlugin)

	public:
		OpenBabelImportExport();
		~OpenBabelImportExport();

		// NXDataImportExportPlugin implementation
		NXCommandResult* importFromFile(NXMoleculeSet* moleculeSet,
										NXDataStoreInfo* dataStoreInfo,
										const std::string& filename,
										int frameSetId, int frameIndex);
		NXCommandResult* exportToFile(NXMoleculeSet* moleculeSet,
									  NXDataStoreInfo* dataStoreInfo,
									  const std::string& filename,
									  int frameSetId, int frameIndex);
	private:
		void populateCommandResult(NXCommandResult* result,
								   const string& message);
};

#endif

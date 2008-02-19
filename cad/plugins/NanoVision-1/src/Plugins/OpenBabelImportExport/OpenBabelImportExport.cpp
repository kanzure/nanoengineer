// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "OpenBabelImportExport.h"


/* CONSTRUCTOR */
OpenBabelImportExport::OpenBabelImportExport() {
}


/* DESTRUCTOR */
OpenBabelImportExport::~OpenBabelImportExport() {
}


/* FUNCTION: importFromFile */
NXCommandResult* OpenBabelImportExport::importFromFile
		(NXMoleculeSet* moleculeSet, NXDataStoreInfo* dataStoreInfo,
		 const string& filename, int frameSetId, int frameIndex) {
			
	bool success = true;
	NXCommandResult* result = new NXCommandResult();
	result->setResult(NX_CMD_SUCCESS);

	// Check input file format
	OBConversion conv;
	OBFormat* inFormat = conv.FormatFromExt(filename.c_str());
	if (inFormat) {
		conv.SetInFormat(inFormat);
		
	} else {
		populateCommandResult(result,
							  (string("Can't read file type: ") + filename)
							  	.c_str());
		success = false;
	}
	
	// Read file into a new OpenBabel molecule
	if (success) {
		ifstream inFileStream;
		inFileStream.open(filename.c_str());
		if (!inFileStream) {
			populateCommandResult(result,
								  (string("File not found: ") + filename)
								  	.c_str());
			success = false;
			
		} else {
			conv.SetInStream(&inFileStream);
			
			OBMol* obMolecule = moleculeSet->newMolecule();
			conv.Read(obMolecule);
			inFileStream.close();
		}
	}
	
	// Set the meta information about the data store.
	if (success) {
		dataStoreInfo->setIsSingleStructure(true);
	}
	
	return result;
}


/* FUNCTION: exportToFile */
NXCommandResult* OpenBabelImportExport::exportToFile
		(NXMoleculeSet* moleculeSet, NXDataStoreInfo* dataStoreInfo,
		 const string& filename, int frameSetId, int frameIndex) {
		
	bool success = true;
	NXCommandResult* result = new NXCommandResult();
	result->setResult(NX_CMD_SUCCESS);

	// Make sure we can handle the output type.
	OBConversion conv;
	OBFormat* outFormat = conv.FormatFromExt(filename.c_str());
	if (outFormat) {
		conv.SetOutFormat(outFormat);
		
	} else {
		populateCommandResult(result,
							  (string("Can't write file type: ") + filename)
							  	.c_str());
		success = false;
	}
	
	// Write the molecule to file
	if (success) {
		ofstream outFileStream;
		outFileStream.open(filename.c_str());
		if (!outFileStream) {
			populateCommandResult(result,
								(string("Couldn't open file: ") + filename)
									.c_str());
			success = false;
	
		} else {
			conv.SetOutStream(&outFileStream);
			
			OBMolIterator moleculeIter = moleculeSet->moleculesBegin();
			OBMol* obMolecule = *moleculeIter;
			conv.Write(obMolecule);
			outFileStream.close();
		}
	}
	return result;
}	


/* FUNCTION: populateCommandResult */
void OpenBabelImportExport::populateCommandResult
		(NXCommandResult* result, const string& message) {
	result->setResult(NX_PLUGIN_REPORTS_ERROR);
	vector<QString> resultVector;
	resultVector.push_back("OpenBabelImportExport");
	resultVector.push_back(message.c_str());
	result->setParamVector(resultVector);
}

Q_EXPORT_PLUGIN2 (OpenBabelImportExport, OpenBabelImportExport)

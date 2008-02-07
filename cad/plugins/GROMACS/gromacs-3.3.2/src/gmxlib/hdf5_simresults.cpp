
//#include <io.h>
#include <errno.h>

#include <sys/stat.h>

// hdf5_simresults.h is the GMX adaptor for HDF5_SimResults
#include "hdf5_simresults.h"
#include "Nanorex/HDF5_SimResults.h"

int frameIndex = 0;
Nanorex::HDF5_SimResults* simResults = 0;


/* FUNCTION: openHDF5dataStore */
void openHDF5dataStore(const char* dataStoreName) {
printf(">>> hdf5simresults.cpp:openHDF5dataStore\n");
	
	// The dataStoreName string will be something like foo.nh5. Strip the .nh5
	// off to form the directory name.
	//
	std::string dataStoreDirectory = dataStoreName;
	dataStoreDirectory.erase(strlen(dataStoreName) - 4, 4);
	
	// Backup old datastore file
	//
	char filename[128], backupFilename[128];
	sprintf(backupFilename, "%s/#%s#", dataStoreDirectory.c_str(),
			HDF5_SIM_RESULT_FILENAME);
	unlink(backupFilename);
	sprintf(filename, "%s/%s", dataStoreDirectory.c_str(),
			HDF5_SIM_RESULT_FILENAME);
	if (rename(filename, backupFilename) == 0)
		fprintf(stderr, "\n[HDF5] Backed up %s to %s\n", filename, backupFilename);
	else
		if (errno != ENOENT)
			fprintf(stderr, "\n[HDF5] Couldn't back up %s to %s (errno=%d)\n",
					filename, backupFilename, errno);
	
	// Create the datastore directory
	//
	int status =
		mkdir(dataStoreDirectory.c_str(),
			  S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);

	if (status == 0)
		fprintf(stderr, "[HDF5] HDF5 datastore directory created: %s\n",
				dataStoreDirectory.c_str());
	else
		if (errno != EEXIST)
			fprintf(stderr, "[HDF5] Failed to create the datastore directory: %s (errno=%d)\n",
					dataStoreDirectory.c_str(), errno);
		else
			status = 0;
	
	// Create the HDF5 datastore
	//
	std::string message;
	if (status == 0) {
		simResults = new Nanorex::HDF5_SimResults();
		
		status = simResults->openDataStore(dataStoreDirectory.c_str(), message);
		if (status) {
			fprintf(stderr, "[HDF5] Unable to open datastore %s: %d (%s)\n",
				   dataStoreDirectory.c_str(), status, message.c_str());
			delete simResults;
			simResults = 0;
		}
	}
	
	// Set the run result to "still running"
	status = simResults->setRunResult(1, "", message);
	
	// Create a frame set
	//
	if (status == 0) {
		status = simResults->addFrameSet(HDF5_FRAMESET_NAME, message);
		if (status) {
			fprintf(stderr, "[HDF5] Unable to create frameset %s: %d (%s)\n",
					HDF5_FRAMESET_NAME, status, message.c_str());
			delete simResults;
			simResults = 0;
		}
	}
}


/* FUNCTION: addHDF5frame */
void addHDF5frame(float time) {
	if (simResults == 0)
		return; // Short-circuit
	
	std::string message;
	int status =
		simResults->addFrame(HDF5_FRAMESET_NAME, time, frameIndex, message);
	if (status) {
		fprintf(stderr, "[HDF5] Unable to add frame for time=%g: %d (%s)\n",
				time, status, message.c_str());
		delete simResults;
		simResults = 0;
	}
}


/* FUNCTION: addHDF5atomIds */
void addHDF5atomIds(const unsigned int* atomIds, unsigned int atomCount) {
	if (simResults == 0)
		return; // Short-circuit

	std::string message;
	int status =
		simResults->setFrameAtomIds(HDF5_FRAMESET_NAME, atomIds, atomCount,
									message);
	if (status) {
		fprintf(stderr, "[HDF5] Unable to set atom Ids: %d (%s)\n",
				status, message.c_str());
		delete simResults;
		simResults = 0;
	}
}


/* FUNCTION: addHDF5atomicNumbers */
void addHDF5atomicNumbers(const unsigned int* atomicNumbers,
						  unsigned int atomCount) {
	if (simResults == 0)
		return; // Short-circuit

	std::string message;
	int status =
		simResults->setFrameAtomicNumbers(HDF5_FRAMESET_NAME, atomicNumbers,
										  atomCount, message);
	if (status) {
		fprintf(stderr, "[HDF5] Unable to set atomic numbers: %d (%s)\n",
				status, message.c_str());
		delete simResults;
		simResults = 0;
	}
}


/* FUNCTION: addHDF5bonds */
void addHDF5bonds(const void* bonds, unsigned int bondCount) {
	if (simResults == 0)
		return; // Short-circuit

	std::string message;
	int status =
		simResults->setFrameBonds(HDF5_FRAMESET_NAME, frameIndex, bonds,
								  bondCount, message);
	if (status) {
		fprintf(stderr, "[HDF5] Unable to add bonds to frame=%d: %d (%s)\n",
				frameIndex, status, message.c_str());
		delete simResults;
		simResults = 0;
	}
}


/* FUNCTION: addHDF5atomCoordinates */
void addHDF5atomCoordinates(const float* coordinates, unsigned int atomCount) {
	if (simResults == 0)
		return; // Short-circuit
	
	std::string message;
//printf("coords: %g %g %g\n", coordinates[0], coordinates[1], coordinates[2]);
	int status =
		simResults->setFrameAtomPositions(HDF5_FRAMESET_NAME, frameIndex,
										  coordinates, atomCount, message);
	if (status) {
		fprintf(stderr, "[HDF5] Unable to add atom coordinates to frame=%d: %d (%s)\n",
				frameIndex, status, message.c_str());
		delete simResults;
		simResults = 0;
	}
}


/* FUNCTION: flushHDF5 */
void flushHDF5() {
	if (simResults == 0)
		return; // Short-circuit

	simResults->flush();	
}


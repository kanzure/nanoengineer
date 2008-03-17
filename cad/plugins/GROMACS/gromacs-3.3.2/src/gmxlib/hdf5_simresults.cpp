
#ifdef WIN32
// Needed for unlink() on Win32 with MinGW
#include <io.h>
#endif

#include <errno.h>
#include <unistd.h>
#include <sys/stat.h>

// hdf5_simresults.h is the GMX adaptor for HDF5_SimResults
#include "hdf5_simresults.h"
#include "Nanorex/HDF5_SimResults.h"

int frameIndex = 0;
Nanorex::HDF5_SimResults* simResults = 0;


#ifdef WIN32
#include "windows.h"

/* FUNCTION: checkNamedMutexUnlocked
 *
 * Returns true if the mutex with the given name exists and was acquired by this
 * function, false otherwise.
 */
char mutexName[32];
bool mutexNameInitialized = false;
HANDLE mutex = NULL;
bool checkNamedMutex(const char* name) {
	
	// Add pid to mutex name so we only affect this process.
	if (!mutexNameInitialized) {
		sprintf(mutexName, "%s%d", name, getpid());
printf(">> mutexName=%s\n", mutexName);
		mutexNameInitialized = true;
	}

	if (mutex == NULL)
		mutex =
			OpenMutex( 
				MUTEX_ALL_ACCESS,	// request full access
				FALSE,				// handle not inheritable
				TEXT(mutexName));	// object name

	if (mutex != NULL) {
printf(">>> Mutex open\n");fflush(0);
		bool gotMutexLock = false;
		while (!gotMutexLock) {
			DWORD result =
				WaitForSingleObject( 
					mutex,			// handle to mutex
					500);			// give signaller 500 ms to let us lock
					
			if (result == WAIT_OBJECT_0) {
printf(">>> Got mutex (%s)\n", mutexName); fflush(0);
				gotMutexLock = true;
				
			} else {
printf(">>> didn't get mutex\n"), fflush(0);
			}
		}
		return true;
		
	} else {
printf(">>> mutex null\n");fflush(0);
	}
	return false;
}
#endif


/* FUNCTION: openHDF5dataStore */
void openHDF5dataStore(const char* dataStoreName) {
printf(">>> hdf5simresults.cpp: openHDF5dataStore\n");
	
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
#if defined(WIN32)
	int status =
		mkdir(dataStoreDirectory.c_str());
#else
	int status =
		mkdir(dataStoreDirectory.c_str(),
			  S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
#endif

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
	simResults->flush();
}


/* FUNCTION: addHDF5inputParameters */
void addHDF5inputParameters(const HDF5inputParameters* inputParams) {
	if (simResults == 0)
		return; // Short-circuit

	std::string message;
	simResults->setStringParameter
		("GMX.pbc", inputParams->pbc, message);
	simResults->setStringParameter
		("GMX.integrator", inputParams->integrator, message);
	simResults->setStringParameter
		("GMX.ns_type", inputParams->ns_type, message);
	simResults->setIntParameter
		("GMX.nsteps", inputParams->nsteps, message);
	simResults->setIntParameter
		("GMX.nstcgsteep", inputParams->nstcgsteep, message);
	simResults->setIntParameter
		("GMX.nstlist", inputParams->nstlist, message);
	simResults->setFloatParameter
		("GMX.rlist", inputParams->rlist, message);
	simResults->setFloatParameter
		("GMX.rcoulomb", inputParams->rcoulomb, message);
	simResults->setFloatParameter
		("GMX.rvdw", inputParams->rvdw, message);
	simResults->setFloatParameter
		("GMX.epsilon_r", inputParams->epsilon_r, message);
	simResults->setFloatParameter
		("GMX.emtol", inputParams->emtol, message);
	simResults->setFloatParameter
		("GMX.emstep", inputParams->emstep, message);
	
	// Hard-coded for now
	simResults->setFilePath((const char*)("input.mmp"),
							(const char*)("input.mmp"), message);
	simResults->flush();
}


/* FUNCTION: addHDF5resultsData */
void addHDF5resultsData(const HDF5resultsData* resultsData) {
	if (simResults == 0)
		return; // Short-circuit

	std::string message, reason;
	int result = 2;
	if (resultsData->converged) {
		result = 0; // success
		
	} else if (resultsData->convergedToMachinePrecision) {
		result = 2; // failure
		reason = "Converged to machine precision.";
		
	} else if (resultsData->gotSIGTERM) {
		result = 3; // aborted
		reason = "Received SIGTERM.";
	}
	simResults->setRunResult(result, reason.c_str(), message);
printf(">>> addHDF5resultsData: runResult=%d\n", result);fflush(0);
	
	simResults->setIntResult
		("FinalStep", resultsData->finalStep, message);
	simResults->setFloatResult
		("TotalEnergy", resultsData->totalEnergy, message);
	simResults->setFloatResult
		("MaximumForce", resultsData->maxForce, message);
		
	simResults->flush();
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
	simResults->flush();
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
	simResults->flush();
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
	simResults->flush();
}


/* FUNCTION: addHDF5atomCoordinates */
void addHDF5atomCoordinates(const float* coordinates, unsigned int atomCount) {
	if (simResults == 0)
		return; // Short-circuit
	
	std::string message;
	int status =
		simResults->setFrameAtomPositions(HDF5_FRAMESET_NAME, frameIndex,
										  coordinates, atomCount, message);
	if (status) {
		fprintf(stderr, "[HDF5] Unable to add atom coordinates to frame=%d: %d (%s)\n",
				frameIndex, status, message.c_str());
		delete simResults;
		simResults = 0;
	}
	simResults->flush();
}


/* FUNCTION: closeHDF5dataStore */
void closeHDF5dataStore() {
	delete simResults;
	simResults = 0;
}



#ifndef hdf5_simresults_h
#define hdf5_simresults_h

#define HDF5_FRAMESET_NAME "frame-set-1"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
	char pbc[4];
	char integrator[8];
	char ns_type[8];
	int nsteps, nstcgsteep, nstlist;
	float rlist, rcoulomb, rvdw, epsilon_r, emtol, emstep;
} HDF5inputParameters;

typedef struct {
	int gotSIGTERM, converged, convergedToMachinePrecision;
	int finalStep;
	float totalEnergy, maxForce;
} HDF5resultsData;

#ifdef WIN32
bool checkNamedMutex(const char* name);
#endif

void openHDF5dataStore(const char* dataStoreName);
void addHDF5inputParameters(const HDF5inputParameters* inputParams);
void addHDF5resultsData(const HDF5resultsData* resultsData);
void addHDF5frame(float time);
void addHDF5atomIds(const unsigned int* atomIds, unsigned int atomCount);
void addHDF5atomicNumbers(const unsigned int* atomicNumbers,
								 unsigned int atomCount);
void addHDF5bonds(const void* bonds, unsigned int bondCount);
void addHDF5atomCoordinates(const float* coordinates,
								   unsigned int atomCount);
void closeHDF5dataStore();

#ifdef __cplusplus
} // extern "C" {
#endif

#endif


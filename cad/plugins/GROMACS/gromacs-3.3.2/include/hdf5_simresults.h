
#ifndef hdf5_simresults_h
#define hdf5_simresults_h

#define HDF5_FRAMESET_NAME "frame-set-1"

#ifdef __cplusplus
extern "C" {
#endif

extern void openHDF5dataStore(const char* dataStoreName);
extern void addHDF5frame(float time);
extern void addHDF5atomIds(const unsigned int* atomIds, unsigned int atomCount);
extern void addHDF5atomicNumbers(const unsigned int* atomicNumbers,
								 unsigned int atomCount);
extern void addHDF5bonds(const void* bonds, unsigned int bondCount);
extern void addHDF5atomCoordinates(const float* coordinates,
								   unsigned int atomCount);
extern void flushHDF5();

#ifdef __cplusplus
} // extern "C" {
#endif

#endif


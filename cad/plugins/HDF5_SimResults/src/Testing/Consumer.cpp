
// Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 

#include <stdlib.h>
#include <stdio.h>
#include <signal.h> 
#include <time.h> 

#include <string>


#include "Nanorex/HDF5_SimResults.h"
using namespace Nanorex;

unsigned int renderHelper(HDF5_SimResults* hdf5_SimResults,
                          const unsigned int& frameIndex,
                          bool justFrameCount);
void printScene(unsigned int frameIndex, unsigned int frameCount);

void set_timespec(struct timespec *tmr, unsigned long long ustime) {
	tmr->tv_sec = (time_t) (ustime / 1000000ULL);
	tmr->tv_nsec = (long) (1000ULL * (ustime % 1000000ULL));
}


HDF5_SimResults* simResults = 0;
unsigned int frameIndex = 0;
void render(int dummy) {
	int frameCount = renderHelper(simResults, frameIndex, false);
	if (frameIndex < frameCount)
		frameIndex++;
}


/* FUNCTION: main */
int main(int argc, char* argv[]) {
	
	simResults = new HDF5_SimResults();
	
	std::string message;
	int status;
	if (argc > 1)
		status = simResults->openDataStore(argv[1], message);
	else
		status = simResults->openDataStore("Testing/shared", message);
	if (status) {
		printf("Couldn't open %s: %s\n", "Testing/shared", message.c_str());
		exit(1);
	}
		
	int frameCount, frameIndex = 0;

	// Set up a repeating timer and start it
	timer_t timerid;
	struct sigaction sigact;
	struct sigevent sigev;
	sigact.sa_handler = render;
	sigemptyset(&(sigact.sa_mask));
	sigact.sa_flags = 0;
	if (sigaction(SIGUSR1, &sigact, (struct sigaction *)NULL) == -1) {
		printf("sigaction failed");
		exit(1);
	}
	sigev.sigev_notify = SIGEV_SIGNAL;
	sigev.sigev_signo = SIGUSR1;
	if (timer_create(CLOCK_REALTIME, &sigev, &timerid) == -1) {
		printf("timer_create failed");
		exit(1);
	}
	struct itimerspec tmr;
	set_timespec(&tmr.it_value, 100 * 1000); // 100 milliseconds
	set_timespec(&tmr.it_interval, 100 * 1000);
	if (timer_settime(timerid, 0, &tmr, (struct itimerspec *)NULL) == -1) {
		printf("timer_create failed");
		exit(1);
	}

	while (true) {
		pause();
		//sleep(1);
	}
	return 0;
}


/* Variables needed by renderHelper() and printScene(). */
unsigned int atomIdCount, bondIdCount;
int* atomicNumbers, *aIds, *bIds;
float zoom;
float* xCoords, *yCoords, *zCoords;

/* FUNCTION: renderHelper */
unsigned int renderHelper(HDF5_SimResults* hdf5_SimResults,
                    	  const unsigned int& frameIndex,
                          bool justFrameCount) {
    int status, frameCount;
    std::string message;

    hdf5_SimResults->synchronize();

    // Setup atom arrays (once), assumes the number of atoms in the system is
    // constant.
    static bool InitializeAtoms = true;
    if (InitializeAtoms) {
        hdf5_SimResults->getFrameAtomIdsCount("frame-set-1", atomIdCount);
        if (atomIdCount > 0) {
            xCoords = (float*)malloc(atomIdCount*sizeof(float));
            yCoords = (float*)malloc(atomIdCount*sizeof(float));
            zCoords = (float*)malloc(atomIdCount*sizeof(float));
            atomicNumbers = (int*)malloc(atomIdCount*sizeof(int));
            InitializeAtoms = false;
        }
    }

    // Check bond counts and memory allocation.
    // Note: The zero in the following makes assumptions that need to be
    // generalized later. Plus, this assumes that bonds never change.
    static bool InitializeBonds = true;
    if (InitializeBonds) {
        hdf5_SimResults->getFrameBondsCount("frame-set-1", 0, bondIdCount);
        if (bondIdCount > 0) {
            aIds = (int*)malloc(bondIdCount*sizeof(int));
            bIds = (int*)malloc(bondIdCount*sizeof(int));
            InitializeBonds = false;
        }
    }

    // Get time dimension count
    hdf5_SimResults->getFrameCount("frame-set-1", frameCount);
    if ((frameIndex < frameCount) && !justFrameCount) {

        // Atoms
        //
        float* positions = (float*)malloc(atomIdCount*3*sizeof(float));
        status =
            hdf5_SimResults->getFrameAtomPositions("frame-set-1",
                                                   frameIndex, atomIdCount,
                                                   positions, message);

        // Collect the atom positions. Center the molecule and assign atomic
        // numbers the first time it is displayed.
        static bool InitializeMolecule = true;
        static float xShift = 0.0, yShift = 0.0, zShift = 0.0;
        float maxX, minX, maxY, minY, maxZ, minZ;
        for (unsigned int atomIdIndex = 0;
             atomIdIndex < atomIdCount;
             atomIdIndex++) {
            xCoords[atomIdIndex] = positions[atomIdIndex*3 + 0] * 10 + xShift;
            yCoords[atomIdIndex] = positions[atomIdIndex*3 + 1] * 10 + yShift;
            zCoords[atomIdIndex] = positions[atomIdIndex*3 + 2] * 10 + zShift;
            if (InitializeMolecule) {
                if (atomIdIndex == 0) {
                    maxX = minX = xCoords[atomIdIndex];
                    maxY = minY = yCoords[atomIdIndex];
                    maxZ = minZ = zCoords[atomIdIndex];

                } else {
                    if (xCoords[atomIdIndex] > maxX)
                        maxX = xCoords[atomIdIndex];
                    else if (xCoords[atomIdIndex] < minX)
                        minX = xCoords[atomIdIndex];
                    if (yCoords[atomIdIndex] > maxY)
                        maxY = yCoords[atomIdIndex];
                    else if (yCoords[atomIdIndex] < minY)
                        minY = yCoords[atomIdIndex];
                    if (zCoords[atomIdIndex] > maxZ)
                        maxZ = zCoords[atomIdIndex];
                    else if (zCoords[atomIdIndex] < minZ)
                        minZ = zCoords[atomIdIndex];
                }
            }
        }
        free(positions);
        if (InitializeMolecule) {
            xShift = (minX + maxX) / -2.0;
            yShift = (minY + maxY) / -2.0;
            zShift = (minZ + maxZ) / -2.0;

            // Determine initial zoom
            float maxVector = maxX - minX;
            if (maxY - minY > maxVector) maxVector = maxY - minY;
            if (maxZ - minZ > maxVector) maxVector = maxZ - minZ;
            zoom = maxVector * -1.28;

            unsigned int* _atomicNumbers =
                (unsigned int*)malloc(atomIdCount*3*sizeof(unsigned int));
            status =
                hdf5_SimResults->getFrameAtomicNumbers("frame-set-1",
                                                       _atomicNumbers, message);
            for (unsigned int atomIdIndex = 0;
                 atomIdIndex < atomIdCount;
                 atomIdIndex++) {
                xCoords[atomIdIndex] += xShift;
                yCoords[atomIdIndex] += yShift;
                zCoords[atomIdIndex] += zShift;
                atomicNumbers[atomIdIndex] = _atomicNumbers[atomIdIndex];
            }
            free(_atomicNumbers);
            InitializeMolecule = false;
        }

        // Bonds
        //
        static bool InitializeBonds2 = true;
        if (InitializeBonds2) {
            SimResultsBond* bonds =
                (SimResultsBond*)malloc
                    (bondIdCount*sizeof(SimResultsBond));
            status =
                hdf5_SimResults->getFrameBonds("frame-set-1", 0,
                                               bonds, message);
            for (unsigned int bondIdIndex = 0;
                 bondIdIndex < bondIdCount;
                 bondIdIndex++) {
                aIds[bondIdIndex] = bonds[bondIdIndex].atomId_1;
                bIds[bondIdIndex] = bonds[bondIdIndex].atomId_2;
            }
            free(bonds);
            InitializeBonds2 = false;
        }

        // Redraw scene
        //Refresh(FALSE);
		printScene(frameIndex, frameCount);
    }
    return frameCount;
}


/* FUNCTION: printScene */
void printScene(unsigned int frameIndex, unsigned int frameCount) {
	printf("\n==========================\n");
	printf("atoms:%d bonds:%d frame:%d/%d\n",
		   atomIdCount, bondIdCount, frameIndex+1, frameCount);
}


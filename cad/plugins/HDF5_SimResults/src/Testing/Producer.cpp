
// Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
#include <stdlib.h>
#include <string>

#include "Nanorex/HDF5_SimResults.h"
using namespace Nanorex;


/* FUNCTION: main */
int main(int argc, char* argv[]) {
	
	HDF5_SimResults* simResults = new HDF5_SimResults();
	
	std::string message;
	int status = simResults->openDataStore("Testing/shared", message);
	if (status) {
		printf("Couldn't open %s: %s\n", "Testing/shared", message.c_str());
		exit(1);
	}
	
	status = simResults->setRunResult(1, "", message);

	status = simResults->addFrameSet("frame-set-1", message);
	if (status) {
		printf("Error: %s\n", message.c_str());
		exit(1);
	}
		
	int frameIndex = 0;
	int atomIndex;
	int nAtoms = 3;
	float positions[nAtoms*3];

	unsigned int atomIds[] = { 0, 1, 2 };
	status =
		simResults->setFrameAtomIds("frame-set-1", atomIds, nAtoms, message);
	if (status) {
		printf("Error: %s\n", message.c_str());
		exit(1);
	}

	unsigned int atomicNumbers[] = { 8, 1, 1 };
	status =
		simResults->setFrameAtomicNumbers
					("frame-set-1", atomicNumbers, nAtoms, message);
	if (status) {
		printf("Error: %s\n", message.c_str());
		exit(1);
	}

	while (frameIndex < 50/*true*/) {
		status = simResults->addFrame("frame-set-1", 0.0, frameIndex, message);
		if (status) {
			printf("Error: %s\n", message.c_str());
			exit(1);
		}
		printf("Added frame: %d\n", frameIndex);
		
		for (atomIndex = 0; atomIndex < nAtoms; atomIndex++) {
			positions[atomIndex*3+0] = frameIndex * 1.0f;
			positions[atomIndex*3+1] = frameIndex * 1.0f + 1.0f;
			positions[atomIndex*3+2] = frameIndex * 1.0f + 2.0f;
		}
		status =
			simResults->setFrameAtomPositions("frame-set-1", frameIndex,
											  positions, 3, message);
		if (status) {
			printf("Error: %s\n", message.c_str());
			exit(1);
		}
		
		sleep(1/*2*/);
	}

	simResults->setRunResult(0, "", message);
	return 0;
}


// Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
#include <stdlib.h>
#include <string>

#include "HDF5_SimResults.h"


/* FUNCTION: main */
int main(int argc, char* argv[]) {
	
	ne1::HDF5_SimResults* simResults = new ne1::HDF5_SimResults();
	
	std::string message;
	int status = simResults->openDataStore("Testing/shared", message);
	if (status) {
		printf("Couldn't open %s: %s\n", "Testing/shared", message.c_str());
		exit(1);
	}
		
	int frameCount, frameIndex, atomIndex;
	int nAtoms = 3;
	float positions[nAtoms*3];
	while (true) {
		simResults->synchronize();
		simResults->getFrameCount("frame-set-1", frameCount);
		printf("Frame count: %d\n", frameCount);
		
		for (frameIndex = 0; frameIndex < frameCount; frameIndex++) {
			status =
				simResults->getFrameAtomPositions("frame-set-1", frameIndex, 3,
												  positions, message);
			if (status) {
				printf("Error: %s\n", message.c_str());
				exit(1);
			}
			
			for (atomIndex = 0; atomIndex < nAtoms; atomIndex++) {
				printf("%g ", positions[atomIndex*3+0]);
			}
		}
		printf("\n==========================\n");

		sleep(1);
	}
	
	return 0;
}

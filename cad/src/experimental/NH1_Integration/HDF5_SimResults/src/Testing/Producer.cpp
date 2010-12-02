
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
	
	status = simResults->addFrameSet("frame-set-1", message);
	if (status) {
		printf("Error: %s\n", message.c_str());
		exit(1);
	}
		
	int frameIndex, atomIndex;
	int nAtoms = 3;
	float positions[nAtoms*3];
	while (true) {
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
		
		sleep(2);
	}
	
	return 0;
}

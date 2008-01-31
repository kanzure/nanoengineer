
// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include <stdlib.h>
#include <stdio.h>
#include <signal.h> 
#include <time.h> 

#include <string>

#include "Nanorex/Interface/NXEntityManager.h"
using namespace Nanorex;


/* FUNCTION: set_timespec */
void set_timespec(struct timespec *tmr, unsigned long long ustime) {
	tmr->tv_sec = (time_t) (ustime / 1000000ULL);
	tmr->tv_nsec = (long) (1000ULL * (ustime % 1000000ULL));
}


NXEntityManager* entityManager = 0;
int trajId = 0;
unsigned int frameIndex = 0;


/* FUNCTION: render */
void render(int dummy) {
	NXMoleculeSet* moleculeSet =
		entityManager->getRootMoleculeSet(trajId, frameIndex);
	unsigned int frameCount = 0;
	if (moleculeSet != 0) {
		printf("\n==========================\n");
		frameCount = entityManager->getFrameCount(trajId);
		OBMolIterator moleculeIter = moleculeSet->moleculesBegin();
		printf("%d ", (*moleculeIter)->GetAtom(1)->GetAtomicNum());
		printf("%g ", (*moleculeIter)->GetAtom(1)->GetZ());
		printf("%d ", (*moleculeIter)->NumBonds());
		printf("frame:%d/%d\n", frameIndex+1, frameCount);

		frameIndex++;
	}
}


/* FUNCTION: main */
int main(int argc, char* argv[]) {

	// Set the entity manager up
	//
	entityManager = new NXEntityManager();
		
	NXProperties* properties = new NXProperties();
	properties->setProperty("NXEntityManager.importExport.0.plugin",
							"libHDF5_SimResultsImportExport");
	entityManager->loadDataImportExportPlugins(properties);
	delete properties;

	// Prime read
	NXCommandResult* commandResult =
		entityManager->importFromFile("Testing/shared.nh5");
	if (commandResult->getResult() != NX_CMD_SUCCESS) {
		printf("%s\n", qPrintable(GetNV1ResultCodeString(commandResult)));
		exit(1);
	}

	// Discover a store-not-complete trajectory frame set
	NXDataStoreInfo* dataStoreInfo = entityManager->getDataStoreInfo();
	trajId = dataStoreInfo->getTrajectoryId("frame-set-1");
	if (dataStoreInfo->storeIsComplete(trajId)) {
		printf("error: data store is complete\n");
		exit(1);
	}

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
	set_timespec(&tmr.it_value, 1000 * 1000); // 1000 milliseconds
	//set_timespec(&tmr.it_value, 100 * 1000); // 100 milliseconds
	set_timespec(&tmr.it_interval, 100 * 1000);
	if (timer_settime(timerid, 0, &tmr, (struct itimerspec *)NULL) == -1) {
		printf("timer_create failed");
		exit(1);
	}

	while (!dataStoreInfo->storeIsComplete(trajId)) {
		printf(" . "); fflush(0);
		pause();
	}
	return 0;
}

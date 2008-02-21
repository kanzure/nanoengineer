// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include "TrajectoryGraphicsPane.h"


/* CONSTRUCTOR */
TrajectoryGraphicsPane::TrajectoryGraphicsPane(QWidget *parent)
		: DataWindow(parent), Ui_TrajectoryGraphicsPane() {

	setupUi(this);
	
	_frameIndex = 0;
}


/* DESTRUCTOR */
TrajectoryGraphicsPane::~TrajectoryGraphicsPane() {
}


/* FUNCTION: newFrame */
void TrajectoryGraphicsPane::newFrame(int frameSetId, int frameIndex,
									  NXMoleculeSet* newMoleculeSet) {
	
	// Start printing all frames available from the first render() call
	unsigned int frameCount = 0;
	QString line;
	NXMoleculeSet* moleculeSet =
		entityManager->getRootMoleculeSet(frameSetId, _frameIndex);
	while (moleculeSet != 0) {
		textEdit->insertPlainText("\n==========================\n");
		line =
			QString("storeComplete=%1 ").arg(entityManager->getDataStoreInfo()->storeIsComplete(frameSetId));
		textEdit->insertPlainText(line);
		frameCount = entityManager->getFrameCount(frameSetId);
		line =
			QString("frame: %1%2/%3\n")
			   .arg(_frameIndex+1)
			   .arg(moleculeSet == newMoleculeSet ? "*" : "")
			   .arg(frameCount);
		textEdit->insertPlainText(line);

		_frameIndex++;
		moleculeSet =
			entityManager->getRootMoleculeSet(frameSetId, _frameIndex);
	}
	
	// Stop once the data store is complete
	//if (entityManager->getDataStoreInfo()->storeIsComplete(frameSetId))
	//	exit(0);
}


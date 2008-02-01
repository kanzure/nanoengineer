// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef HDF5_CONSUMER_H
#define HDF5_CONSUMER_H

#include <stdlib.h>
#include <stdio.h>

#include <string>

#include <QThread>
#include <QCoreApplication>

#include "Nanorex/Interface/NXEntityManager.h"
using namespace Nanorex;


/* CLASS: HDF5_Consumer */
class HDF5_Consumer : public QObject {

	Q_OBJECT
	
	public:
		HDF5_Consumer(NXEntityManager* entityManager) {
			this->entityManager = entityManager;
			_frameIndex = 0;
		}
		~HDF5_Consumer() { }
	
	public slots:
		void render(int frameSetId, int frameIndex,
					NXMoleculeSet* newMoleculeSet);
		
	private:
		unsigned int _frameIndex;
		NXEntityManager* entityManager;
};


#endif

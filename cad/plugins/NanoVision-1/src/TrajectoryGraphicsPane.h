// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#ifndef TRAJECTORYGRAPHICSPANE_H
#define TRAJECTORYGRAPHICSPANE_H

#include <QWidget>

#include "Nanorex/Interface/NXEntityManager.h"
using namespace Nanorex;

#include "DataWindow.h"
#include <ui_TrajectoryGraphicsPane.h>


/* CLASS: TrajectoryGraphicsPane */
class TrajectoryGraphicsPane
		: public DataWindow, private Ui_TrajectoryGraphicsPane {
			
	Q_OBJECT

	public:
		TrajectoryGraphicsPane(QWidget *parent = 0);
		~TrajectoryGraphicsPane();
		
		void setEntityManager(NXEntityManager* entityManager) {
			this->entityManager = entityManager;
		}
		
	public slots:
		void newFrame(int frameSetId, int frameIndex,
					  NXMoleculeSet* newMoleculeSet);

	private:
		unsigned int _frameIndex;
		NXEntityManager* entityManager;
};

#endif

// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#ifndef TRAJECTORYGRAPHICSWINDOW_H
#define TRAJECTORYGRAPHICSWINDOW_H

#include <QWidget>

#include "Nanorex/Interface/NXEntityManager.h"
using namespace Nanorex;

#include "DataWindow.h"
#include <ui_TrajectoryGraphicsWindow.h>


/* CLASS: TrajectoryGraphicsWindow */
class TrajectoryGraphicsWindow
		: public DataWindow, private Ui_TrajectoryGraphicsWindow {
			
	Q_OBJECT

	public:
		TrajectoryGraphicsWindow(QWidget *parent = 0);
		~TrajectoryGraphicsWindow();
		
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

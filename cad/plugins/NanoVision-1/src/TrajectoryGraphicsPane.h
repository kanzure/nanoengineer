// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#ifndef TRAJECTORYGRAPHICSPANE_H
#define TRAJECTORYGRAPHICSPANE_H

#include <QWidget>

#include <ui_TrajectoryGraphicsPane.h>


/* CLASS: TrajectoryGraphicsPane */
class TrajectoryGraphicsPane
		: public QWidget, private Ui_TrajectoryGraphicsPane {
	Q_OBJECT

public:
	TrajectoryGraphicsPane(QWidget *parent = 0);
	~TrajectoryGraphicsPane();
};

#endif

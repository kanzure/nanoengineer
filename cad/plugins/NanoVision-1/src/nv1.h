// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#ifndef NV1_H
#define NV1_H

#include <QtGui>
#include <QMainWindow>
#include <QFileDialog>
#include <QCloseEvent>

#include "Nanorex/Interface/NXEntityManager.h"
using namespace Nanorex;

#include "ResultsWindow.h"
#include "LogHandlerWidget.h"
#include "MainWindowTabWidget.h"


/* CLASS: nv1 */
class nv1 : public QMainWindow {
	Q_OBJECT

public:
	nv1(NXEntityManager* entityManager, LogHandlerWidget* logHandlerWidget);
	~nv1();

protected:
	void closeEvent (QCloseEvent *event);

private slots:
	void open();
	void about();
	void updateMenus();
	void updateWindowMenu();

private:
	NXEntityManager* entityManager;
	
	QMenu *fileMenu;
	QMenu *windowMenu;
	QMenu *helpMenu;
	QToolBar *fileToolBar;

	MainWindowTabWidget* mainWindowTabs;
	ResultsWindow* resultsWindow;
	
	QAction *openAction;
	QAction *exitAction;
	QAction *closeAction;
	QAction *closeAllAction;
	QAction *tileAction;
	QAction *cascadeAction;
	QAction *arrangeAction;
	QAction *nextAction;
	QAction *previousAction;
	QAction *separatorAction;
	QAction *aboutAction;
	
	void createActions();
	void createMenus();
	void createToolBars();
	void createStatusBar();
	void readSettings();
	void writeSettings();
};

#endif

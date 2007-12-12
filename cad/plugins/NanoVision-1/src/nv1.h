// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#ifndef NV1_H
#define NV1_H

#include <QtGui>
#include <QMainWindow>
#include <QFileDialog>
#include <QCloseEvent>

// For Qt 4.3: #include <QMdiArea>
#include <QWorkspace>

#include "MdiWindow.h"


/* CLASS: nv1 */
class nv1 : public QMainWindow {
	Q_OBJECT

public:
	nv1();
	~nv1();

protected:
	void closeEvent (QCloseEvent *event);

private slots:
	void open();
	void about();
	void updateMenus();
	void updateWindowMenu();
	MdiWindow* createMdiWindow();

private:
	void createActions();
	void createMenus();
	void createToolBars();
	void createStatusBar();
	void readSettings();
	void writeSettings();
	MdiWindow* activeMdiWindow();
	MdiWindow* findMdiWindow(const QString &fileName);

	QWorkspace* workspace;
	QSignalMapper* windowMapper;

//	void loadFile (const QString &fileName);
//	void setCurrentFile ( const QString &fileName );
//	QString strippedName ( const QString &fullFileName );

//	QString curFile;

	QMenu *fileMenu;
	QMenu *windowMenu;
	QMenu *helpMenu;
	QToolBar *fileToolBar;

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
};

#endif

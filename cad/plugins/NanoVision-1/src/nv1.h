// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.


#ifndef NV1_H
#define NV1_H

#include <QtGui>
#include <QMainWindow>
#include <QFileDialog>
#include <QCloseEvent>
//#include <QMdiArea>

//class QAction;
//class QMenu;


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

private:
	void createActions();
	void createMenus();
	void createToolBars();
	void createStatusBar();
	void readSettings();
	void writeSettings();
	void loadFile (const QString &fileName);
	void setCurrentFile ( const QString &fileName );
	QString strippedName ( const QString &fullFileName );

	QString curFile;

	QMenu *fileMenu;
	QMenu *helpMenu;
	QToolBar *fileToolBar;

	QAction *openAction;
	QAction *exitAction;
	QAction *aboutAction;
};

#endif

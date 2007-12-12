// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#ifndef MDIWINDOW_H
#define MDIWINDOW_H

#include <QWidget>
#include <QFile>
#include <QMessageBox>
#include <QApplication>
#include <QCloseEvent>
#include <QFileInfo>


/* CLASS: MdiWindow */
class MdiWindow : public QWidget {
	Q_OBJECT

public:
	MdiWindow(QWidget *parent = 0);
	~MdiWindow();

	bool loadFile(const QString &fileName);
	QString userFriendlyCurrentFile();
	QString currentFile() {
		return curFile;
	}

protected:
	void closeEvent(QCloseEvent *event);

private:
	void setCurrentFile(const QString &fileName);
	QString strippedName(const QString &fullFileName);

	QString curFile;
};

#endif

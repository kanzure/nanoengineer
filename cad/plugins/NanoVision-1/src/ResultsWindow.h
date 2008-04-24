// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#ifndef RESULTSWINDOW_H
#define RESULTSWINDOW_H

#include <QtGui>
#include <QFile>
#include <QWidget>
#include <QObject>
#include <QFileInfo>
#include <QWorkspace>
#include <QTreeWidget>
#include <QMainWindow>
#include <QDockWidget>
#include <QMessageBox>
#include <QCloseEvent>
#include <QApplication>

#include "Nanorex/Interface/NXEntityManager.h"
#include "Nanorex/Interface/NXGraphicsManager.h"
using namespace Nanorex;

#include "ui_ResultsWindow.h"
#include "DataWindow.h"
#include "ErrorDialog.h"
#include "ResultsSummaryWindow.h"
#include "InputParametersWindow.h"
#include "StructureGraphicsWindow.h"
#include "TrajectoryGraphicsWindow.h"


// forward decl
class StructureGraphicsTreeItem;

/* CLASS: ResultsWindow */
class ResultsWindow : public QWidget, private Ui_ResultsWindow {
	Q_OBJECT;
	
public:
	QWorkspace* workspace;
	QSignalMapper* windowMapper;
	NXEntityManager* entityManager;
	NXGraphicsManager* graphicsManager;
	
	ResultsWindow(NXEntityManager* entityManager,
	              NXGraphicsManager* graphicsManager,
	              QWidget* parent = 0);
	~ResultsWindow();
	
	bool loadFile(const QString &fileName);
	bool closeFile(void);
	
	QString userFriendlyCurrentFile();
	QString currentFile() { return curFile; }
	DataWindow* activeDataWindow();
	
	private slots:
		void resultsTreeItemDoubleClicked(QTreeWidgetItem* treeWidgetItem,
										  int column);
	private:
		QString curFile;
		
		QTreeWidget *resultsTree;
		QIcon resultsTreeIcon;
		QIcon nh5FileIcon;
		QIcon mmpFileIcon;
		QIcon atomIcon;
		QIcon atomSetIcon;
		QIcon inputParametersIcon;
		QIcon inputFilesIcon;
		QIcon inputFileIcon;
		QIcon resultsIcon;
		QIcon resultsTrajectoriesIcon;
		
		void setCurrentFile(const QString &fileName);
		QString strippedName(const QString &fullFileName);
		
		bool isMMPFile(std::string const& filename);
		
        void setupResultsTree(void);
		void setupSingleStructureTree(void);
		void setupSimulationResultsTree(void);
		StructureGraphicsTreeItem*
		setupMoleculeSetResultsSubtree(NXMoleculeSet *molSetPtr,
		                               QTreeWidgetItem *const molSetItem);
    // void setupMoleculeSetResultsSubtree_helper
    // 	(NXMoleculeSet *molSetPtr, QTreeWidgetItem *const molSetItem);	
};


/* CLASS: DataWindowTreeItem */
class DataWindowTreeItem : public QObject, public QTreeWidgetItem {
	
	Q_OBJECT;
	
public:
	DataWindowTreeItem(ResultsWindow* resultsWindow,
	                   QTreeWidget* treeWidget);
	DataWindowTreeItem(ResultsWindow* resultsWindow,
	                   QTreeWidgetItem* treeWidgetItem);
	virtual ~DataWindowTreeItem();
	
	virtual void showWindow() = 0;
	
public slots:
	virtual void refresh();
	
protected:
	ResultsWindow* resultsWindow;
};


/* CLASS: InputParametersTreeItem */
class InputParametersTreeItem : public DataWindowTreeItem {

	public:
		InputParametersTreeItem(ResultsWindow* resultsWindow,
								QTreeWidgetItem* treeWidgetItem);
		~InputParametersTreeItem();
		
		void showWindow();
		
	private:
		InputParametersWindow* inputParametersWindow;
};


/* CLASS: ResultsSummaryTreeItem */
class ResultsSummaryTreeItem : public QWidget, public DataWindowTreeItem {
	
	Q_OBJECT;
	
public:
	ResultsSummaryTreeItem(ResultsWindow* resultsWindow,
	                       QTreeWidgetItem* treeWidgetItem);
	~ResultsSummaryTreeItem();
	
	void showWindow();
	void setTrajectoryId(int trajectoryId) {
		this->trajectoryId = trajectoryId;
	}
	
public slots:
	void refresh();
	
private:
	int trajectoryId;
	ResultsSummaryWindow* resultsSummaryWindow;
	
	QIcon resultsSummaryIcon;
	QIcon resultsSummaryIcon2;
};


/* CLASS: StructureGraphicsTreeItem */
class StructureGraphicsTreeItem : public DataWindowTreeItem {
	
public:
	StructureGraphicsTreeItem(NXMoleculeSet *theMolSetPtr,
	                          ResultsWindow* theResultsWindow,
	                          QTreeWidgetItem* treeWidgetItem);
	StructureGraphicsTreeItem(OBMol *theMolPtr,
	                          ResultsWindow* resultsWindow,
	                          QTreeWidgetItem* treeWidgetItem);
	~StructureGraphicsTreeItem();
	
	void showWindow();
	
private:
	NXMoleculeSet *molSetPtr;
	ResultsWindow *resultsWindow;
	bool const deleteOnDestruct;
	StructureGraphicsWindow* structureWindow;
};


/* CLASS: TrajectoryGraphicsTreeItem */
class TrajectoryGraphicsTreeItem : public DataWindowTreeItem {
	
public:
	TrajectoryGraphicsTreeItem(const string& trajectoryName,
	                           ResultsWindow* theResultsWindow,
	                           QTreeWidgetItem* treeWidgetItem);
	~TrajectoryGraphicsTreeItem();
	
	void showWindow();
	
private:
	string trajectoryName;
	ResultsWindow *resultsWindow;
	TrajectoryGraphicsWindow* trajWindow;
};


#endif

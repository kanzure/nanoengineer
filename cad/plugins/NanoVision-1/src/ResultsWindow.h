// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#ifndef RESULTSWINDOW_H
#define RESULTSWINDOW_H

#include <QtGui>
#include <QWidget>
#include <QFile>
#include <QMessageBox>
#include <QApplication>
#include <QCloseEvent>
#include <QFileInfo>
#include <QMainWindow>
#include <QDockWidget>
#include <QWorkspace>
#include <QTreeWidget>

#include "Nanorex/Interface/NXEntityManager.h"
using namespace Nanorex;

#include "ui_ResultsWindow.h"
#include "DataWindow.h"
#include "ErrorDialog.h"
#include "InputParametersWindow.h"
#include "TrajectoryGraphicsWindow.h"


/* CLASS: ResultsWindow */
class ResultsWindow : public QWidget, private Ui_ResultsWindow {
	Q_OBJECT
	
	public:
		QWorkspace* workspace;
		QSignalMapper* windowMapper;
		NXEntityManager* entityManager;
				
		ResultsWindow(NXEntityManager* entityManager, QWidget* parent = 0);
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
		QIcon mmpFileIcon;
		QIcon atomIcon;
		QIcon atomSetIcon;
		QIcon inputParametersIcon;
		QIcon inputFilesIcon;
		QIcon inputFileIcon;
		QIcon resultsIcon;
		QIcon resultsSummaryIcon;
		QIcon resultsTrajectoriesIcon;
		
		void setCurrentFile(const QString &fileName);
		QString strippedName(const QString &fullFileName);
		
		bool isMMPFile(std::string const& filename);
		
		void updateResultsTree(void);
		void setupSingleStructureTree(void);
		void setupSimulationResultsTree(void);
		void setupMoleculeSetResultsSubtree(QTreeWidgetItem *const mmpFileItem);
		void setupMoleculeSetResultsSubtree_helper
			(NXMoleculeSet *molSetPtr, QTreeWidgetItem *const molSetItem);	
};


/* CLASS: DataWindowTreeItem */
class DataWindowTreeItem : public QTreeWidgetItem {

	public:
		DataWindowTreeItem(ResultsWindow* resultsWindow,
						   QTreeWidget* treeWidget);
		DataWindowTreeItem(ResultsWindow* resultsWindow,
						   QTreeWidgetItem* treeWidgetItem);
		virtual ~DataWindowTreeItem();
		
		virtual void showWindow() = 0;
		
	protected:
		ResultsWindow* resultsWindow;
};


/* CLASS: InputParametersTreeItem */
class InputParametersTreeItem : public DataWindowTreeItem {

	public:
		InputParametersTreeItem(ResultsWindow* resultsWindow,
								QTreeWidget* treeWidget);
		~InputParametersTreeItem();
		
		void showWindow();
		
	private:
		InputParametersWindow* inputParametersWindow;
};


/* CLASS: ResultsSummaryTreeItem 
class ResultsSummaryTreeItem : public DataWindowTreeItem {

	public:
		ResultsSummaryTreeItem(ResultsWindow* resultsWindow,
							   QTreeWidgetItem* treeWidgetItem);
		~ResultsSummaryTreeItem();
		
		void showWindow();
		
	private:
		ResultsSummaryWindow* resultsSummaryWindow;
};
*/

/* CLASS: TrajectoryGraphicsTreeItem */
class TrajectoryGraphicsTreeItem : public DataWindowTreeItem {

	public:
		TrajectoryGraphicsTreeItem(const string& trajectoryName,
								   ResultsWindow* resultsWindow,
								   QTreeWidgetItem* treeWidgetItem);
		~TrajectoryGraphicsTreeItem();
		
		void showWindow();
		
	private:
		string trajectoryName;
		TrajectoryGraphicsWindow* trajWindow;
};


#endif

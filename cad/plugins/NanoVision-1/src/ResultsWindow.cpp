// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include "ResultsWindow.h"


/* CONSTRUCTOR */
ResultsWindow::ResultsWindow(NXEntityManager* entityManager, QWidget* parent)
		: QWidget(parent), Ui_ResultsWindow() {
	this->entityManager = entityManager;
		
	setupUi(this);

	workspace = new QWorkspace();
 	connect(workspace, SIGNAL(windowActivated(QWidget *)),
 	        this, SLOT(parent->updateMenus()));
	windowMapper = new QSignalMapper(this);
	connect(windowMapper, SIGNAL(mapped(QWidget *)),
            workspace, SLOT(setActiveWindow(QWidget *)));
	
    // manoj modelTree UI experiment
    modelTree = new QTreeWidget(tabWidget);
    modelTree->setHeaderLabel(tr("foo.mmp"));
    QList<QTreeWidgetItem*> modelTreeItemList;
    QTreeWidgetItem *homeItem = new QTreeWidgetItem(modelTree);
    QIcon homeIcon(tr(":/Icons/home.png"));
    homeItem->setIcon(0, homeIcon);
    homeItem->setText(0, tr("Home"));
    modelTreeItemList.append(homeItem);
    QTreeWidgetItem *partItem = new QTreeWidgetItem(modelTree);
    QIcon partIcon(tr(":/Icons/Model_Tree.png"));
    partItem->setIcon(0, partIcon);
    partItem->setText(0, tr("Part"));
    modelTreeItemList.append(partItem);
    modelTree->addTopLevelItems(modelTreeItemList);
    

    int modelTreePos = tabWidget->addTab(modelTree, tr("Model Tree"));
            
	splitter->insertWidget(1, workspace);
	delete widget;
}


/* DESTRUCTOR */
ResultsWindow::~ResultsWindow() {
	workspace->closeAllWindows();
	if (activeDataWindow()) {
		; // Can't delete?
	}
}


/* FUNCTION: loadFile */
bool ResultsWindow::loadFile(const QString &fileName) {

	QApplication::setOverrideCursor(Qt::WaitCursor);
	
	// Read file
	NXCommandResult* commandResult =
		entityManager->importFromFile(qPrintable(fileName));
	QApplication::restoreOverrideCursor();
	
	bool success = true;
	if (commandResult->getResult() != NX_CMD_SUCCESS) {
		QFileInfo fileInfo(fileName);
		QString message =
			tr("Unable to open file: %1").arg(fileInfo.fileName());
		ErrorDialog errorDialog(message, commandResult);
		errorDialog.exec();
		success = false;
		
	} else {
		setCurrentFile(fileName);

		//
		// Discover a store-not-complete trajectory frame set
		NXDataStoreInfo* dataStoreInfo = entityManager->getDataStoreInfo();
		int trajId = dataStoreInfo->getTrajectoryId("frame-set-1");
		TrajectoryGraphicsPane* trajPane = new TrajectoryGraphicsPane();
		trajPane->setEntityManager(entityManager);
		workspace->addWindow(trajPane);
		trajPane->show();
		if (!dataStoreInfo->storeIsComplete(trajId)) {
			QObject::connect(entityManager,
							 SIGNAL(newFrameAdded(int, int, NXMoleculeSet*)),
							 trajPane,
							 SLOT(newFrame(int, int, NXMoleculeSet*)));
		}
	
/* MDI data window example
	DataWindow *child = new DataWindow;
	workspace->addWindow(child);
	child->show();
*/
		// Floating data window example
		ViewParametersWindow* viewParametersWindow =
			new ViewParametersWindow(dataStoreInfo->getInputParameters(), this);
		viewParametersWindow->show();
		
		QString message = tr("File loaded: %1").arg(fileName);
		NXLOG_INFO("ResultsWindow", qPrintable(message));
	}
	delete commandResult;
	return success;
}


/* FUNCTION: userFriendlyCurrentFile */
QString ResultsWindow::userFriendlyCurrentFile() {
	return strippedName(curFile);
}


/* FUNCTION: setCurrentFile */
void ResultsWindow::setCurrentFile(const QString &fileName) {
	curFile = QFileInfo(fileName).canonicalFilePath();
	setWindowTitle(userFriendlyCurrentFile() + "[*]");
}


/* FUNCTION: strippedName */
QString ResultsWindow::strippedName(const QString &fullFileName) {
	return QFileInfo(fullFileName).fileName();
}


/* FUNCTION: activeDataWindow */
DataWindow* ResultsWindow::activeDataWindow() {
	return qobject_cast<DataWindow *>(workspace->activeWindow());
}


/* FUNCTION: createResultsWindow */
DataWindow* ResultsWindow::createDataWindow() {
	DataWindow* window = new DataWindow;
	workspace->addWindow(window);

	return window;
}

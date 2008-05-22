// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include "ResultsWindow.h"
#include <QFileInfo>
#include <cassert>

#include "Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRenderer.h"

/* CONSTRUCTOR */
ResultsWindow::ResultsWindow(NXEntityManager* entityManager,
                             NXGraphicsManager* graphicsManager,
                             QWidget* parent)
: QWidget(parent), Ui_ResultsWindow(),
workspace(NULL),		windowMapper(NULL),
entityManager(NULL),	graphicsManager(NULL),
curFile(),     resultsTree(NULL),
resultsTreeIcon(		tr(":/Icons/results_tree.png")),
nh5FileIcon(			tr(":/Icons/nh5_file.png")),
mmpFileIcon(			tr(":/Icons/nanoENGINEER-1.ico")),
atomIcon(				tr(":/Icons/atom.png")),
atomSetIcon(			tr(":/Icons/atom_set.png")),
inputParametersIcon(	tr(":/Icons/input_parameters.png")),
inputFilesIcon(			tr(":/Icons/input_files.png")),
inputFileIcon(			tr(":/Icons/input_file.png")),
resultsIcon(			tr(":/Icons/results.png")),
resultsTrajectoriesIcon(tr(":/Icons/trajectories.png"))
{
	this->entityManager = entityManager;
	this->graphicsManager = graphicsManager;
	
	setupUi(this);
	
	workspace = new QWorkspace();
	connect(workspace, SIGNAL(windowActivated(QWidget *)),
	        parent, SLOT(updateMenus()));
	windowMapper = new QSignalMapper(this);
	connect(windowMapper, SIGNAL(mapped(QWidget *)),
	        workspace, SLOT(setActiveWindow(QWidget *)));
	
    // Create empty results-tree
    resultsTree = new QTreeWidget(tabWidget);
    resultsTree->setHeaderLabel(tr(""));
    tabWidget->removeTab(0);
    tabWidget->insertTab(0, resultsTree, resultsTreeIcon, "");
    
    splitter->insertWidget(1, workspace);
    delete widget;
}


/* DESTRUCTOR */
ResultsWindow::~ResultsWindow() {
	workspace->closeAllWindows();
	closeFile();
	if (activeDataWindow()) {
		; // Can't delete?
	}
}


/* FUNCTION: closeFile */
bool ResultsWindow::closeFile(void)
{
	QWidget *tab1Widget = tabWidget->widget(0);
	resultsTree = dynamic_cast<QTreeWidget*>(tab1Widget);
	resultsTree->clear();
	resultsTree->setHeaderLabel(tr(""));
	entityManager->reset();
	NXLOG_INFO("ResultsWindow", string("closed ") + qPrintable(curFile));
	return true;
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
		
        // Populate results tree
		setupResultsTree();
		
		QString message = tr("File loaded: %1").arg(fileName);
		NXLOG_INFO("ResultsWindow", qPrintable(message));
	}
	// delete commandResult; - commandResult now member of importer
	return success;
}


/* FUNCTION: setupResultsTree */
void ResultsWindow::setupResultsTree(void)
{
	NXDataStoreInfo* dataStoreInfo = entityManager->getDataStoreInfo();
    // MMP or OpenBabel file import
	if (dataStoreInfo->isSingleStructure()) {
		setupSingleStructureTree();
	}
    // Simulation results import
	else if (dataStoreInfo->isSimulationResults()) {
		setupSimulationResultsTree();
	}
	
	resultsTree->resizeColumnToContents(0);
	
	connect(resultsTree,
	        SIGNAL(itemDoubleClicked(QTreeWidgetItem*, int)),
	        this,
	        SLOT(resultsTreeItemDoubleClicked(QTreeWidgetItem*, int)));
}


/* FUNCTION: isMMPFile */
bool ResultsWindow::isMMPFile(string const& filename)
{
	QFileInfo fileInfo(filename.c_str());
	bool result =
		(fileInfo.suffix().compare(tr("mmp"), Qt::CaseInsensitive) == 0);
	return result;
}


/* FUNCTION: setupSimulationResultsTree */
void ResultsWindow::setupSimulationResultsTree(void)
{
    NXDataStoreInfo *dataStoreInfo = entityManager->getDataStoreInfo();
    QWidget *tab1Widget = tabWidget->widget(0);
    resultsTree = dynamic_cast<QTreeWidget*>(tab1Widget);
    resultsTree->clear();
	QTreeWidgetItem* rootNode = new QTreeWidgetItem(resultsTree);
	rootNode->setText(0, userFriendlyCurrentFile());
	rootNode->setIcon(0, nh5FileIcon);
	rootNode->setFlags(Qt::ItemIsEnabled);
	rootNode->setExpanded(true);
	resultsTree->addTopLevelItem(rootNode);
    
    // input parameters
	NXProperties *inputParameters = dataStoreInfo->getInputParameters();
	if (inputParameters != NULL) {
		DataWindowTreeItem* inputParametersItem =
			new InputParametersTreeItem(this, rootNode);
		inputParametersItem->setIcon(0, inputParametersIcon);
		inputParametersItem->setText(0, tr("Input parameters"));
		inputParametersItem->setFlags(Qt::ItemIsSelectable | Qt::ItemIsEnabled);
    }
    
    // input files
    vector<string> inputFileNames = dataStoreInfo->getInputFileNames();
    if (inputFileNames.size() > 0) {
        QTreeWidgetItem *inputFilesItem = new QTreeWidgetItem(rootNode);
        inputFilesItem->setIcon(0, inputFilesIcon);
        inputFilesItem->setText(0, tr("Input files"));
		inputFilesItem->setFlags(Qt::ItemIsEnabled);
		inputFilesItem->setExpanded(true);
        
        vector<string>::const_iterator inputFileNameIter;
        for (inputFileNameIter = inputFileNames.begin();
            inputFileNameIter != inputFileNames.end();
            ++inputFileNameIter)
        {
            QTreeWidgetItem *inputFileItem = new QTreeWidgetItem(inputFilesItem);
            inputFileItem->setIcon(0, inputFileIcon);
            inputFileItem->setText
				(0, strippedName(QString(inputFileNameIter->c_str())));
			inputFileItem->setFlags(Qt::ItemIsEnabled);
            // inputFilesItem->addChild(inputFileItem);
			
			if(isMMPFile(*inputFileNameIter)) {
				int mmpFileFrameSetId = 
					dataStoreInfo->getInputStructureId(*inputFileNameIter);
				if (mmpFileFrameSetId > -1) {
					NXMoleculeSet *rootMoleculeSet = 
						entityManager->getRootMoleculeSet(mmpFileFrameSetId, 0);
					setupMoleculeSetResultsSubtree(rootMoleculeSet,
					                               inputFileItem);
				} else {
                    // TODO: handle this
				}
            }

        }
    }
    
    // Results
	
	NXProperties *resultsSummary = dataStoreInfo->getResultsSummary();
	vector<string> trajectoryNames = dataStoreInfo->getTrajectoryNames();
	
    // don't create if no children
    if (resultsSummary == NULL && trajectoryNames.size()==0) return;
    
    QTreeWidgetItem *resultsItem = new QTreeWidgetItem(rootNode);
    resultsItem->setIcon(0, resultsIcon);
    resultsItem->setText(0, tr("Results"));
	resultsItem->setFlags(Qt::ItemIsEnabled);
	resultsItem->setExpanded(true);
    
    // Results -> Summary
	DataWindowTreeItem* resultsSummaryItem = NULL;
	if (resultsSummary != NULL) {
		resultsSummaryItem = new ResultsSummaryTreeItem(this, resultsItem);
		resultsSummaryItem->setText(0, tr("Summary"));
		resultsSummaryItem->setFlags(Qt::ItemIsSelectable | Qt::ItemIsEnabled);
	}
	
    // Results -> Trajectories
	if (trajectoryNames.size() > 0) {
		QTreeWidgetItem *trajectoryItem = new QTreeWidgetItem(resultsItem);
		trajectoryItem->setIcon(0, resultsTrajectoriesIcon);
		trajectoryItem->setText(0, tr("Trajectories"));
		trajectoryItem->setFlags(Qt::ItemIsEnabled);
		trajectoryItem->setExpanded(true);
        
        vector<string>::const_iterator trajectoryNameIter;
        for (trajectoryNameIter = trajectoryNames.begin();
            trajectoryNameIter != trajectoryNames.end();
            ++trajectoryNameIter)
        {
            TrajectoryGraphicsTreeItem* trajectoryNameItem =
                new TrajectoryGraphicsTreeItem(*trajectoryNameIter,
											   this,
											   trajectoryItem);
            trajectoryNameItem->setIcon(0, resultsTrajectoriesIcon);
            trajectoryNameItem->setText(0, QString(trajectoryNameIter->c_str()));
			trajectoryNameItem->setFlags(Qt::ItemIsSelectable |
			                             Qt::ItemIsEnabled);
            // trajectoryItem->addChild(trajectoryNameItem);
			
            // Show some graphics right away
			if (trajectoryNameIter == trajectoryNames.begin())
				trajectoryNameItem->showWindow();
			
            // Signal the results summary window once the data store is
            // complete so it can refresh itself
			int trajectoryId =
				dataStoreInfo->getTrajectoryId(*trajectoryNameIter);
			if ((resultsSummaryItem != NULL) &&
			    (!dataStoreInfo->storeIsComplete(trajectoryId)))
			{
				/// @todo: This code will need to be a little smarter once we support multiple
				/// trajectories and such. As it stands, it would make multiple identical signal-
				/// slot connections.
				
				    QObject::connect(entityManager,
				                     SIGNAL(dataStoreComplete()),
				                     resultsSummaryItem,
				                     SLOT(refresh()));
				    ((ResultsSummaryTreeItem*)resultsSummaryItem)
					    ->setTrajectoryId(trajectoryId);
				    resultsSummaryItem->refresh();
			    }
		}
	}
}

#if 0
/* FUNCTION: setupMoleculeSetResultsSubtree */
void
ResultsWindow::
setupMoleculeSetResultsSubtree(QTreeWidgetItem *const mmpFileItem)
{
    NXDataStoreInfo *const dataStoreInfo = entityManager->getDataStoreInfo();
    int frameSetID = dataStoreInfo->getSingleStructureId();
    NXMoleculeSet *rootMoleculeSet = 
        entityManager->getRootMoleculeSet(frameSetID, 0);

    setupMoleculeSetResultsSubtree_helper(rootMoleculeSet, mmpFileItem);
}
#endif

/* FUNCTION: setupMoleculeSetResultsSubtree */
StructureGraphicsTreeItem*
ResultsWindow::
setupMoleculeSetResultsSubtree(NXMoleculeSet *molSetPtr,
                               QTreeWidgetItem *const parentItem)
{
    StructureGraphicsTreeItem *molSetItem =
        new StructureGraphicsTreeItem(molSetPtr, this, parentItem);
    molSetItem->setIcon(0, atomSetIcon);
    molSetItem->setText(0, (molSetPtr->getTitle()).c_str());
    molSetItem->setFlags(Qt::ItemIsEnabled | Qt::ItemIsSelectable);
/*    QObject::connect((QTreeWidget*) molSetItem,
                     SIGNAL(itemDoubleClicked(QTreeWidgetItem*, int)),
                     this,
                     SLOT(resultsTreeItemDoubleClicked(QTreeWidgetItem*, int)));*/
	
	OBMolIterator molIter;
	for(molIter = molSetPtr->moleculesBegin();
	    molIter != molSetPtr->moleculesEnd();
	    ++molIter)
	{
		OBMol *molPtr = *molIter;
		QTreeWidgetItem *molItem =
			new StructureGraphicsTreeItem(molPtr, this, molSetItem);
		molItem->setIcon(0,atomIcon);
		molItem->setText(0, tr(molPtr->GetTitle()));
		molItem->setFlags(Qt::ItemIsEnabled | Qt::ItemIsSelectable);
    }
    
    NXMoleculeSetIterator childMolSetIter;
    for(childMolSetIter = molSetPtr->childrenBegin();
        childMolSetIter != molSetPtr->childrenEnd();
        ++childMolSetIter)
    {
        NXMoleculeSet *childMolSetPtr = *childMolSetIter;
        
/*        QTreeWidgetItem * childMolSetNode =
            new StructureGraphicsTreeItem(this, molSetItem, childMolSetPtr);
        childMolSetNode->setIcon(0, atomSetIcon);
        char const *const childMolSetTitle =
            (childMolSetPtr->getTitle()).c_str();
        childMolSetNode->setText(0, tr(childMolSetTitle));
        childMolSetNode->setFlags(Qt::ItemIsEnabled);*/
	    (void) setupMoleculeSetResultsSubtree(childMolSetPtr, molSetItem);
	}
	
	return molSetItem;
}


/* FUNCTION: setupSingleStructureTree */
void ResultsWindow::setupSingleStructureTree(void)
{
    NXDataStoreInfo *const dataStoreInfo = entityManager->getDataStoreInfo();
    QWidget *tab1Widget = tabWidget->widget(0);
    resultsTree = dynamic_cast<QTreeWidget*>(tab1Widget);
    resultsTree->clear();
    
    string const& singleStructureFileName =
        dataStoreInfo->getSingleStructureFileName();
    QString const fileFullPath(singleStructureFileName.c_str());
    QFileInfo fileInfo(fileFullPath);
    QString const fileName = fileInfo.fileName();
    QTreeWidgetItem *fileItem = new QTreeWidgetItem(resultsTree);
    fileItem->setIcon(0, inputFileIcon);
    fileItem->setText(0, fileName);
	fileItem->setFlags(Qt::ItemIsEnabled);
    resultsTree->addTopLevelItem(fileItem);
    
    if(isMMPFile(singleStructureFileName)) {
        int frameSetID = dataStoreInfo->getSingleStructureId();
        NXMoleculeSet *rootMoleculeSet = 
            entityManager->getRootMoleculeSet(frameSetID, 0);
	    assert(rootMoleculeSet != 0);
	    StructureGraphicsTreeItem *rootMoleculeSetItem =
		    setupMoleculeSetResultsSubtree(rootMoleculeSet, fileItem);
	    // show top-level group right away
	    if(rootMoleculeSetItem != NULL)
		    rootMoleculeSetItem->showWindow();
    
	    if(dataStoreInfo->hasClipboardStructure()) {
		    NXMoleculeSet *clipboardGroup =
			    dataStoreInfo->getClipboardStructure();
		    assert(clipboardGroup != NULL);
		    setupMoleculeSetResultsSubtree(clipboardGroup, fileItem);
	    }
    }
}


/* FUNCTION: userFriendlyCurrentFile */
QString ResultsWindow::userFriendlyCurrentFile() {
	if (entityManager->getDataStoreInfo()->isSingleStructure())
		return strippedName(curFile);
	
	else {
		// TODO: Make this not HDF5_SimResults-specific
		QString filename = curFile;
		filename.remove(filename.lastIndexOf("/"), 16);
		filename.remove(0, filename.lastIndexOf("/") + 1);
		return filename;
	}
}


/* FUNCTION: setCurrentFile */
void ResultsWindow::setCurrentFile(const QString &fileName) {
	curFile = QFileInfo(fileName).absoluteFilePath();
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


/* FUNCTION: resultsTreeItemDoubleClicked */
void ResultsWindow::resultsTreeItemDoubleClicked(QTreeWidgetItem* treeItem,
                                                 int /*column*/) {
	if ((treeItem != NULL) && (treeItem->flags() & Qt::ItemIsSelectable))
		((DataWindowTreeItem*)treeItem)->showWindow();
}


/* ************************ DataWindowTreeItem ************************ */


/* CONSTRUCTORS */
DataWindowTreeItem::DataWindowTreeItem(ResultsWindow* resultsWindow,
                                       QTreeWidget* treeWidget)
: QTreeWidgetItem(treeWidget) {
	this->resultsWindow = resultsWindow;
}
DataWindowTreeItem::DataWindowTreeItem(ResultsWindow* resultsWindow,
                                       QTreeWidgetItem* treeWidgetItem)
: QTreeWidgetItem(treeWidgetItem) {
	this->resultsWindow = resultsWindow;
}


/* DESTRUCTOR */
DataWindowTreeItem::~DataWindowTreeItem() {
}


/* FUNCTION: refresh */
void DataWindowTreeItem::refresh() { }


/* ************************ InputParametersTreeItem ************************ */


/* CONSTRUCTOR */
InputParametersTreeItem::InputParametersTreeItem(ResultsWindow* resultsWindow,
												 QTreeWidgetItem* treeWidgetItem)
		: DataWindowTreeItem(resultsWindow, treeWidgetItem) {
	inputParametersWindow = NULL;
}


/* DESTRUCTOR */
InputParametersTreeItem::~InputParametersTreeItem() {
	if (inputParametersWindow != NULL)
		delete inputParametersWindow;
}


/* FUNCTION: showWindow */
void InputParametersTreeItem::showWindow() {
	if (inputParametersWindow == NULL) {
		NXDataStoreInfo* dataStoreInfo =
			resultsWindow->entityManager->getDataStoreInfo();
		inputParametersWindow =
			new InputParametersWindow(resultsWindow->userFriendlyCurrentFile(),
			                          dataStoreInfo->getInputParameters());
	}
	inputParametersWindow->show();
}


/* ************************ ResultsSummaryTreeItem ************************ */


/* CONSTRUCTOR */
ResultsSummaryTreeItem::ResultsSummaryTreeItem(ResultsWindow* resultsWindow,
                                               QTreeWidgetItem* treeWidgetItem)
: DataWindowTreeItem(resultsWindow, treeWidgetItem),
resultsSummaryIcon(tr(":/Icons/results_summary.png")),
resultsSummaryIcon2(tr(":/Icons/results_summary2.png")) {
	
	trajectoryId = -1;
	resultsSummaryWindow = NULL;
	setIcon(0, resultsSummaryIcon);
}


/* DESTRUCTOR */
ResultsSummaryTreeItem::~ResultsSummaryTreeItem() {
	if (resultsSummaryWindow != NULL)
		delete resultsSummaryWindow;
}


/* FUNCTION: showWindow */
void ResultsSummaryTreeItem::showWindow() {
	if (resultsSummaryWindow == NULL) {
		NXDataStoreInfo* dataStoreInfo =
			resultsWindow->entityManager->getDataStoreInfo();
		resultsSummaryWindow =
			new ResultsSummaryWindow(resultsWindow->userFriendlyCurrentFile(),
			                         dataStoreInfo);
	}
	resultsSummaryWindow->show();
}


/* FUNCTION: refresh */
void ResultsSummaryTreeItem::refresh() {
	if (resultsSummaryWindow != NULL)
		resultsSummaryWindow->refresh();
	
	if ((trajectoryId != -1) &&
	    !resultsWindow->entityManager->getDataStoreInfo()
	    ->storeIsComplete(trajectoryId))
		setIcon(0, resultsSummaryIcon2);
	else
		setIcon(0, resultsSummaryIcon);
}


/* *********************** StructureGraphicsTreeItem *********************** */

/* CONSTRUCTOR */
StructureGraphicsTreeItem::StructureGraphicsTreeItem
(NXMoleculeSet* theMolSetPtr,
 ResultsWindow* theResultsWindow,
 QTreeWidgetItem* treeWidgetItem)
: DataWindowTreeItem(resultsWindow, treeWidgetItem),
molSetPtr(theMolSetPtr),
resultsWindow(theResultsWindow),
deleteOnDestruct(false),
structureWindow(NULL)
{
}


/* CONSTRUCTOR */
StructureGraphicsTreeItem::StructureGraphicsTreeItem
(OBMol* theMolPtr,
 ResultsWindow* theResultsWindow,
 QTreeWidgetItem* treeWidgetItem)
: DataWindowTreeItem(resultsWindow, treeWidgetItem),
molSetPtr(NULL),
resultsWindow(theResultsWindow),
deleteOnDestruct(true),
structureWindow(NULL)
{
	// Encapsulate molecule in a non-destructive molecule-set
	molSetPtr = new NXMoleculeSet(false);
	molSetPtr->addMolecule(theMolPtr);
	molSetPtr->setTitle(theMolPtr->GetTitle());
}


/* DESTRUCTOR */
StructureGraphicsTreeItem::~StructureGraphicsTreeItem() {
	if(deleteOnDestruct)
		delete molSetPtr;
	if (structureWindow != NULL)
		delete structureWindow;
}


/* FUNCTION: showWindow */
void StructureGraphicsTreeItem::showWindow()
{
// 	QWidget *activeWidget = resultsWindow->workspace->activeWindow();
// 	bool activeWidgetIsMaximized =
// 		(activeWidget != 0) && (activeWidget->isMaximized());
// 	if(activeWidgetIsMaximized)
// 		activeWidget->showNormal();
	
	if (structureWindow == NULL) {
		
		structureWindow =
			new StructureGraphicsWindow(NULL,
			                            resultsWindow->graphicsManager);
		/// @fixme - trap errors
		assert(structureWindow != NULL);
		// re-parent and display
		structureWindow->setWindowTitle(QString((molSetPtr->getTitle()).c_str()));
		structureWindow->show(); // creates OpenGL context
		
		NXCommandResult const *const addMolSetFrameResult =
			structureWindow->setMoleculeSet(molSetPtr);
		// structureWindow->show();
		
		if(addMolSetFrameResult->getResult() != (int) NX_CMD_SUCCESS) {
			ostringstream logMsgStream;
			logMsgStream << "Molecule(set) couldn't be drawn";
			vector<QString> const& msgs =
				addMolSetFrameResult->getParamVector();
			vector<QString>::const_iterator msgIter;
			for(msgIter = msgs.begin(); msgIter != msgs.end(); ++msgIter) {
				logMsgStream << ": " << qPrintable(*msgIter);
			}
			NXLOG_SEVERE("StructureGraphicsWindow", logMsgStream.str());
		}
		
		// set initial view
		NXEntityManager *entityManager = resultsWindow->entityManager;
		NXDataStoreInfo *dataStoreInfo = entityManager->getDataStoreInfo();

		if(dataStoreInfo->hasLastView()) {
			NXNamedView lastView = dataStoreInfo->getLastView();
			structureWindow->setNamedView(lastView);
			NXLOG_DEBUG("StructureGraphicsWindow", "Setting NE1 last-view");
			cerr << "StructureGraphicsWindow: Setting NE1 last-view\n\t"
				<< lastView << endl;
		}
		else if(dataStoreInfo->hasHomeView()) {
			NXNamedView homeView = dataStoreInfo->getHomeView();
			structureWindow->setNamedView(homeView);
			NXLOG_DEBUG("StructureGraphicsWindow", "Setting NE1 home-view");
			cerr << "StructureGraphicsWindow Setting NE1 home-view\n\t"
				<< homeView << endl;
		}
		else {
			structureWindow->resetView();
			NXLOG_DEBUG("StructureGraphicsWindow",
			            "Inferring default view from atom layout");
			cerr << "StructureGraphicsWindow: Inferring default view from atom layout"<< endl;
		}
		resultsWindow->workspace->addWindow((DataWindow*) structureWindow);
		structureWindow->show();
		// resultsWindow->workspace->setActiveWindow((DataWindow*)structureWindow);
		// structureWindow->move(QPoint(10,10));
		// structureWindow->resize((resultsWindow->workspace->size()) *= 0.75);
		// resultsWindow->workspace->update(); // structureWindow->show();
	}
	else
		structureWindow->show();
	
// 	if(activeWidgetIsMaximized)
// 		structureWindow->showMaximized();
// 	else
// 		structureWindow->showNormal();
	
	
	// structureWindow->update();
}



/* *********************** TrajectoryGraphicsTreeItem *********************** */


/* CONSTRUCTOR */
TrajectoryGraphicsTreeItem::
TrajectoryGraphicsTreeItem(const string& trajName,
                           ResultsWindow* theResultsWindow,
                           QTreeWidgetItem* treeWidgetItem)
: DataWindowTreeItem(resultsWindow, treeWidgetItem),
trajectoryName(trajName),
resultsWindow(theResultsWindow),
trajWindow(NULL)
{
}


/* DESTRUCTOR */
TrajectoryGraphicsTreeItem::~TrajectoryGraphicsTreeItem() {
	if (trajWindow != NULL)
		delete trajWindow;
}


/* FUNCTION: showWindow */
void TrajectoryGraphicsTreeItem::showWindow()
{
	QWidget *activeWidget = resultsWindow->workspace->activeWindow();
	bool activeWidgetIsMaximized =
		(activeWidget != 0) && (activeWidget->isMaximized());
	if(activeWidgetIsMaximized)
		activeWidget->showNormal();
	
	if (trajWindow == NULL) {
		NXEntityManager* entityManager = resultsWindow->entityManager;
		NXDataStoreInfo* dataStoreInfo = entityManager->getDataStoreInfo();
		NXGraphicsManager* graphicsManager = resultsWindow->graphicsManager;
		
		int trajId = dataStoreInfo->getTrajectoryId(trajectoryName);
		trajWindow =
			new TrajectoryGraphicsWindow((QWidget*)0,
			                             entityManager,
			                             graphicsManager);
		/// @fixme Trap errors
		resultsWindow->workspace->addWindow(trajWindow);
		
		trajWindow->resize((resultsWindow->workspace->size()) *= 0.75);
		trajWindow->setWindowTitle(QString(trajectoryName.c_str()));
		
		resultsWindow->workspace->setActiveWindow(trajWindow);
		trajWindow->show();
		
		trajWindow->setFrameSetId(trajId);
		
		// set initial view
		if(dataStoreInfo->hasLastView()) {
			NXNamedView const& lastView = dataStoreInfo->getLastView();
			trajWindow->setNamedView(lastView);
			NXLOG_DEBUG("TrajectoryGraphicsWindow", "Setting NE1 last-view");
		}
		else if(dataStoreInfo->hasHomeView()) {
			NXNamedView const& homeView = dataStoreInfo->getHomeView();
			trajWindow->setNamedView(homeView);
			NXLOG_DEBUG("TrajectoryGraphicsWindow", "Setting NE1 home-view");
		}
		else {
			trajWindow->resetView();
			NXLOG_DEBUG("TrajectoryGraphicsWindow",
			            "Inferring default view from atom layout");
		}
		
		if (!dataStoreInfo->storeIsComplete(trajId)) {
			QObject::connect(entityManager,
			                 SIGNAL(newFrameAdded(int, int, NXMoleculeSet*)),
			                 trajWindow,
			                 SLOT(newFrame(int, int, NXMoleculeSet*)));
		}
		// resultsWindow->workspace->update();
	}
// 	else
// 		trajWindow->show();
	
	if(activeWidgetIsMaximized)
		trajWindow->showMaximized();
	else
		trajWindow->showNormal();
	
}


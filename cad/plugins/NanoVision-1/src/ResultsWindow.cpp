// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include "ResultsWindow.h"
#include <QFileInfo>
#include <cassert>

#include "Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRenderer.h"

/* CONSTRUCTOR */
ResultsWindow::ResultsWindow(NXEntityManager* entityManager, QWidget* parent)
: QWidget(parent), Ui_ResultsWindow(),
    workspace(NULL),		windowMapper(NULL),
    entityManager(NULL),	curFile(),     resultsTree(NULL),
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
    tabWidget->insertTab(0,resultsTree,tr("Results Tree"));
    
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
    delete commandResult;
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
    resultsTree->setHeaderLabel("Sim Results");
    
    // input parameters
    NXProperties *inputParameters = dataStoreInfo->getInputParameters();
    if (inputParameters != NULL) {
        DataWindowTreeItem* inputParametersItem =
			new InputParametersTreeItem(this, resultsTree);
        inputParametersItem->setIcon(0, inputParametersIcon);
        inputParametersItem->setText(0, tr("Input parameters"));
		inputParametersItem->setFlags(Qt::ItemIsSelectable | Qt::ItemIsEnabled);
        resultsTree->addTopLevelItem(inputParametersItem);
    }
    
    // input files
    vector<string> inputFileNames = dataStoreInfo->getInputFileNames();
    if (inputFileNames.size() > 0) {
        QTreeWidgetItem *inputFilesItem = new QTreeWidgetItem(resultsTree);
        inputFilesItem->setIcon(0, inputFilesIcon);
        inputFilesItem->setText(0, tr("Input files"));
		inputFilesItem->setFlags(Qt::ItemIsEnabled);
        
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
        
        resultsTree->addTopLevelItem(inputFilesItem);
    }
    
    // Results
    
    NXProperties *resultsSummary = dataStoreInfo->getResultsSummary();
    vector<string> trajectoryNames = dataStoreInfo->getTrajectoryNames();
    
    // don't create if no children
    if (resultsSummary == NULL && trajectoryNames.size()==0) return;
    
    QTreeWidgetItem *resultsItem = new QTreeWidgetItem(resultsTree);
    resultsItem->setIcon(0, resultsIcon);
    resultsItem->setText(0, tr("Results"));
	resultsItem->setFlags(Qt::ItemIsEnabled);
    resultsTree->addTopLevelItem(resultsItem);
    
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
				(!dataStoreInfo->storeIsComplete(trajectoryId))) {
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
void
ResultsWindow::
setupMoleculeSetResultsSubtree(NXMoleculeSet *molSetPtr,
                               QTreeWidgetItem *const parentItem)
{
    StructureGraphicsTreeItem *molSetItem =
        new StructureGraphicsTreeItem(molSetPtr, this, parentItem);
    molSetItem->setIcon(0, atomSetIcon);
    molSetItem->setText(0, (molSetPtr->getTitle()).c_str());
    molSetItem->setFlags(Qt::ItemIsEnabled);
    molSetItem->setFlags(Qt::ItemIsSelectable);
    
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
		molItem->setFlags(Qt::ItemIsEnabled);
        molItem->setFlags(Qt::ItemIsSelectable);
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
        setupMoleculeSetResultsSubtree(childMolSetPtr, molSetItem);
    }
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
    fileItem->setIcon(0, mmpFileIcon);
    fileItem->setText(0, fileName);
	fileItem->setFlags(Qt::ItemIsEnabled);
    resultsTree->addTopLevelItem(fileItem);
    QString const fileSuffix = fileInfo.suffix();
    resultsTree->setHeaderLabel(fileSuffix.toUpper() + " file");
    
    if(isMMPFile(singleStructureFileName)) {
        int frameSetID = dataStoreInfo->getSingleStructureId();
        NXMoleculeSet *rootMoleculeSet = 
            entityManager->getRootMoleculeSet(frameSetID, 0);
        setupMoleculeSetResultsSubtree(rootMoleculeSet, fileItem);
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
												 QTreeWidget* treeWidget)
		: DataWindowTreeItem(resultsWindow, treeWidget) {
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
(NXMoleculeSet *_molSetPtr,
 ResultsWindow* resultsWindow,
 QTreeWidgetItem* treeWidgetItem)
: DataWindowTreeItem(resultsWindow, treeWidgetItem),
molSetPtr(_molSetPtr),
molPtr(NULL),
isSingleMolecule(false),
structureWindow(NULL)
{
}


/* CONSTRUCTOR */
StructureGraphicsTreeItem::StructureGraphicsTreeItem
(OBMol *_mol,
 ResultsWindow* resultsWindow,
 QTreeWidgetItem* treeWidgetItem)
: DataWindowTreeItem(resultsWindow, treeWidgetItem),
molSetPtr(NULL),
molPtr(_mol),
isSingleMolecule(true),
structureWindow(NULL)
{
}


/* DESTRUCTOR */
StructureGraphicsTreeItem::~StructureGraphicsTreeItem() {
    if (structureWindow != NULL)
        delete structureWindow;
}


/* FUNCTION: showWindow */
void StructureGraphicsTreeItem::showWindow() {
    if (structureWindow == NULL) {
        NXEntityManager* entityManager = resultsWindow->entityManager;
        // NXDataStoreInfo* dataStoreInfo = entityManager->getDataStoreInfo();
        // int structureId = dataStoreInfo->getStructureId(structureName);
        structureWindow = new StructureGraphicsWindow();
        assert(structureWindow != NULL);
        structureWindow->setRenderer(new NXBallAndStickOpenGLRenderer);
        if(isSingleMolecule)
            structureWindow->setMolecule(molPtr);
        else
            structureWindow->setRootMoleculeSet(molSetPtr);
        structureWindow->setEntityManager(entityManager);
        resultsWindow->workspace->addWindow((DataWindow*)structureWindow);
    }
    structureWindow->NXOpenGLRenderingEngine::show();
}



/* *********************** TrajectoryGraphicsTreeItem *********************** */


/* CONSTRUCTOR */
TrajectoryGraphicsTreeItem::TrajectoryGraphicsTreeItem
		(const string& trajectoryName,
		 ResultsWindow* resultsWindow,
		 QTreeWidgetItem* treeWidgetItem)
		: DataWindowTreeItem(resultsWindow, treeWidgetItem) {
	trajWindow = NULL;
	this->trajectoryName = trajectoryName;
}


/* DESTRUCTOR */
TrajectoryGraphicsTreeItem::~TrajectoryGraphicsTreeItem() {
	if (trajWindow != NULL)
		delete trajWindow;
}


/* FUNCTION: showWindow */
void TrajectoryGraphicsTreeItem::showWindow() {
	if (trajWindow == NULL) {
		NXEntityManager* entityManager = resultsWindow->entityManager;
		NXDataStoreInfo* dataStoreInfo = entityManager->getDataStoreInfo();
		int trajId = dataStoreInfo->getTrajectoryId(trajectoryName);
		trajWindow = new TrajectoryGraphicsWindow();
		trajWindow->setEntityManager(entityManager);
		resultsWindow->workspace->addWindow(trajWindow);
		if (!dataStoreInfo->storeIsComplete(trajId)) {
			QObject::connect(entityManager,
							 SIGNAL(newFrameAdded(int, int, NXMoleculeSet*)),
							 trajWindow,
							 SLOT(newFrame(int, int, NXMoleculeSet*)));
		}
	}
	trajWindow->show();
}


// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include "ResultsWindow.h"
#include <QFileInfo>

/* CONSTRUCTOR */
ResultsWindow::ResultsWindow(NXEntityManager* entityManager, QWidget* parent)
: QWidget(parent), Ui_ResultsWindow(),
    workspace(NULL), windowMapper(NULL), curFile(),
    entityManager(NULL), resultsTree(NULL),
    mmpFileIcon(tr(":/Icons/nanoENGINEER-1.ico")),
    atomIcon(tr(":/Icons/atom.png")),
    atomSetIcon(tr(":/Icons/atom_set.png")),
    inputParametersIcon(tr(":/Icons/input_parameters.png")),
    inputFilesIcon(tr(":/Icons/input_files.png")),
    inputFileIcon(tr(":/Icons/input_file.png")),
    resultsIcon(tr(":/Icons/results.png")),
    resultsSummaryIcon(tr(":/Icons/results_summary.png")),
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
        
        NXDataStoreInfo *dataStoreInfo = entityManager->getDataStoreInfo();
        
        // populate results tree
        updateResultsTree();
        
/*        // Discover a store-not-complete trajectory frame set
        int trajId = dataStoreInfo->getTrajectoryId("frame-set-1");
        TrajectoryGraphicsWindow* trajWindow = new TrajectoryGraphicsWindow();
        trajPane->setEntityManager(entityManager);
        workspace->addWindow(trajWindow);
        trajWindow->show();
        if (!dataStoreInfo->storeIsComplete(trajId)) {
            QObject::connect(entityManager,
                                SIGNAL(newFrameAdded(int, int, NXMoleculeSet*)),
                                trajWindow,
                                SLOT(newFrame(int, int, NXMoleculeSet*)));
        }*/
        
/* MDI data window example
    DataWindow *child = new DataWindow;
    workspace->addWindow(child);
    child->show();
*/
        // Floating data window example
        ViewParametersWindow* viewParametersWindow =
            new ViewParametersWindow(dataStoreInfo->getInputParameters(),
                                     (QWidget*)(parent()));
        viewParametersWindow->show();
        
        QString message = tr("File loaded: %1").arg(fileName);
        NXLOG_INFO("ResultsWindow", qPrintable(message));
    }
    delete commandResult;
    return success;
}


/* FUNCTION: updateResultsTree */
void ResultsWindow::updateResultsTree(void)
{
    NXDataStoreInfo* dataStoreInfo = entityManager->getDataStoreInfo();
    // MMP or OpenBabel file import
    if(dataStoreInfo->isSingleStructure()) {
        setupSingleStructureTree();
    }
    // Simulation results import
    else if(dataStoreInfo->isSimulationResults()) {
        setupSimulationResultsTree();
    }
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
        QTreeWidgetItem *inputParametersItem = new QTreeWidgetItem(resultsTree);
        inputParametersItem->setIcon(0, inputParametersIcon);
        inputParametersItem->setText(0, tr("Input parameters"));
        resultsTree->addTopLevelItem(inputParametersItem);
    }
    
    // input files
    vector<string> inputFileNames = dataStoreInfo->getInputFileNames();
    if (inputFileNames.size() > 0) {
        QTreeWidgetItem *inputFilesItem = new QTreeWidgetItem(resultsTree);
        inputFilesItem->setIcon(0, inputFilesIcon);
        inputFilesItem->setText(0, tr("Input files"));
        
        vector<string>::const_iterator inputFileIter;
        for (inputFileIter = inputFileNames.begin();
            inputFileIter != inputFileNames.end();
            ++inputFileIter)
        {
            QTreeWidgetItem *inputFileItem = new QTreeWidgetItem(inputFilesItem);
            inputFileItem->setIcon(0, inputFileIcon);
            inputFileItem->setText
				(0, strippedName(QString(inputFileIter->c_str())));
            // inputFilesItem->addChild(inputFileItem);
            
            if(isMMPFile(*inputFileIter))
                setupMoleculeSetResultsSubtree(inputFileItem);

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
    resultsTree->addTopLevelItem(resultsItem);
    
    // Results -> Summary
    QTreeWidgetItem *resultsSummaryItem = NULL;
    if (resultsSummary != NULL) {
        resultsSummaryItem = new QTreeWidgetItem(resultsItem);
        resultsSummaryItem->setIcon(0, resultsSummaryIcon);
        resultsSummaryItem->setText(0, tr("Summary"));
    }
    
    // Results -> Trajectories
    if (trajectoryNames.size() > 0) {
        QTreeWidgetItem *trajectoryItem = new QTreeWidgetItem(resultsItem);
        trajectoryItem->setIcon(0, resultsTrajectoriesIcon);
        trajectoryItem->setText(0, tr("Trajectories"));
        
        vector<string>::const_iterator trajectoryNameIter;
        for (trajectoryNameIter = trajectoryNames.begin();
            trajectoryNameIter != trajectoryNames.end();
            ++trajectoryNameIter)
        {
            QTreeWidgetItem *trajectoryNameItem =
                new QTreeWidgetItem(trajectoryItem);
            trajectoryNameItem->setIcon(0, resultsTrajectoriesIcon);
            trajectoryNameItem->setText(0, QString(trajectoryNameIter->c_str()));
            // trajectoryItem->addChild(trajectoryNameItem);
        }
    }
}


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


/* FUNCTION: setupMoleculeSetResultsSubtree_helper */
void
ResultsWindow::
setupMoleculeSetResultsSubtree_helper(NXMoleculeSet *molSetPtr,
                                      QTreeWidgetItem *const molSetItem)
{
    OBMolIterator molIter;
    for(molIter = molSetPtr->moleculesBegin();
        molIter != molSetPtr->moleculesEnd();
        ++molIter)
    {
        OBMol *molPtr = *molIter;
        QTreeWidgetItem *molItem = new QTreeWidgetItem(molSetItem);
        molItem->setIcon(0,atomIcon);
        molItem->setText(0, tr(molPtr->GetTitle()));
    }
    
    NXMoleculeSetIterator childMolSetIter;
    for(childMolSetIter = molSetPtr->childrenBegin();
        childMolSetIter != molSetPtr->childrenEnd();
        ++childMolSetIter)
    {
        NXMoleculeSet *childMolSetPtr = *childMolSetIter;
        QTreeWidgetItem * childMolSetNode = new QTreeWidgetItem(molSetItem);
        childMolSetNode->setIcon(0, atomSetIcon);
        char const *const childMolSetTitle =
            (childMolSetPtr->getTitle()).c_str();
        childMolSetNode->setText(0, tr(childMolSetTitle));
        setupMoleculeSetResultsSubtree_helper(childMolSetPtr, childMolSetNode);
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
    resultsTree->addTopLevelItem(fileItem);
    QString const fileSuffix = fileInfo.suffix();
    resultsTree->setHeaderLabel(fileSuffix.toUpper() + " file");
    
    if(isMMPFile(singleStructureFileName))
       setupMoleculeSetResultsSubtree(fileItem);
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

// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include "ResultsWindow.h"
#include <QFileInfo>

/* CONSTRUCTOR */
ResultsWindow::ResultsWindow(NXEntityManager* entityManager, QWidget* parent)
: QWidget(parent), Ui_ResultsWindow() {
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
        
        // populate results tree
        QWidget *tab1Widget = tabWidget->widget(0);
        resultsTree = dynamic_cast<QTreeWidget*>(tab1Widget);
        resultsTree->clear();
        NXDataStoreInfo* dataStoreInfo = entityManager->getDataStoreInfo();
        if(dataStoreInfo->isSingleStructure()) {
            // MMP or OpenBabel file import
            string const& singleStructureFileName =
                dataStoreInfo->getSingleStructureFileName();
            QString const fileFullPath(singleStructureFileName.c_str());
            QFileInfo fileInfo(fileFullPath);
            QString const fileName = fileInfo.fileName();
            QTreeWidgetItem *fileItem = new QTreeWidgetItem(resultsTree);
            QIcon fileIcon(tr(":/Icons/nanoENGINEER-1.ico"));
            fileItem->setIcon(0, fileIcon);
            fileItem->setText(0, fileName);
            resultsTree->addTopLevelItem(fileItem);
            QString const fileSuffix = fileInfo.suffix();
            resultsTree->setHeaderLabel(fileSuffix.toUpper() + " file");
        }
        else {
        // Discover a store-not-complete trajectory frame set
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
        }        
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

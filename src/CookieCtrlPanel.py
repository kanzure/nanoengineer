from qt import *
from Utility import imagename_to_pixmap
from constants import dispLabel

class CookieCtrlPanel(QObject):
       """This is class is served to provide GUI controls to the cookie-cutter mode. """
       
       def __init__(self, parent):
            """<parent> is the main window  for the program"""
            self.w = parent
            self._createDashBoard()
            
            self.actionNamesList = [(self.w.CircleSelAction,'CIRCLE'), (self.w.HexagonSelAction, 'HEXAGON'), (self.w.RectCtrSelAction, 'RECTANGLE'), (self.w.TriangleSelAction, 'TRIANGLE'), (self.w.LassoSelAction, 'LASSO'), (self.w.RectCornerSelAction, 'RECT_CORNER'), (self.w.SquareSelAction, 'SQUARE'), (self.w.DiamondSelAction, 'DIAMOND'), (self.w.DefaultSelAction, 'DEFAULT')]
       
            
       def _createDashBoard(self):
            """Programmably create the dashBoard, which is possibly not needed when the Qt designer is capable of doing sth that it can't right now. This is similar to a function 'do_what_MainWindowUI_should_do() ' used by other modes.  """
        
            self.w.cookieCutterDashboard.clear()
        
            self.w.cookieCutterDashboard.setEnabled(1)
            self.w.cookieCutterDashboard.setGeometry(QRect(0,0,1115,29))
            self.w.cookieCutterDashboard.setBackgroundOrigin(QToolBar.WidgetOrigin)

            #textLabel1 = QLabel("Cookie Cutter", self.w.cookieCutterDashboard,"textLabel1")
            
            #self.w.cookieCutterDashboard.addSeparator()

            latticeComponet = QVBox(self.w.cookieCutterDashboard)
            textLabel2 = QLabel("Lattice Type", latticeComponet, "textLabel2")
            self.latticeCBox = QComboBox(0, latticeComponet, "ccLatticeCBox")
            self.latticeCBox.insertItem("Diamond")
            self.latticeCBox.insertItem("Lonsdaleite")
        
            self.w.cookieCutterDashboard.addSeparator()
        
            
            self.orientButtonGroup = QButtonGroup(self.w.cookieCutterDashboard,"orientationButtonGroup")
            self.orientButtonGroup.setPaletteBackgroundColor(QColor(223,231,212))
            self.orientButtonGroup.setExclusive(1)
            self.orientButtonGroup.setColumnLayout(0,Qt.Vertical)
            self.orientButtonGroup.layout().setSpacing(1)
            self.orientButtonGroup.layout().setMargin(2)
            orientButtonGroupLayout = QGridLayout(self.orientButtonGroup.layout())
            orientButtonGroupLayout.setAlignment(Qt.AlignTop)
        
            tButton1 = QToolButton(self.orientButtonGroup,"orient100Button")
            tButton1.setToggleButton(1)
            tButton1.setOn(0)
            tButton1.setPixmap(imagename_to_pixmap('surface100-t.png'))
            QToolTip.add(tButton1,self.w.tr("Surface 100."))
            
            self.orientButtonGroup.insert( tButton1, 0)
            orientButtonGroupLayout.addWidget(tButton1, 0, 0)
            
            #tButton4 = QToolButton(self.orientButtonGroup,"orient100Button")
            #tButton4.setToggleButton(1)
            #tButton4.setOn(0)
            #tButton4.setEnabled(False)
            #tButton4.setPixmap(imagename_to_pixmap('surface100-t.png'))
            
            #self.orientButtonGroup.insert( tButton4, 3)
            #orientButtonGroupLayout.addWidget(tButton4, 0, 1)
            
            tButton2 = QToolButton(self.orientButtonGroup,"orient110Button")
            tButton2.setToggleButton(1)
            tButton2.setOn(0)
            tButton2.setPixmap(imagename_to_pixmap('surface110-t.png'))
            QToolTip.add(tButton2,self.w.tr("Surface 110."))
            
            self.orientButtonGroup.insert( tButton2, 1)
            orientButtonGroupLayout.addWidget(tButton1, 1,0)
            
            tButton3 = QToolButton(self.orientButtonGroup,"orient111Button")
            tButton3.setToggleButton(1)
            tButton3.setOn(0)
            tButton3.setPixmap(imagename_to_pixmap('surface111-t.png'))
            QToolTip.add(tButton3,self.w.tr("Surface 111."))
            
            self.orientButtonGroup.insert(tButton3, 2)
            orientButtonGroupLayout.addWidget(tButton3,1,1)
            
            self.w.cookieCutterDashboard.addSeparator()
        
            gridRotateComp = QVBox(self.w.cookieCutterDashboard)
            row1Comp = QHBox(gridRotateComp)
            
            self.antiRotateButton = QToolButton(row1Comp,"antiClockRotateButton")
            self.antiRotateButton.setPixmap(imagename_to_pixmap('angle-minus-t.png'))
            QToolTip.add(self.antiRotateButton,self.w.tr("Rotate anti-clockwisely."))
            
            self.rotateButton = QToolButton(row1Comp,"clockRotateButton")
            self.rotateButton.setPixmap(imagename_to_pixmap('angle-plus-t.png'))
            QToolTip.add(self.rotateButton,self.w.tr("Rotate clockwisely."))
            
            row2Comp = QHBox(gridRotateComp)
            self.gridRotateAngle = QSpinBox(0, 360, 5, row2Comp)
            QToolTip.add(self.gridRotateAngle,self.w.tr("Degrees to rotate."))
            
            
            self.w.cookieCutterDashboard.addSeparator()
            
            cookieLayerComp = QVBox(self.w.cookieCutterDashboard)
            row1Comp = QHBox(cookieLayerComp)
            self.addLayerButton = QPushButton("Add Layer", row1Comp,"addLayerButton")
            
            row2Comp = QHBox(cookieLayerComp)
            self.currentLayerCBox = QComboBox(0, row2Comp,"currentLayerCBox")
            QToolTip.add(self.currentLayerCBox,self.w.tr("Current Layer"))
            
            self.w.cookieCutterDashboard.addSeparator()
            
            thicknessComp = QVBox(self.w.cookieCutterDashboard)
            row1Comp = QHBox(thicknessComp)

            textLabel3 = QLabel("Thickness:", row1Comp,"textLabel3")
            self.layerThicknessLineEdit = QLineEdit(row1Comp,"layerThicknessLineEdit")
            self.layerThicknessLineEdit.setReadOnly(1)
            QToolTip.add(self.layerThicknessLineEdit,self.w.tr("Thickness of layer in Angstroms"))
            
            row2Comp = QHBox(thicknessComp)
            textLabel6 = QLabel("# of cells:", row2Comp, "textLabel6")

            self.layerCellsSpinBox = QSpinBox(row2Comp,"layerCellsSpinBox")
            self.layerCellsSpinBox.setMaxValue(25)
            self.layerCellsSpinBox.setMinValue(1)
            self.layerCellsSpinBox.setValue(2)
            QToolTip.add(self.layerCellsSpinBox,self.w.tr("Number of lattice cells"))
            
            self.w.cookieCutterDashboard.addSeparator()

            checkComp = QVBox(self.w.cookieCutterDashboard)
            row1Comp = QHBox(checkComp)

            self.freeViewCheckBox = QCheckBox("Free View", row1Comp,"freeViewCheckBox")
            QToolTip.add(self.freeViewCheckBox,self.w.tr("By checking it, you can view the cookie freely."))
            self.fullModelCheckBox = QCheckBox("Existing Model", row1Comp,"fullModelCheckBox")
            QToolTip.add(self.fullModelCheckBox,self.w.tr("Show or hide existing model."))
            
            row2Comp = QHBox(checkComp)
            self.gridLineCheckBox = QCheckBox("Grid Line", row2Comp,"gridLineCheckBox")
            self.gridLineCheckBox.setChecked(1)
            QToolTip.add(self.gridLineCheckBox,self.w.tr("Show or hide the grid line."))

            self.gridColorLabel = QLabel(self.w.cookieCutterDashboard,"gridColorLabel")
            self.gridColorLabel.setMinimumSize(QSize(0,0))
            self.gridColorLabel.setMaximumSize(QSize(0,0))
            self.gridColorLabel.setPaletteBackgroundColor(QColor(222,148,0))
            self.gridColorLabel.setFrameShape(QLabel.StyledPanel)

            self.gridColorButton = QPushButton(self.w.cookieCutterDashboard,"ccGridColorButton")
            self.gridColorButton.setMaximumSize(QSize(0,0))
            
            self.w.cookieCutterDashboard.addSeparator()

            dispComp = QVBox(self.w.cookieCutterDashboard)

            dispTextLabel = QLabel("Display Format", dispComp,"dispLabel")    
            self.dispModeCBox = QComboBox(0,dispComp,"dispModeCBox")
            self.dispModeCBox.insertItem("Tubes")
            self.dispModeCBox.insertItem("Spheres")
            
            self.w.cookieCutterDashboard.addSeparator()
            
            self.w.toolsBackUpAction.addTo(self.w.cookieCutterDashboard)
            self.w.toolsStartOverAction.addTo(self.w.cookieCutterDashboard)
            self.w.toolsDoneAction.addTo(self.w.cookieCutterDashboard)
            self.w.toolsCancelAction.addTo(self.w.cookieCutterDashboard)
        
            ##make connections
            self._makeConnections()
            
       def _makeConnections(self):
            """Connect signal to slots """
            self.connect(self.latticeCBox, SIGNAL("activated ( int )"), self.changeLatticeType)  
            
            self.connect(self.orientButtonGroup, SIGNAL("clicked(int)"), self.changeGridOrientation)
            
            self.connect(self.antiRotateButton, SIGNAL("clicked()"), self.antiRotateView)
            self.connect(self.rotateButton, SIGNAL("clicked()"), self.rotateView)
            
            self.connect(self.addLayerButton,SIGNAL("clicked()"), self.addLayer)
            self.connect(self.currentLayerCBox,SIGNAL("activated(int)"), self.changeLayer)
            
            self.connect(self.layerCellsSpinBox,SIGNAL("valueChanged(int)"), self.setThickness)
            
            self.connect(self.gridColorButton,SIGNAL("clicked()"),self.changeGridColor)
            self.connect(self.gridLineCheckBox,SIGNAL("toggled(bool)"),self.showGridLine)
            self.connect(self.freeViewCheckBox,SIGNAL("toggled(bool)"),self.setFreeView)
            self.connect(self.fullModelCheckBox, SIGNAL("toggled(bool)"),self.toggleFullModel)
            
            self.connect(self.dispModeCBox, SIGNAL("activated(const QString &)"), self.changeDispMode)
            
            self.connect(self.w.CookieSelectionGroup, SIGNAL("selected(QAction *)"),self.changeSelectionShape)
       
       
       def initGui(self):
            """This is used to initialize GUI items which needs to change every time when the mode is on. """
            self.w.glpane.setCursor(self.w.CookieAddCursor)
            self.w.toolsCookieCutAction.setOn(1) # toggle on the Cookie Cutter icon
            
            #Huaicai 3/29: Added the condition to fix bug 477
            self.w.dispbarLabel.setText("    ")
            
            self.latticeCBox.setEnabled(True)
            
            #Set projection to ortho, display them
            self.w.setViewOrthoAction.setOn(True)  
            self.w.setViewOrthoAction.setEnabled(False)
            self.w.setViewPerspecAction.setEnabled(False)
            
            self.layerCellsSpinBox.setValue(2)
            self.gridRotateAngle.setValue(45)
            
            self.currentLayerCBox.clear()
            self.currentLayerCBox.insertItem("1")#QString(str(len(self.layers[0]))))
            self.addLayerButton.setEnabled(False)
             
            self.w.cookieCutterDashboard.show()
            
            # Disable some action items in the main window.
            self.w.zoomToolAction.setEnabled(0) # Disable "Zoom Tool"
            self.w.panToolAction.setEnabled(0) # Disable "Pan Tool"
            self.w.rotateToolAction.setEnabled(0) # Disable "Rotate Tool"
            
            # Hide the some toolbars
            self.w.modifyToolbar.hide()
            self.w.simToolbar.hide()
            
            #Show the Cookie Selection Dashboard
            self.w.cookieSelectDashboard.show()  
       
       
       def restoreGui(self):
            """Restore GUI items when exit from the cookie-cutter mode. """
            self.w.cookieCutterDashboard.hide()
            
            self.w.zoomToolAction.setEnabled(1) # Enable "Zoom Tool"
            self.w.panToolAction.setEnabled(1) # Enable "Pan Tool"
            self.w.rotateToolAction.setEnabled(1) # Enable "Rotate Tool"
            
            #Hide the Cookie Selection Dashboard
            self.w.cookieSelectDashboard.hide()
            
            # Show those hidden toolbars
            self.w.modifyToolbar.show()
            self.w.simToolbar.show()
            
            #Restore display mode status message
            self.w.dispbarLabel.setText( "Default Display: " + dispLabel[self.w.glpane.display] )
            
            # Restore view projection, enable them.
            self.w.setViewOrthoAction.setEnabled(True)
            self.w.setViewPerspecAction.setEnabled(True)
            
            # Enable all those view options
            self.enableViewChanges(True)
       
       
       def enableViewChanges(self, enableFlag):
            """Turn on or off view changes depending on <param> 'enableFlag'. Turn off view changes is needed during the cookie-cutting stage. """
            
            self.orientButtonGroup.setEnabled(enableFlag)
            
            self.gridRotateAngle.setEnabled(enableFlag)
            self.antiRotateButton.setEnabled(enableFlag)
            self.rotateButton.setEnabled(enableFlag)
            
            self.w.setViewBackAction.setEnabled(enableFlag) 
            self.w.setViewBottomAction.setEnabled(enableFlag)
            self.w.setViewFitToWindowAction.setEnabled(enableFlag)
            self.w.setViewFrontAction.setEnabled(enableFlag)
            self.w.setViewHomeAction.setEnabled(enableFlag)
            self.w.setViewLeftAction.setEnabled(enableFlag)
            self.w.setViewRecenterAction.setEnabled(enableFlag)
            self.w.setViewRightAction.setEnabled(enableFlag)
            self.w.setViewTopAction.setEnabled(enableFlag)
                      
        
       def changeSelectionShape(self, action):
            """Slot method that is called when user changes selection shape by GUI. """
            for item in self.actionNamesList:
                if action == item[0]:
                    sShape = item[1]
                    self.w.glpane.mode.changeSelectionShape(sShape)
                    break
      
       def getSelectionShape(self):
            """Get the current selection shape that user chooses and returns it. """
            for item in self.actionNamesList:
                if item[0].isOn():
                    selectionShape = item[1]
                    break
            
            return selectionShape
   
       def setThickness(self, value):
          self.w.glpane.mode.setThickness(value)
          
       def addLayer(self):
            self.addLayerButton.setEnabled(False)
            layerId = self.w.glpane.mode.addLayer()
            
            self.currentLayerCBox.insertItem(QString(str(layerId)))
            self.currentLayerCBox.setCurrentItem(layerId-1)
            
            self.w.glpane.gl_update()

       def changeLayer(self, value):
            """Change current layer to <value> layer """
            self.w.glpane.mode.change2Layer(value)

       def setFreeView(self, freeView):
            """Slot function to switch between free view/cookie selection states """
            self.w.glpane.mode.setFreeView(freeView)
        
       def toggleFullModel(self, showFullModel):
            """Slot function for the check box of 'Full Model' in cookie-cutter dashboard """
            self.w.glpane.mode.toggleFullModel(showFullModel)
        
       def showGridLine(self, show):
            """Slot function"""
            self.w.glpane.mode.showGridLine(show)
                
       def changeGridColor(self):
            """Open the stand color chooser dialog to change grid line color """
            c = QColorDialog.getColor(QColor(222,148,0), self, "choose")
            if c.isValid():
                self.gridColorLabel.setPaletteBackgroundColor(c)
                self.w.glpane.mode.setGridLineColor(c)

       def changeLatticeType(self, lType):
           self.w.glpane.mode.changeLatticeType(lType)

       def changeDispMode(self, mode):
            self.w.glpane.mode.changeDispMode(mode)
        
       def changeGridOrientation(self, value):
           if value == 0: self._orient100()
           elif value == 1: self._orient110()
           elif value == 2: self._orient111()
       
       def _rotView(self, direction):
           """Rotate the view anti-clockwise or clockWise. 
           If <direction> == True, anti-clockwise rotate, otherwise, 
           clockwise rotate"""
           from math import pi
           from VQT import Q
           
           angle = self.gridRotateAngle.value()
           if not direction: angle = -angle
           angle = pi * angle/180.0
       
           glpane = self.w.glpane
           glpane.quat += Q(glpane.out, angle)
           glpane.gl_update()
       
       def antiRotateView(self):
           """Anti-clockwise rotatation """
           self._rotView(True)
       
       def rotateView(self):
           """clock-wise rotation """
           self._rotView(False)

       def _orient100(self):
            """ Along one axis """
            self.w.glpane.mode.surfset(0)
            self.w.glpane.snapquat100()
    
       def _orient110(self):
            """halfway between two axes"""           
            self.w.glpane.mode.surfset(1)
            self.w.glpane.snapquat110()
    
       def _orient111(self):
            """equidistant from three axes """
            self.w.glpane.mode.surfset(2)
            self.w.glpane.snapquat111()
    
       
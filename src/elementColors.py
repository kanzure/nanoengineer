# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
'''
elementColors.py

$Id$
'''
from ElementColorsDialog import *
from fileIO import readElementColors, saveElementColors
from elements import PeriodicTable 
from constants import globalParms, diVDW, diCPK, diTUBES 
from ThumbView import *
from chem import atom
from chunk import molecule
from HistoryWidget import redmsg # Mark 050311
from VQT import V

########################################################
# Declaring tuples
elementAMU = { 1 : "1.008", 2 : "4.003",
                        5 : "10.811", 6 : "12.011" , 7 : "14.007", 8 : "15.999", 9 : "18.998", 10: "20.178",
                        13 : "26.982", 14 : "28.086", 15 : "30.974", 16 : "32.066", 17 : "35.453", 18 : "39.948",
                        32 : "72.610", 33 : "74.922", 34 : "78.960", 35 : "79.904", 36 : "83.800",
                        51 : "121.760", 52 : "127.600", 53 : "126.904", 54 : "131.290" }
########################################################

class elementColors(ElementColorsDialog):
    _displayList = (diTUBES, diCPK, diVDW)
    
    def __init__(self, win):
        ElementColorsDialog.__init__(self, win, None, 0, Qt.WStyle_Customize | Qt.WStyle_NormalBorder | Qt.WStyle_Title | Qt.WStyle_SysMenu)
        self.w = win
        self.fileName = None
        self.isElementModified = False
        self.isFileSaved = False
        self.oldTable = PeriodicTable.deepCopy()
        self.elemTable = PeriodicTable
        self.displayMode = self._displayList[0]
        
        buttons = [(self.pushButton1, 1), (self.pushButton2, 2), (self.pushButton5, 5), (self.pushButton6, 6), (self.pushButton7,7), (self.pushButton8, 8), (self.pushButton9, 9), (self.pushButton10, 10), (self.pushButton13, 13), (self.pushButton14, 14), (self.pushButton15, 15), (self.pushButton16, 16), (self.pushButton17, 17), (self.pushButton18, 18), (self.pushButton32,32), (self.pushButton33, 33), (self.pushButton34, 34), (self.pushButton35, 35), (self.pushButton36, 36), (self.pushButton51, 51), (self.pushButton52, 52), (self.pushButton53, 53), (self.pushButton54, 54)]
        
        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.setExclusive(True)
        self.buttonGroup.hide()
        for button in buttons: self.buttonGroup.insert(button[0], button[1])
        self.connect(self.buttonGroup, SIGNAL("clicked(int)"), self.setElementInfo)
         
        self.elemGLPane = ElementView(self.elementFrame, "element glPane", self.w.glpane)
        # Put the GL widget inside the frame
        flayout = QVBoxLayout(self.elementFrame,1,1,'flayout')
        flayout.addWidget(self.elemGLPane,1)
        
        
    def closeEvent(self, e):
        """When user closes dialog by clicking the 'X' button on the dialog title bar, this method
            is called
        """
        self.ok()
         
    
    def disConnectChangingControls(self):
        self.disconnect(self.redSlider,SIGNAL("valueChanged(int)"),self.changeSpinRed)
        self.disconnect(self.redSpinBox,SIGNAL("valueChanged(int)"),self.changeSliderRed)
        self.disconnect(self.blueSlider,SIGNAL("valueChanged(int)"),self.changeSpinBlue)
        self.disconnect(self.blueSpinBox,SIGNAL("valueChanged(int)"),self.changeSliderBlue)
        self.disconnect(self.greenSlider,SIGNAL("valueChanged(int)"),self.changeSpinGreen)
        self.disconnect(self.greenSpinBox,SIGNAL("valueChanged(int)"),self.changeSliderGreen)
   
    def reconnectChangingControls(self):
        self.connect(self.redSlider,SIGNAL("valueChanged(int)"),self.changeSpinRed)
        self.connect(self.redSpinBox,SIGNAL("valueChanged(int)"),self.changeSliderRed)
        self.connect(self.blueSlider,SIGNAL("valueChanged(int)"),self.changeSpinBlue)
        self.connect(self.blueSpinBox,SIGNAL("valueChanged(int)"),self.changeSliderBlue)
        self.connect(self.greenSlider,SIGNAL("valueChanged(int)"),self.changeSpinGreen)
        self.connect(self.greenSpinBox,SIGNAL("valueChanged(int)"),self.changeSliderGreen)    
    
    
    def loadDefaultProp(self):
        """Load default set of color/rvdw for the current periodic table """    
        self.elemTable.loadDefaults()
        self._updateModelDisplay()
        elemNum =  self.buttonGroup.selectedId()
        self.setDisplay(elemNum)
        self.isElementModified = True
        
    def loadAlterProp(self):
        """Load alternate set of color/rvdw for the current periodic table """ 
        self.elemTable.loadAlternates()
        self._updateModelDisplay()
        elemNum =  self.buttonGroup.selectedId()
        self.setDisplay(elemNum)
        self.isElementModified = True
    
    def changeDisplayMode(self, value):
        """Called when any of the display mode radioButton clicked. """
        assert value in [0, 1, 2]
        newMode = self._displayList[value]
        if newMode != self.displayMode:
            self.displayMode = newMode
            elemNum =  self.buttonGroup.selectedId()
            elm = self.elemTable.getElement(elemNum)
            self.elemGLPane.refreshDisplay(elm, self.displayMode)
 
    # called as a slot from button push
    def setElementInfo(self,value):
        self.setDisplay(value)
        
    def setDisplay(self, value):
        eInfoText =   str(value) + "<br>"#"</p> "
        elemSymbol = self.elemTable.getElemSymbol(value)
        elemName = self.elemTable.getElemName(value)
        elemRvdw = str(self.elemTable.getElemRvdw(value))
        elemBonds = str(self.elemTable.getElemBondCount(value))
        if not elemSymbol: return
        eInfoText +=   "<font size=18> <b>" + elemSymbol + "</b> </font> <br>"#</p>"
        eInfoText +=  elemName + "<br>"#"</p>"
        eInfoText += "Amu: " + elementAMU[value] + "<br>"#"</p>"
        eInfoText += "Rvdw: " + elemRvdw + "<br>"#"</p>"
        eInfoText += "Open Bonds: " + elemBonds #</p>"
        self.elemInfoLabel.setText(eInfoText)
        
        self.buttonGroup.setButton(value)
        self.updateElemGraphDisplay()
        
        r =  int(self.color[0]*255 + 0.5)
        g = int(self.color[1]*255 + 0.5)
        b = int(self.color[2]*255 + 0.5)
        
        self.disConnectChangingControls()
        self.redSlider.setValue(r)
        self.greenSlider.setValue(g)
        self.blueSlider.setValue(b)
        self.redSpinBox.setValue(r)
        self.greenSpinBox.setValue(g)
        self.blueSpinBox.setValue(b)
        self.reconnectChangingControls()
        
    def updateElemGraphDisplay(self):
        """Update non user interactive controls display for current selected element: element label info and element graphics info """
        elemNum =  self.buttonGroup.selectedId()
        self.color = self.elemTable.getElemColor(elemNum)
        
        elm = self.elemTable.getElement(elemNum)
        self.elemGLPane.refreshDisplay(elm, self.displayMode)
        
        r =  int(self.color[0]*255 + 0.5)
        g = int(self.color[1]*255 + 0.5)
        b = int(self.color[2]*255 + 0.5)
        self.elemColorLabel.setPaletteBackgroundColor(QColor(r, g, b)) 
 

    def read_element_rgb_table(self):
        """Open file browser to select a file to read from, read the data, update elements color in the selector dialog and also the display models """
        # Determine what directory to open.
        import os
        if self.w.assy.filename: odir = os.path.dirname(self.w.assy.filename)
        else: odir = globalParms['WorkingDirectory']
        self.fileName = str(QFileDialog.getOpenFileName(odir,
                "Elements color file (*.txt);;All Files (*.*);;",
                self ))
        if self.fileName:
            colorTable = readElementColors(self.fileName)
            
            if not colorTable:
                self.w.history.message(redmsg("Error in element colors file: [" + self.fileName + "]. Colors not loaded."))
            else:
                self.w.history.message("Element colors loaded from file: [" + self.fileName + "].")
                for row in colorTable:
                     row[1] /= 255.0; row[2] /= 255.0; row[3] /= 255.0
                self.elemTable.setElemColors(colorTable)
                self._updateModelDisplay()     
                
                elemNum =  self.buttonGroup.selectedId()
                self.setDisplay(elemNum)
        #After loading a file, reset the flag        
        self.isElementModified = False        
        
        
    def write_element_rgb_table(self):
        """Save the current set of element preferences into an external file---currently only r,g,b color of each element will be saved."""
        if not self.fileName:
           sdir = globalParms['WorkingDirectory']
        else:
           sdir = self.fileName
           
        fn = QFileDialog.getSaveFileName(sdir,
                    "Element Color File (*.txt);;",
                    self, "colorSaveDialog", "Save Element Colors As ...")
        
        if fn:
            fn = str(fn)
            if fn[-4] != '.':
                fn += '.txt'
            
            import os    
            if os.path.exists(fn): # ...and if the "Save As" file exists...
                    # ... confirm overwrite of the existing file.
                    ret = QMessageBox.warning( self, "Save Element Colors...", "The file \"" + fn + "\" already exists.\n"\
                        "Do you want to overwrite the existing file or cancel?",
                        "&Overwrite", "&Cancel", None,
                        0,      # Enter == button 0
                        1 )     # Escape == button 1

                    if ret==1: # The user cancelled
                        return 
                    
            # write the current set of element colors into a file    
            saveElementColors(fn, self.elemTable.getAllElements())
            self.w.history.message("Element colors saved in file: [" + fn + "]")
            #After saving a file, reset the flag        
            self.isFileSaved = True        
 
    def changeSliderBlue(self,a0):
        self.disconnect(self.blueSlider,SIGNAL("valueChanged(int)"),self.changeSpinBlue)
        self.blueSlider.setValue(a0)
        elemNum =  self.buttonGroup.selectedId()
        self.elemTable.setElemColor(elemNum,  [self.color[0], self.color[1], a0/255.0])
        self._updateModelDisplay()
        self.connect(self.blueSlider,SIGNAL("valueChanged(int)"),self.changeSpinBlue)
        self.updateElemGraphDisplay()
        self.isElementModified = True
        
    def changeSpinRed(self,a0):
        self.disconnect(self.redSpinBox,SIGNAL("valueChanged(int)"),self.changeSliderRed)
        self.redSpinBox.setValue(a0)
        elemNum =  self.buttonGroup.selectedId()
        self.elemTable.setElemColor(elemNum,  [a0/255.0, self.color[1], self.color[2]])
        self._updateModelDisplay()
        self.connect(self.redSpinBox,SIGNAL("valueChanged(int)"),self.changeSliderRed)
        self.updateElemGraphDisplay()
        self.isElementModified = True
        
    def changeSliderRed(self,a0):
        self.disconnect( self.redSlider,SIGNAL("valueChanged(int)"),self.changeSpinRed)
        self.redSlider.setValue(a0)
        elemNum =  self.buttonGroup.selectedId()
        self.elemTable.setElemColor(elemNum,  [a0/255.0, self.color[1], self.color[2]])
        self._updateModelDisplay()
        self.connect(self.redSlider,SIGNAL("valueChanged(int)"),self.changeSpinRed)
        self.updateElemGraphDisplay()
        self.isElementModified = True
      
    def changeSpinBlue(self,a0):
        self.disconnect(self.blueSpinBox,SIGNAL("valueChanged(int)"),self.changeSliderBlue)
        self.blueSpinBox.setValue(a0)
        elemNum =  self.buttonGroup.selectedId()
        self.elemTable.setElemColor(elemNum,  [self.color[0], self.color[1], a0/255.0])
        self._updateModelDisplay()
        self.connect(self.blueSpinBox,SIGNAL("valueChanged(int)"),self.changeSliderBlue)
        self.updateElemGraphDisplay()
        self.isElementModified = True
        
    def changeSpinGreen(self,a0):
        self.disconnect(self.greenSpinBox,SIGNAL("valueChanged(int)"),self.changeSliderGreen)
        self.greenSpinBox.setValue(a0)
        elemNum =  self.buttonGroup.selectedId()
        self.elemTable.setElemColor(elemNum,  [self.color[0], a0/255.0, self.color[2]])
        self._updateModelDisplay()
        self.connect(self.greenSpinBox,SIGNAL("valueChanged(int)"),self.changeSliderGreen)
        self.updateElemGraphDisplay()
        self.isElementModified = True
                
    def changeSliderGreen(self,a0): 
        self.disconnect(self.greenSlider,SIGNAL("valueChanged(int)"),self.changeSpinGreen)
        self.greenSlider.setValue(a0)
        elemNum =  self.buttonGroup.selectedId()
        self.elemTable.setElemColor(elemNum,  [self.color[0], a0/255.0, self.color[2]])
        self._updateModelDisplay()
        self.connect(self.greenSlider,SIGNAL("valueChanged(int)"),self.changeSpinGreen)
        self.updateElemGraphDisplay()
        self.isElementModified = True
        
    def ok(self):
        #if self.isElementModified and not self.isFileSaved:
            #ret = QMessageBox.question(self, "Warnings", "Do you want to save the element colors into a file?", QMessageBox.Yes, QMessageBox.No)
            #if ret == QMessageBox.Yes:
            #    self.write_element_rgb_table()
            
         ##Save the color preference
         self.elemTable.close()
         
         self.accept()
        
        
    def reject(self):
        """ If elements modified or external file loaded, restore
        current pref to originial since our dialog is reused """
        if self.isElementModified or self.fileName:  
            self.elemTable.resetElemTable(self.oldTable)
            self._updateModelDisplay()
        
        QDialog.reject(self)
    
    
    def _updateModelDisplay(self):
        """Update model display """
        for mol in self.w.assy.molecules: 
            mol.changeapp(1)
        
        self.w.glpane.gl_update()
    
    

class ElementView(ThumbView):
    """Element graphical display """    
    def __init__(self, parent, name, shareWidget = None):
        ThumbView.__init__(self, parent, name, shareWidget)
        self.scale = 4.0#5.0 ## the possible largest rvdw of all elements
        self.pos = V(0.0, 0.0, 0.0)
        self.mol = None
        
        ## Dummy attributes. A kludge, just try to make other code
        ##  think it looks like a glpane object.
        self.display = 0  
        self.selatom = None

    def drawModel(self):
        """The method for element drawing """
        if self.mol:
           self.mol.draw(self, None)

    def refreshDisplay(self, elm, dispMode=diVDW):
        """Display the new element or the same element but new display mode"""   
        self.makeCurrent()
        self.mol = self._constructModel(elm, self.pos, dispMode) 
        self.updateGL()
    
    def _constructModel(self, elm, pos, dispMode):
        """This is to try to repeat what 'oneUnbonded()' function does, but hope to remove some stuff not needed here. The main purpose is to build the geometry model for element display. 
        <Param> elm: An object of class elem
        <Param> dispMode: the display mode of the atom--(int)
        <Return>: the molecule which contains the geometry model.
        """
        class DummyAssy:
            """dummy assemby class"""
            drawLevel = 2
            
        if 0:#1:
            assy = DummyAssy()
        else:
            from assembly import assembly 
            assy = assembly(None)
                
        mol = molecule(assy, 'dummy') 
        atm = atom(elm.symbol, pos, mol)
        atm.display = dispMode
        atm.make_singlets_when_no_bonds()
        return mol


##Junk code###
## The following code used to be for drawing text on a QGLWidget
if 0:
           glDisable(GL_LIGHTING)
           glDisable(GL_DEPTH_TEST) 
           self.qglColor(QColor(0, 0, 0))
           font = QFont( QString("Times"), 10)
           text = QString('Rvdw = ' + str(self.rad))
           fontMecs = QFontMetrics(font)
           strWd = fontMecs.width(text)
           strHt = fontMecs.height()
           w = self.width/2 - strWd/2
           h = self.height - strHt/2 
           self.renderText(w, h, text, font)
           glEnable(GL_DEPTH_TEST)
           glEnable(GL_LIGHTING)        
      
        
### Test code #########
import sys        
if __name__=='__main__':
  QApplication.setColorSpec(QApplication.CustomColor)
  app=QApplication(sys.argv)

  if not QGLFormat.hasOpenGL():
    raise 'No Qt OpenGL support.'

  w = elementColors(None)
  app.setMainWidget(w)
  w.resize(400,350)
  w.show()
  w.setCaption('box')
  app.exec_loop()        
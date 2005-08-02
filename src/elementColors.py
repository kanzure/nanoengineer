# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
'''
elementColors.py

$Id$
'''
from ElementColorsDialog import *
from elements import PeriodicTable 
from constants import globalParms, diVDW, diCPK, diTUBES 
from ThumbView import ElementView

from HistoryWidget import redmsg # Mark 050311
from VQT import V

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
        
        self.elemGLPane = ElementView(self.elementFrame, "element glPane", self.w.glpane)
        # Put the GL widget inside the frame
        flayout = QVBoxLayout(self.elementFrame,1,1,'flayout')
        flayout.addWidget(self.elemGLPane,1)
        
        self.connectChangingControls()
        
    def closeEvent(self, e):
        """When user closes dialog by clicking the 'X' button on the dialog title bar, this method
            is called
        """
        self.ok()
         
    
    def disConnectChangingControls(self):
        '''Obsolete member funtion. '''
        self.disconnect(self.redSlider,SIGNAL("valueChanged(int)"),self.changeSpinRed)
        self.disconnect(self.redSpinBox,SIGNAL("valueChanged(int)"),self.changeSliderRed)
        self.disconnect(self.blueSlider,SIGNAL("valueChanged(int)"),self.changeSpinBlue)
        self.disconnect(self.blueSpinBox,SIGNAL("valueChanged(int)"),self.changeSliderBlue)
        self.disconnect(self.greenSlider,SIGNAL("valueChanged(int)"),self.changeSpinGreen)
        self.disconnect(self.greenSpinBox,SIGNAL("valueChanged(int)"),self.changeSliderGreen)
   
    def connectChangingControls(self):
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
        elemNum =  self.elementButtonGroup.selectedId()
        self.setDisplay(elemNum)
        self.isElementModified = True
        
    def loadAlterProp(self):
        """Load alternate set of color/rvdw for the current periodic table """ 
        self.elemTable.loadAlternates()
        self._updateModelDisplay()
        elemNum =  self.elementButtonGroup.selectedId()
        self.setDisplay(elemNum)
        self.isElementModified = True
    
    def changeDisplayMode(self, value):
        """Called when any of the display mode radioButton clicked. Obsolete."""
        assert value in [0, 1, 2]
        newMode = self._displayList[value]
        if newMode != self.displayMode:
            self.displayMode = newMode
            elemNum =  self.elementButtonGroup.selectedId()
            elm = self.elemTable.getElement(elemNum)
            self.elemGLPane.refreshDisplay(elm, self.displayMode)
 
    def setElementInfo(self,value):
        '''Called as a slot from an element button push. '''
        self.setDisplay(value)
        
        
    def setDisplay(self, value):
        self.elementButtonGroup.setButton(value)
        self.updateElemGraphDisplay()
        
        r =  int(self.color[0]*255 + 0.5)
        g = int(self.color[1]*255 + 0.5)
        b = int(self.color[2]*255 + 0.5)
        
        #self.disConnectChangingControls()
        self.redSlider.setValue(r)
        self.greenSlider.setValue(g)
        self.blueSlider.setValue(b)
        self.redSpinBox.setValue(r)
        self.greenSpinBox.setValue(g)
        self.blueSpinBox.setValue(b)
        #self.reconnectChangingControls()

        
    def updateElemGraphDisplay(self):
        """Update non user interactive controls display for current selected element:
        element label info and element graphics info """
        elemNum =  self.elementButtonGroup.selectedId()
        self.color = self.elemTable.getElemColor(elemNum)
        
        elm = self.elemTable.getElement(elemNum)
        self.elemGLPane.resetView(scale = 4.0)
        self.elemGLPane.refreshDisplay(elm, self.displayMode)
        
        r =  int(self.color[0]*255 + 0.5)
        g = int(self.color[1]*255 + 0.5)
        b = int(self.color[2]*255 + 0.5)
        self.elemColorLabel.setPaletteBackgroundColor(QColor(r, g, b)) 
 
    
    def updateElemColorDisplay(self):
        '''Update GL display for user's color change. '''
        elemNum =  self.elementButtonGroup.selectedId()
        self.color = self.elemTable.getElemColor(elemNum)
        
        elm = self.elemTable.getElement(elemNum)
        self.elemGLPane.updateColorDisplay(elm, self.displayMode)
        
        r =  int(self.color[0]*255 + 0.5)
        g = int(self.color[1]*255 + 0.5)
        b = int(self.color[2]*255 + 0.5)
        self.elemColorLabel.setPaletteBackgroundColor(QColor(r, g, b)) 
 

    def read_element_rgb_table(self):
        """Open file browser to select a file to read from, read the data,
        update elements color in the selector dialog and also the display models """
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
                
                elemNum =  self.elementButtonGroup.selectedId()
                self.setDisplay(elemNum)
        #After loading a file, reset the flag        
        self.isElementModified = False        
        
        
    def write_element_rgb_table(self):
        """Save the current set of element preferences into an external file---
        currently only r,g,b color of each element will be saved."""
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
        self.blueSlider.blockSignals(True)
        self.blueSlider.setValue(a0)
        elemNum =  self.elementButtonGroup.selectedId()
        self.elemTable.setElemColor(elemNum,  [self.color[0], self.color[1], a0/255.0])
        self.updateElemColorDisplay()
        self.isElementModified = True
        self.blueSlider.blockSignals(False)
        
    def changeSpinRed(self,a0):
        self.redSpinBox.blockSignals(True)
        self.redSpinBox.setValue(a0)
        elemNum =  self.elementButtonGroup.selectedId()
        self.elemTable.setElemColor(elemNum,  [a0/255.0, self.color[1], self.color[2]])
        self.updateElemColorDisplay()
        self.isElementModified = True
        self.redSpinBox.blockSignals(False)
        
    def changeSliderRed(self,a0):
        self.redSlider.blockSignals(True)
        self.redSlider.setValue(a0)
        elemNum =  self.elementButtonGroup.selectedId()
        self.elemTable.setElemColor(elemNum,  [a0/255.0, self.color[1], self.color[2]])
        self.updateElemColorDisplay()
        self.isElementModified = True
        self.redSlider.blockSignals(False)
      
    def changeSpinBlue(self,a0):
        self.blueSpinBox.blockSignals(True)
        self.blueSpinBox.setValue(a0)
        elemNum =  self.elementButtonGroup.selectedId()
        self.elemTable.setElemColor(elemNum,  [self.color[0], self.color[1], a0/255.0])
        self.updateElemColorDisplay()
        self.isElementModified = True
        self.blueSpinBox.blockSignals(False)
        
        
    def changeSpinGreen(self,a0):
        self.greenSpinBox.blockSignals(True)
        self.greenSpinBox.setValue(a0)
        elemNum =  self.elementButtonGroup.selectedId()
        self.elemTable.setElemColor(elemNum,  [self.color[0], a0/255.0, self.color[2]])
        self.updateElemColorDisplay()
        self.isElementModified = True
        self.greenSpinBox.blockSignals(False)
        
                
    def changeSliderGreen(self,a0): 
        self.greenSlider.blockSignals(True)
        self.greenSlider.setValue(a0)
        elemNum =  self.elementButtonGroup.selectedId()
        self.elemTable.setElemColor(elemNum,  [self.color[0], a0/255.0, self.color[2]])
        self.updateElemColorDisplay()
        self.isElementModified = True
        self.greenSlider.blockSignals(False)
        
    def ok(self):
        #if self.isElementModified and not self.isFileSaved:
            #ret = QMessageBox.question(self, "Warnings",
            # "Do you want to save the element colors into a file?", QMessageBox.Yes, QMessageBox.No)
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


# ==

#bruce 050414 moved readElementColors and saveElementColors from fileIO.py
# into this module, and (while they were still in fileIO -- see its cvs diff)
# slightly revised the wording/formatting of their docstrings.
# Sometime they should be changed to print their error messages into the
# history widget, not sys.stdout.

def readElementColors(fileName):
    """Read element colors (ele #, r, g, b) from a text file.
    Each element is on a new line. A line starting '#' is a comment line.
    <Parameter> fileName: a string for the input file name
    <Return>:  A list of quardral tuples--(ele #, r, g, b) if succeed, otherwise 'None'
    """
    try:
        lines = open(fileName, "rU").readlines()         
    except:
        print "Exception occurred to open file: ", fileName
        return None
    
    elemColorTable = []
    for line in lines: 
        if not line.startswith('#'):
            try:
                words = line.split()
                row = map(int, words[:4])
                # Check Element Number validity
                if row[0] >= 0 and row[0] <= 54:
                    # Check RGB index values
                    if row[1] < 0 or row[1] > 255 or row[2] < 0 or row[2] > 255 or row[3] < 0 or row[3] > 255:
                        raise ValueError, "An RGB index value not in a valid range (0-255)."
                    elemColorTable += [row]
                else:
                    raise ValueError, "Element number value not in a valid range."
            except:
               print "Error in element color file %s.  Invalid value in line: %sElement color file not loaded." % (fileName, line)
               return None
    
    return elemColorTable           


def saveElementColors(fileName, elemTable):
    """Write element colors (ele #, r, g, b) into a text file.
    Each element is on a new line.  A line starting '#' is a comment line.
    <Parameter> fileName: a string for the input file name
    <Parameter> elemTable: A dictionary object of all elements in our periodical table 
    """
    assert type(fileName) == type(" ")
    
    try:
        f = open(fileName, "w")
    except:
        print "Exception occurred to open file %s to write: " % fileName
        return None
   
    f.write("# nanoENGINEER-1.com Element Color File, Version 050311\n")
    f.write("# File format: ElementNumber r(0-255) g(0-255) b(0-255) \n")
    
    for eleNum, elm in elemTable.items():
        col = elm.color
        r = int(col[0] * 255 + 0.5)
        g = int(col[1] * 255 + 0.5)
        b = int(col[2] * 255 + 0.5)
        f.write(str(eleNum) + "  " + str(r) + "  " + str(g) + "  " + str(b) + "\n")
    
    f.close()

# ==

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
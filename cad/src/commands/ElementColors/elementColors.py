# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
elementColors.py - dialog for changing element color table; related functions

@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""

from PyQt4.Qt import QDialog
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QVBoxLayout
from PyQt4.Qt import QFileDialog
from PyQt4.Qt import QMessageBox
from PyQt4.Qt import QApplication
from PyQt4.QtOpenGL import QGLFormat

from commands.ElementColors.ElementColorsDialog import Ui_ElementColorsDialog
from model.elements import PeriodicTable
from utilities.constants import diTrueCPK, diBALL, diTUBES
from graphics.widgets.ThumbView import ElementView
from utilities.qt4transition import qt4todo

from utilities.Log import redmsg # Mark 050311
from widgets.widget_helpers import RGBf_to_QColor
import foundation.env as env

class elementColors(QDialog, Ui_ElementColorsDialog):
    _displayList = (diTUBES, diBALL, diTrueCPK)

    def __init__(self, win):
        qt4todo('what to do with all those options?')
        ## ElementColorsDialog.__init__(self, win, None, 0,
        ##   Qt.WStyle_Customize | Qt.WStyle_NormalBorder |
        ##   Qt.WStyle_Title | Qt.WStyle_SysMenu)
        QDialog.__init__(self, win)
        self.setupUi(self)
        self.connect(self.okButton, SIGNAL("clicked()"), self.ok)
        self.connect(self.loadColorsPB, SIGNAL("clicked()"), self.read_element_rgb_table)
        self.connect(self.saveColorsPB, SIGNAL("clicked()"), self.write_element_rgb_table)
        self.connect(self.cancelButton, SIGNAL("clicked()"), self.reject)
        self.connect(self.defaultButton, SIGNAL("clicked()"), self.loadDefaultProp)
        self.connect(self.alterButton, SIGNAL("clicked()"), self.loadAlterProp)
        self.connect(self.elementButtonGroup, SIGNAL("clicked(int)"), self.setElementInfo)
        self.connect(self.previewPB, SIGNAL("clicked()"), self.preview_color_change)
        self.connect(self.restorePB, SIGNAL("clicked()"), self.restore_current_color)
        self.w = win
        self.fileName = None
        self.isElementModified = False
        self.isFileSaved = False
        self.oldTable = PeriodicTable.deepCopy()
        self.elemTable = PeriodicTable
        self.displayMode = self._displayList[0]
        # The next line fixes a bug. Thumbview expects self.gridLayout on
        # line 117 of Thumbview.py. Mark 2007-10-19.
        self.gridLayout = self.gridlayout
        self.elemGLPane = ElementView(self, "element glPane", self.w.glpane)
        # Put the GL widget inside the frame
        flayout = QVBoxLayout(self.elementFrame)
        flayout.setMargin(1)
        flayout.setSpacing(1)
        flayout.addWidget(self.elemGLPane, 1)

        def elementId(symbol):
            return PeriodicTable.getElement(symbol).eltnum
        self.toolButton6.setChecked(True)
        self.elementButtonGroup.setId(self.toolButton6, elementId("C"))
        self.elementButtonGroup.setId(self.toolButton8, elementId("O"))
        self.elementButtonGroup.setId(self.toolButton10, elementId("Ne"))
        self.elementButtonGroup.setId(self.toolButton9, elementId("F"))
        self.elementButtonGroup.setId(self.toolButton13, elementId("Al"))
        self.elementButtonGroup.setId(self.toolButton17, elementId("Cl"))
        self.elementButtonGroup.setId(self.toolButton5, elementId("B"))
        self.elementButtonGroup.setId(self.toolButton10_2, elementId("Ar"))
        self.elementButtonGroup.setId(self.toolButton15, elementId("P"))
        self.elementButtonGroup.setId(self.toolButton16, elementId("S"))
        self.elementButtonGroup.setId(self.toolButton14, elementId("Si"))
        self.elementButtonGroup.setId(self.toolButton33, elementId("As"))
        self.elementButtonGroup.setId(self.toolButton34, elementId("Se"))
        self.elementButtonGroup.setId(self.toolButton35, elementId("Br"))
        self.elementButtonGroup.setId(self.toolButton36, elementId("Kr"))
        self.elementButtonGroup.setId(self.toolButton32, elementId("Ge"))
        self.elementButtonGroup.setId(self.toolButton7, elementId("N"))
        self.elementButtonGroup.setId(self.toolButton2, elementId("He"))
        self.elementButtonGroup.setId(self.toolButton1, elementId("H"))
        self.elementButtonGroup.setId(self.toolButton0, elementId("X"))

        self.connect(self.toolButton6, SIGNAL("clicked()"), self.updateElemColorDisplay)
        self.connect(self.toolButton8, SIGNAL("clicked()"), self.updateElemColorDisplay)
        self.connect(self.toolButton10, SIGNAL("clicked()"), self.updateElemColorDisplay)
        self.connect(self.toolButton9, SIGNAL("clicked()"), self.updateElemColorDisplay)
        self.connect(self.toolButton13, SIGNAL("clicked()"), self.updateElemColorDisplay)
        self.connect(self.toolButton17, SIGNAL("clicked()"), self.updateElemColorDisplay)
        self.connect(self.toolButton5, SIGNAL("clicked()"), self.updateElemColorDisplay)
        self.connect(self.toolButton10_2, SIGNAL("clicked()"), self.updateElemColorDisplay)
        self.connect(self.toolButton15, SIGNAL("clicked()"), self.updateElemColorDisplay)
        self.connect(self.toolButton16, SIGNAL("clicked()"), self.updateElemColorDisplay)
        self.connect(self.toolButton14, SIGNAL("clicked()"), self.updateElemColorDisplay)
        self.connect(self.toolButton33, SIGNAL("clicked()"), self.updateElemColorDisplay)
        self.connect(self.toolButton34, SIGNAL("clicked()"), self.updateElemColorDisplay)
        self.connect(self.toolButton35, SIGNAL("clicked()"), self.updateElemColorDisplay)
        self.connect(self.toolButton36, SIGNAL("clicked()"), self.updateElemColorDisplay)
        self.connect(self.toolButton32, SIGNAL("clicked()"), self.updateElemColorDisplay)
        self.connect(self.toolButton7, SIGNAL("clicked()"), self.updateElemColorDisplay)
        self.connect(self.toolButton2, SIGNAL("clicked()"), self.updateElemColorDisplay)
        self.connect(self.toolButton1, SIGNAL("clicked()"), self.updateElemColorDisplay)
        self.connect(self.toolButton0, SIGNAL("clicked()"), self.updateElemColorDisplay)

        self.connectChangingControls()
        self.saveColorsPB.setWhatsThis(
            """Save the current color settings for elements in a text file.""")
        self.defaultButton.setWhatsThis(
            """Restore current element colors to the default colors.""")
        self.loadColorsPB.setWhatsThis(
            """Load element colors from an external text file.""")
        self.alterButton.setWhatsThis(
            """Set element colors to the alternate color set.""")

    def closeEvent(self, e):
        """
        When user closes dialog by clicking the 'X' button on the dialog title bar, this method
        is called
        """
        self.ok()

    def connectChangingControls(self):
        self.connect(self.redSlider, SIGNAL("valueChanged(int)"), self.changeSpinRed)
        self.connect(self.redSpinBox, SIGNAL("valueChanged(int)"), self.changeSliderRed)
        self.connect(self.blueSlider, SIGNAL("valueChanged(int)"), self.changeSpinBlue)
        self.connect(self.blueSpinBox, SIGNAL("valueChanged(int)"), self.changeSliderBlue)
        self.connect(self.greenSlider, SIGNAL("valueChanged(int)"), self.changeSpinGreen)
        self.connect(self.greenSpinBox, SIGNAL("valueChanged(int)"), self.changeSliderGreen)

    def loadDefaultProp(self):
        """
        Load default set of color/rvdw for the current periodic table
        """
        self.elemTable.loadDefaults()
        self._updateModelDisplay()
        elemNum =  self.elementButtonGroup.checkedId()
        self.setDisplay(elemNum)
        self.isElementModified = True

    def loadAlterProp(self):
        """
        Load alternate set of color/rvdw for the current periodic table
        """
        self.elemTable.loadAlternates()
        self._updateModelDisplay()
        elemNum =  self.elementButtonGroup.checkedId()
        self.setDisplay(elemNum)
        self.isElementModified = True

    def changeDisplayMode(self, value):
        """
        Called when any of the display mode radioButton clicked. Obsolete.
        """
        assert value in [0, 1, 2]
        newMode = self._displayList[value]
        if newMode != self.displayMode:
            self.displayMode = newMode
            elemNum =  self.elementButtonGroup.checkedId()
            elm = self.elemTable.getElement(elemNum)
            self.elemGLPane.refreshDisplay(elm, self.displayMode)

    def setElementInfo(self, value):
        """
        Called as a slot from an element button push.
        """
        self.setDisplay(value)

    def setDisplay(self, value):
        qt4todo('self.elementButtonGroup.setButton(value)')
        self.updateElemGraphDisplay()
        self.original_color = self.color

        element_color = RGBf_to_QColor(self.color)
        self.update_sliders_and_spinboxes(element_color)
        self.restorePB.setEnabled(0) # Disable Restore button.

    def update_sliders_and_spinboxes(self, color):
        self.redSlider.setValue(color.red())
        self.greenSlider.setValue(color.green())
        self.blueSlider.setValue(color.blue())
        self.redSpinBox.setValue(color.red())
        self.greenSpinBox.setValue(color.green())
        self.blueSpinBox.setValue(color.blue())

    def updateElemGraphDisplay(self):
        """
        Update non user interactive controls display for current selected element:
        element label info and element graphics info
        """
        elemNum =  self.elementButtonGroup.checkedId()
        self.color = self.elemTable.getElemColor(elemNum)
        elm = self.elemTable.getElement(elemNum)
        self.elemGLPane.resetView()
        self.elemGLPane.refreshDisplay(elm, self.displayMode)


    def updateElemColorDisplay(self):
        """
        Update GL display for user's color change.
        """
        elemNum =  self.elementButtonGroup.checkedId()
        self.color = self.elemTable.getElemColor(elemNum)

        elm = self.elemTable.getElement(elemNum)
        self.elemGLPane.updateColorDisplay(elm, self.displayMode)

        self.restorePB.setEnabled(1) # Enable Restore button.

    def read_element_rgb_table(self):
        """
        Open file browser to select a file to read from, read the data,
        update elements color in the selector dialog and also the display models
        """
        # Determine what directory to open.
        import os
        if self.w.assy.filename:
            odir = os.path.dirname(self.w.assy.filename)
        else:
            from utilities.prefs_constants import workingDirectory_prefs_key
            odir = env.prefs[workingDirectory_prefs_key]
        self.fileName = str( QFileDialog.getOpenFileName(
                                self,
                                "Load Element Color",
                                odir,
                                "Elements color file (*.txt);;All Files (*.*);;"
                                 ))
        if self.fileName:
            colorTable = readElementColors(self.fileName)

            if not colorTable:
                msg = "Error in element colors file: [" + self.fileName + "]. Colors not loaded."
                env.history.message(redmsg(msg))
            else:
                msg = "Element colors loaded from file: [" + self.fileName + "]."
                env.history.message(msg)
                for row in colorTable:
                    row[1] /= 255.0
                    row[2] /= 255.0
                    row[3] /= 255.0
                self.elemTable.setElemColors(colorTable)
                self._updateModelDisplay()

                elemNum =  self.elementButtonGroup.checkedId()
                self.setDisplay(elemNum)
        #After loading a file, reset the flag
        self.isElementModified = False


    def write_element_rgb_table(self):
        """
        Save the current set of element preferences into an external file --
        currently only r,g,b color of each element will be saved.
        """
        if not self.fileName:
            from utilities.prefs_constants import workingDirectory_prefs_key
            sdir = env.prefs[workingDirectory_prefs_key]
        else:
            sdir = self.fileName

        fn = QFileDialog.getSaveFileName(
                     self,
                     "Save Element Colors As ...",
                     sdir,
                    "Element Color File (*.txt)"
                     )

        if fn:
            fn = str(fn)
            if fn[-4] != '.':
                fn += '.txt'

            import os
            if os.path.exists(fn): # ...and if the "Save As" file exists...
                # ... confirm overwrite of the existing file.
                ret = QMessageBox.warning( self, "Save Element Colors...",
                    "The file \"" + fn + "\" already exists.\n"
                      "Do you want to overwrite the existing file or cancel?",
                    "&Overwrite", "&Cancel", "",
                    0,      # Enter == button 0
                    1 )     # Escape == button 1

                if ret == 1: # The user cancelled
                    return

            # write the current set of element colors into a file
            saveElementColors(fn, self.elemTable.getAllElements())
            env.history.message("Element colors saved in file: [" + fn + "]")
            #After saving a file, reset the flag
            self.isFileSaved = True

    def changeSpinRed(self, a0):
        self.redSpinBox.blockSignals(True)
        self.redSpinBox.setValue(a0)
        elemNum =  self.elementButtonGroup.checkedId()
        self.elemTable.setElemColor(elemNum,  [a0/255.0, self.color[1], self.color[2]])
        self.updateElemColorDisplay()
        self.isElementModified = True
        self.redSpinBox.blockSignals(False)

    def changeSliderRed(self, a0):
        self.redSlider.blockSignals(True)
        self.redSlider.setValue(a0)
        elemNum =  self.elementButtonGroup.checkedId()
        self.elemTable.setElemColor(elemNum,  [a0/255.0, self.color[1], self.color[2]])
        self.updateElemColorDisplay()
        self.isElementModified = True
        self.redSlider.blockSignals(False)

    def changeSpinBlue(self, a0):
        self.blueSpinBox.blockSignals(True)
        self.blueSpinBox.setValue(a0)
        elemNum =  self.elementButtonGroup.checkedId()
        self.elemTable.setElemColor(elemNum,  [self.color[0], self.color[1], a0/255.0])
        self.updateElemColorDisplay()
        self.isElementModified = True
        self.blueSpinBox.blockSignals(False)

    def changeSliderBlue(self, a0):
        self.blueSlider.blockSignals(True)
        self.blueSlider.setValue(a0)
        elemNum =  self.elementButtonGroup.checkedId()
        self.elemTable.setElemColor(elemNum,  [self.color[0], self.color[1], a0/255.0])
        self.updateElemColorDisplay()
        self.isElementModified = True
        self.blueSlider.blockSignals(False)

    def changeSpinGreen(self, a0):
        self.greenSpinBox.blockSignals(True)
        self.greenSpinBox.setValue(a0)
        elemNum =  self.elementButtonGroup.checkedId()
        self.elemTable.setElemColor(elemNum,  [self.color[0], a0/255.0, self.color[2]])
        self.updateElemColorDisplay()
        self.isElementModified = True
        self.greenSpinBox.blockSignals(False)

    def changeSliderGreen(self, a0):
        self.greenSlider.blockSignals(True)
        self.greenSlider.setValue(a0)
        elemNum =  self.elementButtonGroup.checkedId()
        self.elemTable.setElemColor(elemNum,  [self.color[0], a0/255.0, self.color[2]])
        self.updateElemColorDisplay()
        self.isElementModified = True
        self.greenSlider.blockSignals(False)

    def preview_color_change(self): # mark 060129.
        """
        Slot for Preview button.  Applies color changes for the current element in the GLPane,
        allowing the user to preview the color changes in the model before saving.
        """
        self._updateModelDisplay()

    def restore_current_color(self): # mark 060129.
        """
        Slot for the Restore button.  Restores the current element color to the
        original (previous) color before any color change was made.
        """
        self.update_sliders_and_spinboxes(RGBf_to_QColor(self.original_color))
        self._updateModelDisplay()

    def ok(self):
        ## if self.isElementModified and not self.isFileSaved:
            ## ret = QMessageBox.question(self, "Warnings",
            ##  "Do you want to save the element colors into a file?",
            ##  QMessageBox.Yes, QMessageBox.No )
            ## if ret == QMessageBox.Yes:
            ##     self.write_element_rgb_table()

        #Save the color preference
        self.elemTable.close()
        self._updateModelDisplay() #bruce 090119 bugfix

        self.accept()


    def reject(self):
        """
        If elements modified or external file loaded, restore
        current pref to original since our dialog is reused
        """
        if self.isElementModified or self.fileName:
            self.elemTable.resetElemTable(self.oldTable)
            self._updateModelDisplay()

        QDialog.reject(self)


    def _updateModelDisplay(self):
        """
        Update model display
        """
        #bruce 090119 removed changeapp calls, not needed for a long time
        # (due to PeriodicTable.color_change_counter);
        # then replaced other calls of gl_update with calls of this method
        self.w.glpane.gl_update()


# ==

#bruce 050414 moved readElementColors and saveElementColors from fileIO.py
# into this module, and (while they were still in fileIO -- see its cvs diff)
# slightly revised the wording/formatting of their docstrings.
# Sometime they should be changed to print their error messages into the
# history widget, not sys.stdout.

def readElementColors(fileName):
    """
    Read element colors (ele #, r, g, b) from a text file.
    Each element is on a new line. A line starting '#' is a comment line.
    <Parameter> fileName: a string for the input file name
    <Return>:  A list of quardral tuples--(ele #, r, g, b) if succeed,
    otherwise 'None'
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
                    if row[1] < 0 or row[1] > 255 \
                    or row[2] < 0 or row[2] > 255 \
                    or row[3] < 0 or row[3] > 255:
                        raise ValueError, "An RGB index value not in a valid range (0-255)."
                    elemColorTable += [row]
                else:
                    raise ValueError, "Element number value not in a valid range."
            except:
                # todo: env.history.redmsg
                print "Error in element color file [%s]." % (fileName,)
                print "Invalid value in line: %s" % (line,)
                print "Element color file not loaded."
                return None

    return elemColorTable


def saveElementColors(fileName, elemTable):
    """
    Write element colors (ele #, r, g, b) into a text file.
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

    f.write("# NanoEngineer-1.com Element Color File, Version 050311\n")
    f.write("# File format: ElementNumber r(0-255) g(0-255) b(0-255) \n")

    for eleNum, elm in elemTable.items():
        col = elm.color
        r = int(col[0] * 255 + 0.5)
        g = int(col[1] * 255 + 0.5)
        b = int(col[2] * 255 + 0.5)
        f.write(str(eleNum)
                + "  " + str(r)
                +  "  " + str(g)
                + "  " + str(b)
                + "\n" )

    f.close()


# == Test code

import sys

if __name__ == '__main__':

    QApplication.setColorSpec(QApplication.CustomColor)
    app = QApplication(sys.argv)

    if not QGLFormat.hasOpenGL():
        raise Exception("No Qt OpenGL support.")

    w = elementColors(None)
    app.setMainWidget(w)
    w.resize(400, 350)
    w.show()
    w.setCaption('box')
    app.exec_()



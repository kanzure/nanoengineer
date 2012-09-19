# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details.
"""
BuildCrystal_PropertyManager.py

Class used for the GUI controls for the BuildCrystal_Command.

@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details.

History:
Note: Till Alpha8, this command was called Cookie Cutter mode. In Alpha9
it has been renamed to 'Build Crystal' mode. -- ninad 20070511

Ninad 2008-08-22:
   - renamed class CookieCntrlPanel to BuildCrystal_PropertyManager,also
     deleted the old CookiePropertyManager.py
   - major cleanup: moved flyout toolbar related code
     in its own class (see Ui_BuildCrystalFlyout); moved command specific code
     in the command class.
"""
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QString
from PyQt4.Qt import QColor
from PyQt4.Qt import QColorDialog

from commands.BuildCrystal.Ui_BuildCrystal_PropertyManager import Ui_BuildCrystal_PropertyManager


_superclass = Ui_BuildCrystal_PropertyManager
class BuildCrystal_PropertyManager(Ui_BuildCrystal_PropertyManager):

    def __init__(self, command):
        """
        """


        _superclass.__init__(self, command)

        msg = "Choose one of the selection shapes from the command toolbar. "\
            "When drawing a <b>Polygon</b> shape, double-click to select the final vertex."
        self.updateMessage(msg = msg)

    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect signal to slots
        """
        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect

        change_connect(self.latticeCBox, SIGNAL("activated ( int )"),
                        self.changeLatticeType)

        change_connect(self.orientButtonGroup, SIGNAL("buttonClicked(int)"),
                        self.changeGridOrientation)

        change_connect(self.rotGridAntiClockwiseButton,
                        SIGNAL("clicked()"), self.antiRotateView)

        change_connect(self.rotGridClockwiseButton, SIGNAL("clicked()"),
                        self.rotateView)

        change_connect(self.addLayerButton,SIGNAL("clicked()"), self.addLayer)
        change_connect(self.currentLayerComboBox,SIGNAL("activated(int)"),
                        self.changeLayer)

        change_connect(self.layerCellsSpinBox,SIGNAL("valueChanged(int)"),
                        self.setThickness)
        #change_connect(self.gridColorButton,SIGNAL("clicked()"),self.changeGridColor)

        change_connect(self.gridLineCheckBox,SIGNAL("toggled(bool)"),
                        self.showGridLine)

        change_connect(self.freeViewCheckBox,SIGNAL("toggled(bool)"),
                        self.setFreeView)
        change_connect(self.fullModelCheckBox, SIGNAL("toggled(bool)"),
                        self.toggleFullModel)
        change_connect(self.snapGridCheckBox, SIGNAL("toggled(bool)"),
                        self.setGridSnap)

        change_connect(self.dispModeComboBox, SIGNAL("activated(const QString &)"),
                     self.changeDispMode)


    def show(self):
        """
        This is used to initialize GUI items which need
        to change every time the command becomes active.
        """

        _superclass.show(self)

        self.latticeCBox.setEnabled(True)

        # Other things that have been lost at this point:
        # self.layerThicknessLineEdit
        self.layerCellsSpinBox.setValue(2)
        self.rotateGridByAngleSpinBox.setValue(45)

        self.currentLayerComboBox.clear()
        self.currentLayerComboBox.addItem("1")   #QString(str(len(self.layers[0])))) ? ? ?
        self.addLayerButton.setEnabled(False)

    def close(self):
        """
        Restore GUI items when exiting from the PM (command).
        """
        _superclass.close(self)

        # Enable all those view options
        self.enableViewChanges(True)


    def enableViewChanges(self, enableFlag):
        """Turn on or off view changes depending on <param> 'enableFlag'.
        Turn off view changes is needed during the crystal-cutting stage. """

        for c in self.orientButtonGroup.buttons():
            c.setEnabled(enableFlag)

        self.rotateGridByAngleSpinBox.setEnabled(enableFlag)
        self.rotGridAntiClockwiseButton.setEnabled(enableFlag)
        self.rotGridClockwiseButton.setEnabled(enableFlag)
        self.w.enableViews(enableFlag) # Mark 051122.


    def changeSelectionShape(self, action):
        """Slot method that is called when user changes selection shape by GUI. """
        command = self.command
        if not command.isCurrentCommand(): # [bruce 071008]
            return
        sShape = action.objectName()
        command.changeSelectionShape(sShape)
        return

    def setThickness(self, value):
        self.command.setThickness(value)

    def addLayer(self):
        self.addLayerButton.setEnabled(False)
        layerId = self.command.addLayer()

        self.currentLayerComboBox.addItem(QString(str(layerId)))
        self.currentLayerComboBox.setCurrentIndex(layerId-1)

        self.w.glpane.gl_update()

    def changeLayer(self, value):
        """Change current layer to <value> layer """
        self.command.change2Layer(value)

    def setFreeView(self, freeView):
        """Slot function to switch between free view/crystal selection states """
        self.command.setFreeView(freeView)

    def toggleFullModel(self, showFullModel):
        """Slot function for the check box of 'Full Model' in crystal-cutter dashboard """
        self.command.toggleFullModel(showFullModel)

    def showGridLine(self, show):
        """Slot function"""
        self.command.showGridLine(show)

    def setGridSnap(self, snap):
        """Turn on/off the grid snap option """
        self.command.gridSnap = snap
        pass

    def changeGridColor(self):
        """
        Open the stand color chooser dialog to change grid line color
        """
        c = QColorDialog.getColor(QColor(222,148,0), self)
        if c.isValid():
            self.gridColorLabel.setPaletteBackgroundColor(c)
            self.command.setGridLineColor(c)

    def changeLatticeType(self, lType):
        self.command.changeLatticeType(lType)
        if lType != 0: #Changes to other lattice type
            #Disable the snap to grid feature
            self.setGridSnap(False)
            self.snapGridCheckBox.setEnabled(False)
        else:
            self.snapGridCheckBox.setEnabled(True)

    def changeDispMode(self, display_style):
        self.command.changeDispMode(display_style)

    def changeGridOrientation(self, value):
        if value == 0: self._orient100()
        elif value == 1: self._orient110()
        elif value == 2: self._orient111()

    def _rotView(self, direction):
        """
        Rotate the view anti-clockwise or clockWise.
        If <direction> == True, anti-clockwise rotate, otherwise,
        clockwise rotate
        """
        from math import pi
        from geometry.VQT import Q, V

        angle = self.rotateGridByAngleSpinBox.value()
        if not direction: angle = -angle
        angle = pi * angle/180.0

        glpane = self.w.glpane

        glpane.quat += Q(V(0, 0, 1), angle)
        glpane.gl_update()

    def antiRotateView(self):
        """
        Anti-clockwise rotatation
        """
        self._rotView(True)

    def rotateView(self):
        """
        clock-wise rotation
        """
        self._rotView(False)

    def _orient100(self):
        """
        Along one axis
        """
        self.command.setOrientSurf(0)
        self.command.snapquat100()

    def _orient110(self):
        """
        halfway between two axes
        """
        self.command.setOrientSurf(1)
        self.command.snapquat110()

    def _orient111(self):
        """
        equidistant from three axes
        """
        self.command.setOrientSurf(2)
        self.command.snapquat111()

    pass

# end

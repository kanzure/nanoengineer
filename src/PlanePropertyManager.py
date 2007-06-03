# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad,
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
ninad 20070702: Created.

"""
__author__ = "Ninad"

import sys
from PyQt4.Qt import *
from PyQt4 import QtGui
from PyQt4.QtGui import QAction
from Utility import geticon, getpixmap
from PropMgrBaseClass import *
from PropMgr_Constants import *
from PropertyManagerMixin import PropertyManagerMixin


class PlanePropMgr(object,PropMgrBaseClass, PropertyManagerMixin):
    ''' UI and slot methods for Plane Property manager'''
    
    # <title> - the title that appears in the property manager header.
    title = "Plane"
    # <propmgr_name> - the name of this property manager. This will be set to
    # the name of the PropMgr (this) object via setObjectName().
    propmgr_name = "pm" + title
    # <iconPath> - full path to PNG file that appears in the header.
    iconPath = "ui/actions/Insert/Reference Geometry/Plane.png"
    
    def __init__(self):
        """Construct the Plane Property Manager.
        """
        PropMgrBaseClass.__init__(self, self.propmgr_name)
        self.setPropMgrIcon(self.iconPath)
        self.setPropMgrTitle(self.title)
        self.addGroupBoxes()
        self.addBottomSpacer() 
        self.add_whats_this_text()
        
        msg = "Insert a Plane parallel to the screen. Note: This feature is \
        experimental for Alpha9 and has known bugs"
        
        # This causes the "Message" box to be displayed as well.
        self.MessageGroupBox.insertHtmlMessage(msg, setAsDefault=False)
        
        #self.resized_from_glpane flag makes sure that the spinbox.valuChanged()
        #signal is not emitted after calling spinbox.setValue.
        self.resized_from_glpane = False
        
        self.hideTopRowButtons(pmHideRestoreDefaultsButton)
        
    def addGroupBoxes(self):
        """Add the 1 groupbox for the Graphene Property Manager.
        """
        self.addGroupBoxSpacer()
        self.pmGroupBox1 = PropMgrGroupBox(self, 
                                           title="Parameters",
                                           titleButton=True)
        self.loadGroupBox1(self.pmGroupBox1)
        
        self.pmGroupBox2 = PropMgrGroupBox(self, 
                                           title="Placement",
                                           titleButton=True)
        self.loadGroupBox2(self.pmGroupBox2)        
                 
        self.addGroupBoxSpacer()
     
              
    def loadGroupBox1(self, pmGroupBox):
        """Load widgets in groubox 1.
        """
        
        self.heightDblSpinBox = \
            PropMgrDoubleSpinBox(pmGroupBox, 
                                label="Height :", 
                                val=10.0, setAsDefault=True,
                                min=1.0, max=200.0, 
                                singleStep=1.0, decimals=1, 
                                suffix=' Angstroms')
        
        self.connect(self.heightDblSpinBox, 
                     SIGNAL("valueChanged(double)"), 
                     self.change_plane_size)
        
        
        self.widthDblSpinBox = \
            PropMgrDoubleSpinBox(pmGroupBox,
                                label="Width :", 
                                val=10.0, setAsDefault=True,
                                min=1.0, max=200.0, 
                                singleStep=1.0, decimals=1, 
                                suffix=' Angstroms')
        
        self.connect(self.widthDblSpinBox, 
                     SIGNAL("valueChanged(double)"), 
                     self.change_plane_size)
    
    def loadGroupBox2(self, pmGroupBox):
        """Load widgets in groubox 2.
        """ 
        self.planePlacementActionGrp = QtGui.QActionGroup(self.win)         
        self.parallelToScreenAction = QtGui.QAction(pmGroupBox)
        self.parallelToScreenAction.setText("Parallel to Screen")                
        self.throughSelectedAtomsAction = QtGui.QAction(pmGroupBox)
        self.throughSelectedAtomsAction.setText("Through Selected Atoms")
        
        for act in self.parallelToScreenAction, self.throughSelectedAtomsAction:
            btn = PropMgrToolButton(pmGroupBox,
                              label='',
                              text = act.text())
            btn.setDefaultAction(act)
            btn.setAutoRaise(True)
            act.setCheckable(True)
            self.planePlacementActionGrp.addAction(act)
            
        self.parallelToScreenAction.setChecked(True)
        
        self.connect(self.planePlacementActionGrp,
                     SIGNAL("triggered(QAction *)"), 
                    self.changePlanePlacement)
                
    def add_whats_this_text(self):
        """What's This text for some of the widgets in the Property Manager.
        """    
        self.heightDblSpinBox.setWhatsThis("""<b>Height</b>
        <p>The height of the Plane in angstroms.
        (up to 200 Angstroms)</p>""")
        
        self.widthDblSpinBox.setWhatsThis("""<b>Width</b>
        <p>The width of the Plane in angstroms.
        (up to 200 Angstroms)</p>""")
        pass
    
    def show_propMgr(self):
        ''' Show the Property manager'''
        self.show()
    
    def change_plane_size(self, gl_update=True):
        '''Slot method to change the Plane's width and height'''
        if not self.resized_from_glpane:
            self.width = self.widthDblSpinBox.value()# motor length
            self.height = self.heightDblSpinBox.value() # motor radius
        if gl_update:
            self.glpane.gl_update()
    
    def update_spinboxes(self):
        '''update the width and height spinboxes(may be some more valued in future)
        ''' 
        #self.resized_from_glpane flag makes sure that the spinbox.valuChanged()
        #signal is not emitted after calling spinbox.setValue. 
        # This flag is used in change_plane_size method.-- Ninad 20070601
        self.resized_from_glpane = True
        self.heightDblSpinBox.setValue(self.height)
        self.widthDblSpinBox.setValue(self.width)
        self.resized_from_glpane = False    
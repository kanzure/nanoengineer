# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad,
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
ninad 20070602: Created.

"""
__author__ = "Ninad"


from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QAction
from PyQt4.Qt import QActionGroup
from PyQt4.Qt import QButtonGroup

from PM.PM_Dialog        import PM_Dialog
from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_ComboBox      import PM_ComboBox
from PM.PM_SpinBox       import PM_SpinBox
from PM.PM_PushButton    import PM_PushButton
from PM.PM_CheckBox      import PM_CheckBox
from PM.PM_RadioButton   import PM_RadioButton
from PM.PM_Constants     import pmRestoreDefaultsButton


class PlanePropertyManager(PM_Dialog):
    ''' UI and slot methods for Plane Property manager'''
    
    # <title> - the title that appears in the property manager header.
    title = "Plane"
    # <pmName> - the name of this property manager. This will be set to
    # the name of the PropMgr (this) object via setObjectName().
    pmName = "pm" + title
    # <iconPath> - full path to PNG file that appears in the header.
    iconPath = "ui/actions/Insert/Reference Geometry/Plane.png"
    
    def __init__(self, plane):
        """Construct the Plane Property Manager.
        """
        self.geometry = plane
        PM_Dialog.__init__( self, self.pmName, self.iconPath, self.title )       
        self.addGroupBoxes()
        self.add_whats_this_text()
        
        msg = "Insert a Plane parallel to the screen. Note: This feature is \
        experimental for Alpha9 and has known bugs"
        
        # This causes the "Message" box to be displayed as well.
        self.MessageGroupBox.insertHtmlMessage(msg, setAsDefault=False)
        
        #self.resized_from_glpane flag makes sure that the spinbox.valuChanged()
        #signal is not emitted after calling spinbox.setValue.
        self.resized_from_glpane = False
        
        #Hide Preview and Restore defaults button for Alpha9
        self.hideTopRowButtons(pmRestoreDefaultsButton)
      
        
    def addGroupBoxes(self):
        """Add the 1 groupbox for the Graphene Property Manager.
        """
        self.pmGroupBox1 = PM_GroupBox(self, 
                                       title="Parameters",
                                       addTitleButton=True)
        
        self.loadGroupBox1(self.pmGroupBox1)
        
        self.pmGroupBox2 = PM_GroupBox(self,
                                       title="Placement",
                                       addTitleButton=True)
        
        self.loadGroupBox2(self.pmGroupBox2)        

              
    def loadGroupBox1(self, pmGroupBox):
        """Load widgets in groubox 1.
        """
        
        self.widthDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox,
                       label        = "Width :",
                       value        = 10.0, 
                       setAsDefault = True,
                       minimum      = 1.0, 
                       maximum      = 200.0,
                       singleStep   = 1.0, 
                       decimals     = 1, 
                       suffix       = ' Angstroms')
        
        self.connect(self.widthDblSpinBox, 
                     SIGNAL("valueChanged(double)"), 
                     self.change_plane_width)
                
        self.heightDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                             label ="Height :",
                             value        = 10.0, 
                             setAsDefault = True,
                             minimum      = 1.0, 
                             maximum      = 200.0,
                             singleStep   = 1.0, 
                             decimals     = 1, 
                             suffix       = ' Angstroms')
        
        self.connect(self.heightDblSpinBox, 
                     SIGNAL("valueChanged(double)"), 
                     self.change_plane_height)
            
        self.aspectRatioCheckBox = \
            PM_CheckBox(pmGroupBox,
                        label       = 'Maintain Aspect Ratio of:' ,
                        labelColumn = 1,
                        spanWidth   = False
                        )
        
        self.connect(self.aspectRatioCheckBox,
                     SIGNAL("stateChanged(int)"),
                     self.toggle_state_aspectRatioSpinBox)

        
        self.aspectRatioSpinBox = \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "",
                              value           =  1,
                              setAsDefault  =  True,
                              minimum       =  0.1,
                              maximum       =  100,
                              singleStep    =  1,
                              decimals      =  1,
                              suffix        =  ' : 1')   
            
        if self.aspectRatioCheckBox.isChecked():
            self.aspectRatioSpinBox.setEnabled(True)
        else:
            self.aspectRatioSpinBox.setEnabled(False)
    
    def loadGroupBox2(self, pmGroupBox):
        '''Load widgets in groubox 2'''
        # Default Projection Groupbox in General tab (as of 070430)
        self.planePlacement_btngrp = QButtonGroup()
        self.planePlacement_btngrp.setExclusive(True)
        
        self.parallelToScreen_btn = PM_RadioButton(
            pmGroupBox, label = "Parallel to Screen" )        
        self.throughSelectedAtoms_btn = PM_RadioButton(
            pmGroupBox, label = "Through Selected Atoms" )        
        self.offsetToPlane_btn = PM_RadioButton(
            pmGroupBox, label = "Offset to a Plane" )
        self.customPlacement_btn = PM_RadioButton(
            pmGroupBox, label = "Custom" )  

        
        objId = 0
        for obj in [self.parallelToScreen_btn,\
                    self.throughSelectedAtoms_btn,\
                    self.offsetToPlane_btn, \
                    self.customPlacement_btn]: 
            
            self.planePlacement_btngrp.addButton(obj)
            self.planePlacement_btngrp.setId(obj, objId)
            objId +=1 
            
        #'Custom' plane placement. Do nothing. Fixes bug 2439
        #(was really a Ui issue)
        if self.planePlacement_btngrp.checkedId() == -1:
            self.customPlacement_btn.setChecked(True)
        
        self.connect(self.planePlacement_btngrp,
                     SIGNAL("buttonClicked(int)"),
                     self.geometry.changePlanePlacement)
    
    def loadGroupBox2_ORIG_WITH_TOOLBUTTONS(self, pmGroupBox):
        """
        loadGroupBox2_ORIG_WITH_TOOLBUTTONS : This uses QActionGroup and
        QToolbuttons to define the varios Plane placement options. We may want 
        to implement this in future instead of radio buttons so keeping this code
        This function is not called. -- ninad 20070604
        """ 
        self.planePlacementActionGrp = QActionGroup(self.win)         
        self.parallelToScreenAction = QAction(pmGroupBox)
        self.parallelToScreenAction.setText("Parallel to Screen")                
        self.throughSelectedAtomsAction = QAction(pmGroupBox)
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
        self.update_spinboxes()
        self.show()   
        self.geometry.updateCosmeticProps(previewing = True)
                
    def change_plane_width(self):
        if self.aspectRatioCheckBox.isChecked():
            self.geometry.width = self.widthDblSpinBox.value()
            self.geometry.height = self.geometry.width/self.aspectRatioSpinBox.value()   
            self.update_spinboxes()
        else:
            self.change_plane_size()
    
    def change_plane_height(self, gl_update=True):
        if self.aspectRatioCheckBox.isChecked():
            self.geometry.height = self.heightDblSpinBox.value() 
            self.geometry.width = self.geometry.height*self.aspectRatioSpinBox.value()
            self.update_spinboxes()
        else:
            self.change_plane_size()
        
    def change_plane_size(self, gl_update=True):
        """Slot method to change the Plane's width and height"""
        if not self.resized_from_glpane:
            self.geometry.width = self.widthDblSpinBox.value()
            self.geometry.height = self.heightDblSpinBox.value() 
        if gl_update:
            self.geometry.glpane.gl_update()
    
    def update_spinboxes(self):
        '''Update the width and height spinboxes(may be some more valued in future)
        Update it *without* generating the valueChanged() signal of the spinbox.
        ''' 
        #self.resized_from_glpane flag makes sure that the spinbox.valuChanged()
        #signal is not emitted after calling spinbox.setValue. 
        # This flag is used in change_plane_size method.-- Ninad 20070601
        self.resized_from_glpane = True
        self.heightDblSpinBox.setValue(self.geometry.height)
        self.widthDblSpinBox.setValue(self.geometry.width)
        self.geometry.glpane.gl_update()
        self.resized_from_glpane = False
    
    def toggle_state_aspectRatioSpinBox(self, val):
        self.aspectRatioSpinBox.setEnabled(val)
        

# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
The ExtrudePropertyManager class provides the Property Manager for the
B{Extrude mode}.  The UI is defined in L{Ui_ExtrudePropertyManager}

History: 

ninad 2007-01-10: Split the ui code out of extrudeMode while converting 
extrude dashboard to extrude property manager. 
ninad 2007-07-25: code cleanup to create a propMgr object for extrude mode. Also
moved many ui helper methods defined globally in extrudeMode.py to this class.

"""

import math
from PyQt4.Qt import SIGNAL
from commands.Extrude.Ui_ExtrudePropertyManager import Ui_ExtrudePropertyManager


class ExtrudePropertyManager(Ui_ExtrudePropertyManager):
    """
    The ExtrudePropertyManager class provides the Property Manager for the
    B{Extrude mode}.  The UI is defined in L{Ui_ExtrudePropertyManager}
    """
     
    def __init__(self, parentMode):
        """
        Constructor for the B{Extrude} property manager.
        
        @param parentMode: The parent mode where this Property Manager is used
        @type  parentMode: L{depositMode} 
        """
        self.extrudeSpinBox_circle_n = None
            # REVIEW: I suspect extrudeSpinBox_circle_n is obsolete
            # and can be completely removed. [bruce 080725 comment]
        self.suppress_valuechanged = 0
        
        Ui_ExtrudePropertyManager.__init__(self, parentMode)
        
        self.updateMessage()        
        
    
    def ok_btn_clicked(self):
        """
        Calls MainWindow.toolsDone to exit the current mode. 
        @attention: this method needs to be renamed. (this should be done in 
        PM_Dialog)
        """
        self.w.toolsDone()
    
    def cancel_btn_clicked(self):
        """
        Calls MainWindow.toolsDone to exit the current mode. 
        @attention: this method needs to be renamed. (this should be done in 
        PM_Dialog)
        """
        self.w.toolsCancel()
        
    def connect_or_disconnect_signals(self, connect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        @see: L{extrudeMode.connect_or_disconnect_signals} where this is called
        """
        if connect:
            change_connect = self.w.connect
        else:
            change_connect = self.w.disconnect
        
        # Connect or disconnect widget signals to slots
        
        change_connect(self.extrudeSpinBox_n,
                       SIGNAL("valueChanged(int)"),
                       self.parentMode.spinbox_value_changed)
        
        change_connect(self.extrudeSpinBox_x,
                       SIGNAL("valueChanged(double)"),
                       self.parentMode.spinbox_value_changed)
        
        change_connect(self.extrudeSpinBox_y,
                       SIGNAL("valueChanged(double)"),
                       self.parentMode.spinbox_value_changed)
        
        change_connect(self.extrudeSpinBox_z,
                       SIGNAL("valueChanged(double)"),
                       self.parentMode.spinbox_value_changed)
        
        change_connect(self.extrudeSpinBox_length,
                       SIGNAL("valueChanged(double)"),
                       self.parentMode.length_value_changed)
        
        slider = self.extrudeBondCriterionSlider
        
        change_connect(slider, 
                       SIGNAL("valueChanged(int)"), 
                       self.parentMode.slider_value_changed)
        
        if self.extrudeSpinBox_circle_n and self.parentMode.is_revolve: ###k??
            change_connect(self.extrudeSpinBox_circle_n,
                           SIGNAL("valueChanged(int)"),
                           self.parentMode.circle_n_value_changed)
            
        change_connect(self.extrude_productTypeComboBox,
                       SIGNAL("activated(int)"), 
                       self.parentMode.ptype_value_changed)
            
                
    def set_extrude_controls_xyz(self, (x, y, z) ):
        self.set_extrude_controls_xyz_nolength((x, y, z))
        self.update_length_control_from_xyz()
    
    def set_extrude_controls_xyz_nolength(self, (x, y, z) ):      
        self.extrudeSpinBox_x.setValue(x)
        self.extrudeSpinBox_y.setValue(y)
        self.extrudeSpinBox_z.setValue(z)    
    
    def set_controls_minimal(self): 
        #e would be better to try harder to preserve xyz ratio
        ll = 0.1 # kluge, but prevents ZeroDivisionError
        x = y = 0.0
        z = ll
        self.call_while_suppressing_valuechanged( 
            lambda: self.set_extrude_controls_xyz_nolength((x, y, z) ) )
        
        self.call_while_suppressing_valuechanged( 
            lambda: self.extrudeSpinBox_length.setValue(ll) )
        
        # ZeroDivisionError after user sets xyz each to 0 by typing in them
    
        
    def get_extrude_controls_xyz(self):
        x = self.extrudeSpinBox_x.value()
        y = self.extrudeSpinBox_y.value()
        z = self.extrudeSpinBox_z.value()
        return (x,y,z)
    
    def update_length_control_from_xyz(self):
        x, y, z = self.get_extrude_controls_xyz()
        ll = math.sqrt(x*x + y*y + z*z)
        if ll < 0.1: # prevent ZeroDivisionError
            self.set_controls_minimal()
            return
        
        self.call_while_suppressing_valuechanged( 
            lambda: self.extrudeSpinBox_length.setValue(ll) )
        
    def update_xyz_controls_from_length(self):
        x, y, z = self.get_extrude_controls_xyz()
        ll = math.sqrt(x*x + y*y + z*z)
        if ll < 0.1: # prevent ZeroDivisionError
            self.set_controls_minimal()
            return
        length = self.extrudeSpinBox_length.value()
        rr = float(length) / ll
        self.call_while_suppressing_valuechanged( 
            lambda: self.set_extrude_controls_xyz_nolength( 
                (x*rr, y*rr, z*rr) ) )

    def call_while_suppressing_valuechanged(self, func):
        old_suppress_valuechanged = self.suppress_valuechanged
        self.suppress_valuechanged = 1
        try:
            res = func()
        finally:
            self.suppress_valuechanged = old_suppress_valuechanged
        return res
    
    def set_bond_tolerance_and_number_display(self, tol, nbonds = -1): 
        #e -1 indicates not yet known ###e '?' would look nicer 
        self.extrudeBondCriterionLabel.setText(\
            self.lambda_tol_nbonds(tol,nbonds))
    
    def set_bond_tolerance_slider(self, tol):
        # this will send signals!
        self.extrudeBondCriterionSlider.setValue(int(tol * 100)) 
            
    def get_bond_tolerance_slider_val(self):
        ival = self.extrudeBondCriterionSlider.value()
        return ival / 100.0
    
    def lambda_tol_nbonds(self, tol, nbonds):
        if nbonds == -1:
            nbonds_str = "?"
        else:
            nbonds_str = "%d" % (nbonds,)
        tol_str = ("      %d" % int(tol * 100.0))[-3:]
        # fixed-width (3 digits) but using initial spaces
        # (doesn't have all of desired effect, due to non-fixed-width font)
        tol_str = tol_str + "%"
        return "Tolerance: %s => %s bonds" % (tol_str, nbonds_str)
        
    def updateMessage(self):
        """
        Updates the message box with an informative message.
        """
                
        numCopies = self.extrudeSpinBox_n.value() - 1
        
        if self.parentMode.product_type == "straight rod":
            msg = "Drag one of the " + str(numCopies) + " copies on the right \
                to position them. Bondpoints will highlight in blue and green \
                pairs whenever bonds can be formed between them."
        else:
            msg = "Use the spinboxes below to position the copies. \
                Bondpoints will highlight in blue and green pairs \
                whenever bonds can be formed between them."

        self.MessageGroupBox.insertHtmlMessage( msg, setAsDefault  =  True )

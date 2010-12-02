# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$


History: 

ninad 20070110: Split the ui code out of extrudeMode while converting 
extrude dashboard to extrude property manager. 
ninad 20070725: code cleanup to create a propMgr object for extrude mode. Also
moved many ui helper methods defined globally in extrudeMode.py to this class.

"""

from PyQt4 import QtCore, QtGui
from Ui_ExtrudePropertyManager import Ui_ExtrudePropertyManager
from PropertyManagerMixin import PropertyManagerMixin, pmSetPropMgrIcon, pmSetPropMgrTitle
from PyQt4.Qt import Qt, SIGNAL, QWhatsThis

import math


class ExtrudePropertyManager(QtGui.QWidget, 
                             PropertyManagerMixin, 
                             Ui_ExtrudePropertyManager):
    
    # <title> - the title that appears in the property manager header.
    title = "Extrude"
    # <iconPath> - full path to PNG file that appears in the header.
    iconPath = "ui/actions/Insert/Features/Extrude.png"
    
    def __init__(self, parentMode):
	self.parentMode = parentMode
	self.w = self.parentMode.w
	
        QtGui.QWidget.__init__(self)
        
        self.setupUi(self)
        self.retranslateUi(self)
        
        # setupUi() did not add the icon or title. We do that here.
	pmSetPropMgrIcon( self, self.iconPath )
        pmSetPropMgrTitle( self, self.title )
	
        self.extrudeSpinBox_circle_n = None 
        
        self.suppress_valuechanged = 0
		
        self.updateMessage()
        
        self.add_whats_this_text()
    
    def show_propMgr(self):
	"""
	Show the Extrude Property Manager
	"""
	self.openPropertyManager(self)
    
    def connect_or_disconnect_signals(self, connect):
	if connect:
            change_connect = self.w.connect
        else:
            change_connect = self.w.disconnect
	
	# Connect or disconnect widget signals to slots
        change_connect(self.productSpec_groupBoxButton, 
                     SIGNAL("clicked()"),
                     self.toggle_productSpec_groupBox)
        change_connect(self.extrudeDirection_groupBoxButton, 
                     SIGNAL("clicked()"),
                     self.toggle_extrudeDirection_groupBox)
        change_connect(self.advancedOptions_groupBoxButton, 
                     SIGNAL("clicked()"),
                     self.toggle_advancedOptions_groupBox)
	
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
	    
	    
    def toggle_productSpec_groupBox(self):
        self.toggle_groupbox(self.productSpec_groupBoxButton,
                             self.productSpec_groupBoxWidget)
                        
    def toggle_extrudeDirection_groupBox(self):
        self.toggle_groupbox(self.extrudeDirection_groupBoxButton)
    
    def toggle_advancedOptions_groupBox(self):
        self.toggle_groupbox(self.advancedOptions_groupBoxButton, 
                             self.advancedOptions_groupBoxWidget)
    
    def set_extrude_controls_xyz(self, (x,y,z) ):
	self.set_extrude_controls_xyz_nolength((x,y,z))
	self.update_length_control_from_xyz()
    
    def set_extrude_controls_xyz_nolength(self, (x,y,z) ):	
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
	### obs comment?: this is not working as I expected, but it does seem to prevent that
	# ZeroDivisionError after user sets xyz each to 0 by typing in them
    
        
    def get_extrude_controls_xyz(self):
	x = self.extrudeSpinBox_x.value()
	y = self.extrudeSpinBox_y.value()
	z = self.extrudeSpinBox_z.value()
	return (x,y,z)
    
    def update_length_control_from_xyz(self):
	x,y,z = self.get_extrude_controls_xyz()
	ll = math.sqrt(x*x + y*y + z*z)
	if ll < 0.1: # prevent ZeroDivisionError
	    self.set_controls_minimal()
	    return
	
	self.call_while_suppressing_valuechanged( 
	    lambda: self.extrudeSpinBox_length.setValue(ll) )
	
    def update_xyz_controls_from_length(self):
	x,y,z = self.get_extrude_controls_xyz()
	ll = math.sqrt(x*x + y*y + z*z)
	if ll < 0.1: # prevent ZeroDivisionError
	    self.set_controls_minimal()
	    return
	length = self.extrudeSpinBox_length.value()
	rr = float(length) / ll
	self.call_while_suppressing_valuechanged( 
	    lambda: self.set_extrude_controls_xyz_nolength( 
		(x * rr, y * rr, z * rr) ) )

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
	self.extrudeBondCriterionLabel.setText(self.lambda_tol_nbonds(tol,nbonds))
    
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
	tol_str = ("      %d" % int(tol*100.0))[-3:]
	# fixed-width (3 digits) but using initial spaces
	# (doesn't have all of desired effect, due to non-fixed-width font)
	tol_str = tol_str + "%"
	return "Tolerance: %s => %s bonds" % (tol_str,nbonds_str)
	
    def updateMessage(self):
        """Updates the message box with an informative message.
        """
		
	numCopies = self.extrudeSpinBox_n.value() - 1
	
	if self.parentMode.product_type == "straight rod":
	    msg = "Drag one of the " + str(numCopies) + " copies on the right to \
	        position them. Bondpoints will highlight in blue and green pairs \
	        whenever bonds can be formed between them."
	else:
	    msg = "Use the spinboxes below to position the copies. \
	        Bondpoints will highlight in blue and green pairs \
	        whenever bonds can be formed between them."

        self.MessageGroupBox.insertHtmlMessage( msg, setAsDefault  =  True )
	
    def add_whats_this_text( self ):
        """What's This text for some of the widgets in the 
        Extrude Property Manager.
        """
	self.extrude_productTypeComboBox.setWhatsThis(
            """<b>Final product</b>
            <p>The type of product to create. Options are:</p>
	    <p><b>Rod</b>: a straight rod.<br>
	    <b>Ring</b>: a closed ring.
            </p>""")
	
	self.extrudeSpinBox_n.setWhatsThis(
            """<b>Number of copies</b>
            <p>The total number of copies, including the originally selected 
	    chunk(s).
            </p>""")
	
	self.extrudePref1.setWhatsThis(
	    """<b>Show Entire Model</b>
            <p>Normally, only the selection and their copies are displayed 
	    during the Extrude command. Checking this option displays 
	    everything in the current model.
            </p>""")
	    
	self.extrudePref3.setWhatsThis(
	    """<b>Make Bonds</b>
            <p>When checked, bonds will be made between pairs of bondpoints
	    highlighted in blue and green after clicking <b>Done</b>.
            </p>""")
	
	self.extrudeBondCriterionSlider.setWhatsThis(
            """<b>Tolerance slider</b>
            <p>Sets the bond criterion tolerance. The larger the tolerance 
	    value, the further bonds will be formed between pairs of 
	    bondpoints.
            </p>""")
	
	self.extrudePrefMergeSelection.setWhatsThis(
	    """<b>Merge Selection</b>
            <p>Merges the selected chunks into a single chunk after 
	    clicking <b>Done</b>.
            </p>""")
	    
	self.extrudePref4.setWhatsThis(
	    """<b>Merge Copies</b>
            <p>When checked, copies are merged with the original chunk
	    after clicking <b>Done</b>.
            </p>""")
	
	self.extrudeSpinBox_length.setWhatsThis(
            """<b>Total Offset</b>
            <p>The total offset distance between copies.
            </p>""")
	
	self.extrudeSpinBox_x.setWhatsThis(
	    """<b>X Offset</b>
            <p>The X offset distance between copies.
            </p>""")
	    
	self.extrudeSpinBox_y.setWhatsThis(
	    """<b>Y Offset</b>
            <p>The Y offset distance between copies.
            </p>""")
	    
	self.extrudeSpinBox_z.setWhatsThis(
	    """<b>Z Offset</b>
            <p>The Z offset distance between copies.
            </p>""")
	
	return

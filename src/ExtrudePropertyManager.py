# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtCore, QtGui
from Ui_ExtrudePropertyManager import Ui_ExtrudePropertyManager
from PropertyManagerMixin import PropertyManagerMixin, pmSetPropMgrIcon, pmSetPropMgrTitle
from PyQt4.Qt import Qt, SIGNAL, QWhatsThis

class ExtrudePropertyManager(QtGui.QWidget, 
                             PropertyManagerMixin, 
                             Ui_ExtrudePropertyManager):
    
    # <title> - the title that appears in the property manager header.
    title = "Extrude"
    # <iconPath> - full path to PNG file that appears in the header.
    iconPath = "ui/actions/Insert/Features/Extrude.png"
    
    def __init__(self):
        QtGui.QWidget.__init__(self)
        
        self.setupUi(self)
        self.retranslateUi(self)
        
        # setupUi() did not add the icon or title. We do that here.
	pmSetPropMgrIcon( self, self.iconPath )
        pmSetPropMgrTitle( self, self.title )
	
        self.extrudeSpinBox_circle_n = None ##@@@ This was earlier set in do_what_Mainwindow_.should_do
        ##we are not calling that function anymore so setting it here
        
        # Connect widget signals to slots
        self.connect(self.productSpec_groupBoxButton, 
                     SIGNAL("clicked()"),
                     self.toggle_productSpec_groupBox)
        self.connect(self.extrudeDirection_groupBoxButton, 
                     SIGNAL("clicked()"),
                     self.toggle_extrudeDirection_groupBox)
        self.connect(self.advancedOptions_groupBoxButton, 
                     SIGNAL("clicked()"),
                     self.toggle_advancedOptions_groupBox)
        
        self.updateMessage()
        
        self.add_whats_this_text()
	
    def toggle_productSpec_groupBox(self):
        self.toggle_groupbox(self.productSpec_groupBoxButton,
                             self.productSpec_groupBoxWidget)
                        
    def toggle_extrudeDirection_groupBox(self):
        self.toggle_groupbox(self.extrudeDirection_groupBoxButton)
    
    def toggle_advancedOptions_groupBox(self):
        self.toggle_groupbox(self.advancedOptions_groupBoxButton, 
                             self.advancedOptions_groupBoxWidget)
	
    def updateMessage(self):
        """Updates the message box with an informative message.
        """
		
	numCopies = self.extrudeSpinBox_n.value() - 1
	
	if self.product_type == "straight rod":
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

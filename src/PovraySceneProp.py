# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
'''
PovraySceneProp.py - the PovraySceneProp class, including all methods needed by the POV-Ray Scene dialog.

$Id$

History:

mark 060602 - Created for NFR: "Insert > POV-Ray Scene". Went to school on Will\'s DNAGenerator 
    and GeneratorBaseClass code.

'''
__author__ = "Mark"

from qt import QDoubleValidator, SIGNAL, QDialog
from PovrayScenePropDialog import PovrayScenePropDialog
from GeneratorBaseClass import GeneratorBaseClass
from HistoryWidget import greenmsg
from widgets import double_fixup
from Utility import genViewNum

class PovraySceneProp(GeneratorBaseClass, PovrayScenePropDialog):

    cmd = greenmsg("Insert POV-Ray Scene: ")
    sponsor_keyword = 'DNA'
    prefix = 'POV-Ray Scene-'   # used for genViewNum

    def __init__(self, win):
        PovrayScenePropDialog.__init__(self, win)  # win is parent.
        GeneratorBaseClass.__init__(self, win)
        self.win = win
        self.glpane = self.win.glpane
        self.pvs = None
        self.previousParams = None
        # Validator for the aspect ratio linedit widget.
        self.validator = QDoubleValidator(self)
        # Range of aspect ratio (0.25-4.0, 3 decimal places)
        self.validator.setRange(0.25, 4.0, 3)
        self.aspect_ratio_linedit.setValidator(self.validator)
        self.aspect_ratio_str = str(self.aspect_ratio_linedit.text())
        self.aspect_ratio_linedit.setReadOnly(True) # Read-only for now, maybe forever. Mark 060602.

    def _create_new_name(self):
        pass

    def show(self, pvs=None):
        '''Show the Properties Manager dialog. If <pvs> is supplied, get the parameters from
        it and load the dialog widgets.
        '''
        import Utility
        self.maintain_aspect_ratio_checkbox.setChecked(False) # Needed. Mark 060612.

        if pvs:
            self.name, self.width, self.height, self.output_type = pvs.get_parameters()
            self.struct = pvs
        else:
            # HERE is where we create the new name, we need it early so we can
            # put it in the name_linedit. Nobody else needs something like that.
            #if not self.name:
            self._ViewNum = Utility.ViewNum
            self.name = genViewNum(self.prefix)
            self.width = int(self.glpane.width)
            self.height = int(self.glpane.height)
            self.output_type = 'PNG'

        self.name_linedit.setText(self.name)
        self.image_format_combox.setCurrentText(self.output_type.upper())
        self.width_spinbox.setValue(self.width) # Generates signal.
        self.height_spinbox.setValue(self.height) # Generates signal.
        self.maintain_aspect_ratio_checkbox.setChecked(True)
        self.update_aspect_ratio()
        self.previousParams = self.gather_parameters()
        PovrayScenePropDialog.show(self)
        
    def gather_parameters(self):
        '''Return the current parameter values from the widgets.
        '''
        name = str(self.name_linedit.text())
        width = self.width_spinbox.value()
        height = self.height_spinbox.value()
        output_type = str(self.image_format_combox.currentText()).lower()
        return (name, width, height, output_type)

    def build_struct(self, params):
        if self.pvs: self.action = 'added'
        else: self.action = 'updated'
        
        from PovrayScene import PovrayScene
        self.pvs = pvs = PovrayScene(self.win.assy, params)
        return pvs
    
    def preview_btn_clicked(self):
        '''Overrides GeneratorBaseClass.preview_btn_click().
        '''
        self.remove_struct()
        params = self.gather_parameters()
        self.struct = self.build_struct(params)
        self.win.assy.addnode(self.struct)
        self.win.win_update() # includes mt_update
        self.struct.render_image()
        
    def cancel_btn_clicked(self):
        '''Overrides GeneratorBaseClass.cancel_btn_clicked().
        '''
        if self.struct:
            self.struct.set_parameters(self.previousParams)
            QDialog.accept(self)
        else:
            GeneratorBaseClass.cancel_btn_clicked(self)
    
# Property manager widget slots.

    def change_width(self, width):
        'Slot for Width spinbox'
        self.width = width
        self.update_height()
        
    def update_height(self):
        'Updates height when width changes'
        if self.maintain_aspect_ratio_checkbox.isChecked():
            if self.aspect_ratio:
                self.height = int (self.width / self.aspect_ratio)
            self.disconnect(self.height_spinbox,SIGNAL("valueChanged(int)"),self.change_height)
            self.height_spinbox.setValue(self.height)
            self.connect(self.height_spinbox,SIGNAL("valueChanged(int)"),self.change_height)
        else:
            self.update_aspect_ratio()
    
    def change_height(self, height):
        'Slot for Height spinbox'
        self.height = height
        self.update_width()
        
    def update_width(self):
        'Updates width when height changes'
        if self.maintain_aspect_ratio_checkbox.isChecked():
            if self.aspect_ratio:
                self.width = int (self.height * self.aspect_ratio)
            self.disconnect(self.width_spinbox,SIGNAL("valueChanged(int)"),self.change_width)
            self.width_spinbox.setValue(self.width)
            self.connect(self.width_spinbox,SIGNAL("valueChanged(int)"),self.change_width)
        else:
            self.update_aspect_ratio()
            
    def update_aspect_ratio(self):
        'Updates the aspect ratio value when the width or height changes.'
        self.aspect_ratio = float(self.width) / float(self.height)
        #print "Aspect Ratio float value=", self.aspect_ratio
        self.aspect_ratio_str = "%.3f" % self.aspect_ratio
        self.aspect_ratio_linedit.setText(self.aspect_ratio_str)
        self.aspect_ratio_str = str(self.aspect_ratio_linedit.text())
        
    def aspect_ratio_fixup(self):
        '''Slot for the Aspect Ratio linedit widget.
        This gets called each time a user types anything into the widget.
        This does not get called since the widget has been set to readonly in __init__(). Mark 060602.
        '''
        self.aspect_ratio_str = double_fixup(self.validator, self.aspect_ratio_linedit.text(), self.aspect_ratio_str)
        self.aspect_ratio_linedit.setText(self.aspect_ratio_str)
        #ar = float(str(self.aspect_ratio_str))
        #print "Aspect Ratio =", ar
        
# Property Manager button slots

    def toggle_grpbtn_1(self):
        'Slot for first groupbox toggle button'
        self.toggle_groupbox(self.grpbtn_1, self.line2,
                             self.name_linedit)

    def toggle_grpbtn_2(self):
        'Slot for second groupbox toggle button'
        self.toggle_groupbox(self.grpbtn_2, self.line2_3,
                             self.maintain_aspect_ratio_checkbox,
                             self.image_format_label, self.image_format_combox,
                             self.width_label, self.width_spinbox,
                             self.height_label, self.height_spinbox,
                             self.aspect_ratio_label, self.aspect_ratio_linedit, self.to_1_label)

# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
'''
PovraySceneProp.py - the PovraySceneProp class, including all methods needed by the POV-Ray Scene dialog.

$Id$

History:

mark 060602 - Created for NFR: "Insert > POV-Ray Scene". Went to school on Will\'s DNAGenerator 
    and GeneratorBaseClass code.

'''
__author__ = "Mark"

from qt import Qt, QApplication, QCursor, QDialog, QDoubleValidator, SIGNAL, QWhatsThis, QIconSet, QPixmap
from PovrayScenePropDialog import PovrayScenePropDialog
from GeneratorBaseClass import GroupButtonMixin
from HistoryWidget import greenmsg, redmsg
from Sponsors import findSponsor
from widgets import double_fixup
from Utility import genViewNum
import os
import env

cmd = greenmsg("Insert POV-Ray Scene: ")

class PovraySceneProp(PovrayScenePropDialog, GroupButtonMixin):

    def __init__(self, win):
        PovrayScenePropDialog.__init__(self, win)  # win is parent.
        self.win = win
        self.glpane = self.win.glpane
        self.pvs = None
        self.previousParams = None
        self.sponsor = sponsor = findSponsor('DNA') # Any sponsor will do for now.
        sponsor.configureSponsorButton(self.sponsor_btn)
        
        # Validator for the aspect ratio linedit widget.
        self.validator = QDoubleValidator(self)
        # Range of aspect ratio (0.25-4.0, 3 decimal places)
        self.validator.setRange(0.25, 4.0, 3)
        self.aspect_ratio_linedit.setValidator(self.validator)
        self.aspect_ratio_str = str(self.aspect_ratio_linedit.text())
        self.aspect_ratio_linedit.setReadOnly(True) # Read-only for now, maybe forever. Mark 060602.
    
    def setup(self, pvs=None):
        '''Show Comment dialog with currect comment text. 
        <pvs> - the POV-Ray Scene node object.
        '''
        self.pvs = pvs
        
        if self.pvs: 
            self.new_pvs = False
            self.name, self.width, self.height, self.output_type = self.pvs.get_parameters()
        else:
            # Default parameters
            self.new_pvs = True
            self.name = genViewNum("POV-Ray Scene-")
            self.width = int(self.glpane.width)
            self.height = int(self.glpane.height)
            self.output_type = 'png'
        
        self.load_parameters_in_widgets(self.get_parameters())
        self.previousParams = self.gather_parameters_from_widgets()
            
        QDialog.exec_loop(self)
        
    ###### Private methods ###############################
    
    def get_parameters(self):
        return (self.name, self.width, self.height, self.output_type)
    
    def load_parameters_in_widgets(self, params):
        '''Load the list of parameters in <params> into the widgets in the dialog.
        '''
        self.name, self.width, self.height, self.output_type = params
        
        self.name_linedit.setText(self.name)
        self.aspect_ratio = None # This must come before loading values in width and height spinboxes.
        self.width_spinbox.setValue(self.width) # Generates signal.
        self.height_spinbox.setValue(self.height) # Generates signal.
        self.update_aspect_ratio()
        
    def gather_parameters_from_widgets(self):
        '''Return the current parameter values from the widgets.
        '''
        name = str(self.name_linedit.text())
        width = self.width_spinbox.value()
        height = self.height_spinbox.value()
        output_type = str(self.image_format_combox.currentText()).lower()
        return (name, width, height, output_type)
    
    def create_pvs_or_update_params(self, render_image=True):
        '''Create POV-Ray Scene or, if a POV-Ray Scene already exists, update its parameters.
        Renders image of POV-Ray Scene only when <render_image> is True (default).
        '''
        params =  self.gather_parameters_from_widgets()
        
        if not self.pvs:
            try:
                from PovrayScene import PovrayScene
                self.pvs = PovrayScene(self.win.assy, params)
                self.win.assy.addnode(self.pvs)
                self.win.mt.mt_update()
                self.action = 'added'
            except Exception, e:
                env.history.message(cmd + redmsg(" - ".join(map(str, e.args))))
                self.remove_pvs()
                return
        else:
            if params != self.previousParams:
                self.pvs.set_parameters(params)
                self.previousParams = params
                self.action = 'updated'
            else:
                # Nothing changes, so nothing happened.
                self.action=None
        
        if render_image:
            self.pvs.render_image()
            
        self.done_history_msg()
            
    def remove_pvs(self):
        '''Removes the POV-Ray Scene if it exists.
        '''
        if self.pvs:
            self.pvs.kill()
            self.win.mt.mt_update()
            self.pvs = None
    
    def render_image_from_pvs_OBS(self):
        '''Create a POV-Ray Scene and renders an image.
        '''
        try:
            self.create_pvs_or_update_params()
            self.pvs.render_image()
            self.done_history_msg()
        except Exception, e:
            env.history.message(cmd + redmsg(" - ".join(map(str, e.args))))
            self.remove_pvs()
        
# Property manager widget slots.

    def render_and_save_image(self):
        '''Slot for "Render and Save Image" button.
        Renders image from POV-Ray Scene file and creates an Image node. NIY. Mark 060603.
        '''
        self.create_pvs_or_update_params()
        
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
        
    def done_history_msg(self):
        'Prints history message if some action was performed (i.e. action != None).'
        if self.action:
            env.history.message(cmd + "%s %s." % (self.pvs.name, self.action))
        
# Property Manager button slots

    def open_sponsor_homepage(self):
        'Slot for the Sponsor button'
        self.sponsor.wikiHelp()
    
    def ok_btn_clicked(self):
        'Slot for the OK button'
        self.create_pvs_or_update_params(render_image=False)
        self.pvs = None
        QDialog.accept(self)

    def cancel_btn_clicked(self):
        '''Slot for the Cancel button(s).
        If this is a new POV-Ray Scene, delete it.
        '''
        if self.new_pvs:
            self.remove_pvs()
        self.pvs=None
        QDialog.reject(self)
        
    def restore_defaults_btn_clicked(self):
        'Slot for the Restore Defaults button'
        self.load_parameters_in_widgets(self.previousParams)
    
    def preview_btn_clicked(self):
        'Slot for the Preview button'
        self.create_pvs_or_update_params()
    
    def whatsthis_btn_clicked(self):
        "Slot for the What's This button"
        QWhatsThis.enterWhatsThisMode()

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
                             self.aspect_ratio_label, self.aspect_ratio_linedit, self.to_1_label,
                             self.render_and_save_image_btn)

    def close(self, e=None):
        '''Called when the user closes dialog by clicking the 'X' button on the dialog title bar.
        '''
        try:
            self.cancel_btn_clicked()
            return True
        except:
            return False

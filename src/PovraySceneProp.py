# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
'''
PovraySceneProp.py - the PovraySceneProp class, including all methods needed by the POV-Ray Scene dialog.

$Id$

History:

mark 060602 - Created for NFR: "Insert > POV-Ray Scene". Went to school on Will's DNAGenerator 
    and GeneratorBaseClass code.

'''
__author__ = "Mark"

from qt import Qt, QApplication, QCursor, QDialog, QDoubleValidator, SIGNAL, QWhatsThis
from PovrayScenePropDialog import PovrayScenePropDialog
from HistoryWidget import greenmsg, redmsg
from Sponsors import findSponsor
from widgets import double_fixup
from Utility import genViewNum
import os
import env

cmd = greenmsg("Insert POV-Ray Scene: ")

class PovraySceneProp(PovrayScenePropDialog):

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
            self.name, self.width, self.height, self.output_type = self.pvs.get_parameters()
        else: 
            # Default parameters
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
    
    def create_pvs(self):
        '''Create POV-Ray Scene. Caller is responsible for updating the model tree.
        '''
        params =  self.gather_parameters_from_widgets()
        
        if not self.pvs:
            from PovrayScene import PovrayScene
            self.pvs = pvs = PovrayScene(self.win.assy, params)
            part = self.win.assy.part
            part.ensure_toplevel_group()
            part.topnode.addchild(pvs)
            self.action = 'added'
        else:
            if params != self.previousParams:
                self.pvs.set_parameters(params)
                self.previousParams = params
                self.action = 'updated'
            else:
                # Nothing changes, so nothing happened.
                self.action=None
            
    def remove_pvs(self):
        '''Removes the POV-Ray Scene. Caller is responsible for updating the model tree.
        '''
        if self.pvs != None:
            part = self.win.assy.part
            part.ensure_toplevel_group()
            self.pvs.kill()
            self.pvs = None
    
    def render_image_from_pvs(self, discard_image_after_render=True):
        '''Create a POV-Ray Scene and renders an image.
        If <discard_image_after_render> is True, the POV-Ray Scene and image are deleted
        (i.e. when the user clicks the Preview button).
        '''
        try:
            self.create_pvs()
            self.pvs.render_image()
            if discard_image_after_render:
                self.remove_pvs()
            else:
                self.done_history_msg()
        except Exception, e:
            env.history.message(cmd + redmsg(" - ".join(map(str, e.args))))
            self.remove_pvs()
        self.win.mt.mt_update()
        
    def render_and_save_image(self):
        'Slot for "Render and Save Image" button.'
        self.render_image_from_pvs(discard_image_after_render=False)
        
# Property manager widget slots.

    def update_height_when_width_changes(self, width):
        'Slot for Width spinbox'
        self.width = width
        if self.maintain_aspect_ratio_checkbox.isChecked():
            if self.aspect_ratio:
                self.height = int (self.width / self.aspect_ratio)
            self.disconnect(self.height_spinbox,SIGNAL("valueChanged(int)"),self.update_width_when_height_changes)
            self.height_spinbox.setValue(self.height)
            self.connect(self.height_spinbox,SIGNAL("valueChanged(int)"),self.update_width_when_height_changes)
        else:
            self.update_aspect_ratio()
        
    def update_width_when_height_changes(self, height):
        'Slot for Height spinbox'
        self.height = height
        if self.maintain_aspect_ratio_checkbox.isChecked():
            if self.aspect_ratio:
                self.width = int (height * self.aspect_ratio)
            self.disconnect(self.width_spinbox,SIGNAL("valueChanged(int)"),self.update_height_when_width_changes)
            self.width_spinbox.setValue(self.width)
            self.connect(self.width_spinbox,SIGNAL("valueChanged(int)"),self.update_height_when_width_changes)
        else:
            self.update_aspect_ratio()
            
    def update_aspect_ratio(self):
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
        if self.action:
            env.history.message(cmd + "%s %s." % (self.pvs.name, self.action))
        
# Property Manager button slots

    def open_sponsor_homepage(self):
        'Slot for the Sponsor button'
        self.sponsor.wikiHelp()
    
    def ok_btn_clicked(self):
        'Slot for the OK button'
        try:
            self.create_pvs()
            self.done_history_msg()
            self.pvs = None
        except Exception, e:
            env.history.message(cmd + redmsg(" - ".join(map(str, e.args))))
            self.remove_pvs()
        self.win.mt.mt_update()
        QDialog.accept(self)

    def cancel_btn_clicked(self):
        'Slot for the Cancel button(s)'
        self.pvs=None
        QDialog.reject(self)
        
    def restore_defaults_btn_clicked(self):
        'Slot for the Restore Defaults button'
        self.load_parameters_in_widgets(self.previousParams)
    
    def preview_btn_clicked(self):
        'Slot for the Preview button'
        self.render_image_from_pvs()
    
    def whatsthis_btn_clicked(self):
        '''Slot for the What's This button'''
        QWhatsThis.enterWhatsThisMode()

    def close(self, e=None):
        '''Called when the user closes dialog by clicking the 'X' button on the dialog title bar.
        '''
        try:
            self.cancel_btn_clicked()
            return True
        except:
            return False
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
from HistoryWidget import greenmsg, redmsg
from Sponsors import findSponsor
from widgets import double_fixup
from Utility import genViewNum
import os
import env

_up_arrow = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d\x49\x48\x44\x52" \
    "\x00\x00\x00\x10\x00\x00\x00\x10\x08\x02\x00\x00\x00\x90\x91\x68" \
    "\x36\x00\x00\x00\x06\x62\x4b\x47\x44\x00\xff\x00\xff\x00\xff\xa0" \
    "\xbd\xa7\x93\x00\x00\x00\x09\x70\x48\x59\x73\x00\x00\x0b\x13\x00" \
    "\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x07\x74\x49\x4d\x45" \
    "\x07\xd6\x06\x03\x03\x21\x26\xc9\x92\x21\x9b\x00\x00\x00\x10\x74" \
    "\x45\x58\x74\x43\x6f\x6d\x6d\x65\x6e\x74\x00\x4e\x61\x6e\x6f\x74" \
    "\x75\x62\x65\xa3\x8c\x3b\xec\x00\x00\x00\xda\x49\x44\x41\x54\x28" \
    "\xcf\xb5\x92\x41\x0e\x82\x30\x10\x45\x5b\xe3\x01\x24\x14\x69\x39" \
    "\x01\x3d\x83\x6c\x24\xdc\xc0\xb0\x31\x5c\x8f\x78\x8b\x76\x16\x70" \
    "\x95\xb2\x01\x71\xcd\xa2\x75\x51\x6d\x1a\x40\x23\x0b\xff\x6e\x32" \
    "\xef\xb7\x99\x3f\x83\x55\xa7\xd0\x16\xed\xd0\x46\xed\xfd\xa2\x69" \
    "\x9b\x25\x91\x9d\xb2\x75\x43\xd3\x36\xe5\xa5\x5c\x1a\xea\x5b\x9d" \
    "\x9f\x73\x57\x62\x3b\x83\xa5\x87\xfb\xe0\x1a\x24\x24\xfd\xd0\x23" \
    "\x84\xa6\x69\x12\x52\xf0\x94\x33\xc6\xe6\x33\x98\xb7\x48\x48\x00" \
    "\x80\x84\xc4\x18\x63\x5b\xe3\x63\x5c\x19\x5a\x6b\xad\xb5\x8e\x48" \
    "\x04\x00\x08\x21\x00\x88\x48\xf4\x2d\x25\x63\x4c\x7c\x8c\x2d\x6d" \
    "\x05\x00\x09\x4b\x3e\x1a\x68\x4c\x7d\xda\x79\xaa\x6b\xb5\x62\xc0" \
    "\x18\x2f\x69\xe7\x29\xf2\xe2\x55\xa8\x4e\xfd\xbe\x6c\xd5\x29\xec" \
    "\x68\x21\x85\x9f\xb7\x93\x90\x82\x52\x1a\x1c\x02\x1b\x2b\xf6\x9f" \
    "\x17\x52\x2c\x0d\x3e\x3d\x3f\x0d\x9e\x72\x97\xb7\x93\x4f\xcf\x7f" \
    "\xf8\xcb\xb5\x3e\x01\x8d\xb5\x6a\x19\xa6\x37\x6f\xd9\x00\x00\x00" \
    "\x00\x49\x45\x4e\x44\xae\x42\x60\x82"

_down_arrow = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d\x49\x48\x44\x52" \
    "\x00\x00\x00\x10\x00\x00\x00\x10\x08\x02\x00\x00\x00\x90\x91\x68" \
    "\x36\x00\x00\x00\x06\x62\x4b\x47\x44\x00\xff\x00\xff\x00\xff\xa0" \
    "\xbd\xa7\x93\x00\x00\x00\x09\x70\x48\x59\x73\x00\x00\x0b\x13\x00" \
    "\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x07\x74\x49\x4d\x45" \
    "\x07\xd6\x06\x03\x03\x29\x2f\x78\x97\x13\x37\x00\x00\x00\x10\x74" \
    "\x45\x58\x74\x43\x6f\x6d\x6d\x65\x6e\x74\x00\x4e\x61\x6e\x6f\x74" \
    "\x75\x62\x65\xa3\x8c\x3b\xec\x00\x00\x00\xba\x49\x44\x41\x54\x28" \
    "\xcf\xb5\x92\x3f\x0e\x82\x30\x14\x87\x8b\x31\xcc\x32\xd9\x72\x02" \
    "\x39\x83\x0c\x3f\xb8\x82\xc2\x09\x41\x2f\x41\x0a\x43\x7b\x95\x52" \
    "\x26\xbc\x41\x1d\x48\xb0\xb6\x40\x64\xf0\x6d\x2f\xfd\xbe\xf4\xfd" \
    "\x0b\x54\xaf\xc8\x9e\x38\x90\x9d\x71\xb4\x13\x21\x85\x4f\xa4\xd7" \
    "\x74\x59\x10\x52\x14\xb7\xc2\x17\xea\x67\x9d\x67\xb9\x2b\xc4\x2c" \
    "\xfe\xa5\x1e\xd5\xab\x60\x6a\x5a\x48\x51\xde\xcb\xae\xeb\xd6\x50" \
    "\x00\x13\xf9\x69\xda\x18\x03\x60\x8d\x6e\x78\xb3\x30\x25\x3d\x68" \
    "\xdf\x01\x50\x3d\xaa\xd5\xb1\x3a\x0e\x00\x63\x4c\x18\x86\x5b\x7b" \
    "\x98\x1d\x00\x7a\xd0\x5b\x7b\xb0\x1d\x7a\xa6\x3e\x4d\x08\x09\xe6" \
    "\xd3\xe0\x2d\xb7\xe7\x3d\x07\x6f\x39\xa5\x34\x3a\x45\x8c\xb1\x2f" \
    "\x61\x7a\xf3\x05\x9b\x76\x4b\x4a\x2e\xc9\xf8\x1a\x1d\xc1\xa6\xdd" \
    "\x1f\xfe\x72\xad\x6f\xd8\xd4\x50\x37\x09\xb5\x93\x63\x00\x00\x00" \
    "\x00\x49\x45\x4e\x44\xae\x42\x60\x82"

cmd = greenmsg("Insert POV-Ray Scene: ")

class PovraySceneProp(PovrayScenePropDialog):

    def __init__(self, win):
        PovrayScenePropDialog.__init__(self, win)  # win is parent.
        self.win = win
        self.glpane = self.win.glpane
        self.pvs = None
        self.previousParams = None
        self._up_arrow = QPixmap()
        self._up_arrow.loadFromData(_up_arrow)
        self._down_arrow = QPixmap()
        self._down_arrow.loadFromData(_down_arrow)
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
        '''Slot for the What\'s This button'''
        QWhatsThis.enterWhatsThisMode()

    def toggle_groupbox(self, button, *things):
        if things[0].isShown():
            button.setIconSet(QIconSet(self._down_arrow))
            for thing in things:
                thing.hide()
        else:
            button.setIconSet(QIconSet(self._up_arrow))
            for thing in things:
                thing.show()

    def toggle_grpbtn_1(self):
        self.toggle_groupbox(self.grpbtn_1, self.line2,
                             self.name_linedit)

    def toggle_grpbtn_3(self):
        self.toggle_groupbox(self.grpbtn_3, self.line2_3,
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

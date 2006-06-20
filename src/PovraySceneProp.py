# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
'''
PovraySceneProp.py - the PovraySceneProp class, including all methods needed by the POV-Ray Scene dialog.

$Id$

History:

mark 060602 - Created for NFR: "Insert > POV-Ray Scene".
'''
__author__ = "Mark"

from qt import QDoubleValidator, SIGNAL, QDialog
from PovrayScenePropDialog import PovrayScenePropDialog
from HistoryWidget import greenmsg
from widgets import double_fixup
from PovrayScene import genPVSNum
import env
from HistoryWidget import redmsg, orangemsg, greenmsg

class PovraySceneProp(PovrayScenePropDialog):

    cmdname = greenmsg("Insert POV-Ray Scene: ")
    sponsor_keyword = 'DNA'
    prefix = 'POV-Ray Scene-'
    extension = ".pov"

    def __init__(self, win):
        PovrayScenePropDialog.__init__(self, win)  # win is parent.
        self.win = win
        self.glpane = self.win.glpane
        self.struct = None
        self.previousParams = None
        # Validator for the aspect ratio linedit widget.
        self.validator = QDoubleValidator(self)
        # Range of aspect ratio (0.25-4.0, 3 decimal places)
        self.validator.setRange(0.25, 4.0, 3)
        self.aspect_ratio_linedit.setValidator(self.validator)
        self.aspect_ratio_str = str(self.aspect_ratio_linedit.text())
        self.aspect_ratio_linedit.setReadOnly(True) # Read-only for now, maybe forever. Mark 060602.

    def _create_new_name(self):
        'Create new name for new PVS.'
        import PovrayScene
        self._PVSNum = PovrayScene.PVSNum
        self.name = genPVSNum(self.prefix) + self.extension
    
    def _revert_number(self):
        'Revert the PVS number'
        import PovrayScene
        if hasattr(self, '_PVSNum'):
            PovrayScene.PVSNum = self._PVSNum

    def setup(self, pvs=None):
        '''Show the Properties Manager dialog. If <pvs> is supplied, get the parameters from
        it and load the dialog widgets.
        '''      

        if pvs:
            self.struct_is_new = False
            self.name = pvs.name
            self.width, self.height, self.output_type = pvs.get_parameters()
            self.struct = pvs
            
        else:
            self.struct_is_new = True
            self._create_new_name()
            self.width = int(self.glpane.width)
            self.height = int(self.glpane.height)
            self.output_type = 'PNG'

        self.update_widgets()
        self.previousParams = params = self.gather_parameters()
        self.show()
           
    def gather_parameters(self):
        'Return the current parameter values from the widgets.'
        name = str(self.name_linedit.text())
        width = self.width_spinbox.value()
        height = self.height_spinbox.value()
        output_type = str(self.image_format_combox.currentText()).lower()
        return (name, width, height, output_type)
    
    def update_widgets(self):
        'Update the widgets using the current attr values.'
        self.maintain_aspect_ratio_checkbox.setChecked(False) # Needed. Mark 060612.
        self.name_linedit.setText(self.name)
        self.image_format_combox.setCurrentText(self.output_type.upper())
        self.width_spinbox.setValue(self.width) # Generates signal.
        self.height_spinbox.setValue(self.height) # Generates signal.
        self.maintain_aspect_ratio_checkbox.setChecked(True)
        self.update_aspect_ratio()
    
    def done_msg(self):
        'Tell what message to print when the PVS has been built.'
        if self.struct_is_new:
            return "%s created." % self.name
        else:
            return "%s updated." % self.name

    def build_struct(self, params):
        'Create or update PVS.'
        if not self.struct: 
            name = params[0]
            pvs_params = params[1:]
            from PovrayScene import PovrayScene
            self.struct = PovrayScene(self.win.assy, name, pvs_params) #bruce 060620 revised this
        else:
            self.set_params( self.struct, params)
        self.struct.write_pvs_file()
        return self.struct

    def set_params(self, struct, params): #bruce 060620, since pvs params don't include name, but our params do
        # struct should be a PovrayScene node
        name = params[0]
        pvs_params = params[1:]
        struct.name = name # this ought to be checked for being a legal name; maybe we should use try_rename ###e
        struct.set_parameters(pvs_params)
            # Warning: code in this class assumes a specific order and set of params must be used here
            # (e.g. in gather_parameters), so it might be clearer if set_parameters was just spelled out here
            # as three assignments to attrs of struct. On the other hand, these three parameters (in that order)
            # are also known to the node itself, for use in its mmp record format. Probably that's irrelevant
            # and we should still make this change during the next cleanup of these files. ###@@@ [bruce 060620 comment]
        return
    
    def remove_struct(self):
        'Delete PVS and remove it from the model tree.'
        if self.struct != None:
            self.struct.kill()
            self.struct = None
            self.win.win_update() # includes mt_update

# Property manager standard button slots.

    def ok_btn_clicked(self):
        'Slot for the OK button'
        self.win.assy.current_command_info(cmdname = self.cmdname)
        
        # Need to do this now, before calling build_struct() below.
        if not self.struct:
            addnode = True
        else:
            addnode = False
        
        params = self.gather_parameters()
        self.struct = self.build_struct(params)
        
        if addnode:
            self.win.assy.addnode(self.struct)
            
        self.win.win_update() # Update model tree regardless whether it is a new node or not.
            
        env.history.message(self.cmdname + self.done_msg())
        self.struct = None
        QDialog.accept(self)
        
    def cancel_btn_clicked(self):
        'Slot for Cancel button.'
        self.win.assy.current_command_info(cmdname = self.cmdname + " (Cancel)")
        if self.struct_is_new:
            self.remove_struct()
            self._revert_number()
        else:
            self.set_params(self.struct, self.previousParams)
        QDialog.accept(self)   
    
    def restore_defaults_btn_clicked(self):
        'Slot for Restore Defaults button.'
        self.name, self.width, self.height, self.output_type = self.previousParams
        self.update_widgets()
        
    def preview_btn_clicked(self):
        'Slot for Preview button.'
        
        # Need to do this now, before calling build_struct() below.
        if not self.struct:
            addnode = True
        else:
            addnode = False
        
        params = self.gather_parameters()
        self.struct = self.build_struct(params)
        
        if addnode:
            self.win.assy.addnode(self.struct)
        
        self.win.win_update() # Update model tree regardless whether it is a new node or not.
        
        self.struct.render_image()
        
    def whatsthis_btn_clicked(self):
        'Slot for the What\'s This button'
        QWhatsThis.enterWhatsThisMode()
    
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
        
# Property Manager groupbox button slots

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

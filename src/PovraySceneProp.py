# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
'''
PovraySceneProp.py - the PovraySceneProp class, including all methods needed by the POV-Ray Scene dialog.

$Id$

History:

mark 060602 - Created for NFR: "Insert > POV-Ray Scene".
'''
__author__ = "Mark"

from qt import SIGNAL, QDialog, QWhatsThis, QIconSet
from PovrayScenePropDialog import PovrayScenePropDialog
from HistoryWidget import greenmsg
from widgets import double_fixup
from PovrayScene import genPVSNum
import env
from HistoryWidget import redmsg, orangemsg, greenmsg
from GeneratorBaseClass import GroupButtonMixin

class PovraySceneProp(PovrayScenePropDialog, GroupButtonMixin):

    cmdname = greenmsg("Insert POV-Ray Scene: ")
    sponsor_keyword = 'DNA'
    prefix = 'POV-Ray Scene-'
    extension = ".pov"

    def __init__(self, win):
        PovrayScenePropDialog.__init__(self, win)  # win is parent.
        self.win = win
        self.glpane = self.win.glpane
        self.node = None
        self.previousParams = None

    def _create_new_node_name(self):
        'Create node name for new POV-Ray Scene node.'
        import PovrayScene
        self._PVSNum = PovrayScene.PVSNum
        self.name = genPVSNum(self.prefix) + self.extension
    
    def _revert_node_number(self):
        'Revert the PVS node number'
        import PovrayScene
        if hasattr(self, '_PVSNum'):
            PovrayScene.PVSNum = self._PVSNum

    def setup(self, pov=None):
        '''Show the Properties Manager dialog. If <pov> is supplied, 
        get the parameters from it and load the dialog widgets.
        '''
        
        if not self.win.assy.filename:
            env.history.message( self.cmdname + redmsg("Can't insert POV-Ray Scene until the current part has been saved.") )
            return

        if pov:
            self.node_is_new = False
            self.name = pov.name
            self.filename = pov.povrayscene_file
            self.width, self.height, self.output_type = pov.get_parameters()
            self.node = pov
            
        else:
            self.node_is_new = True
            self._create_new_node_name()
            self.filename = ''
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
        output_type = str(self.output_type_combox.currentText()).lower()
        return (name, width, height, output_type)
    
    def update_widgets(self):
        'Update the widgets using the current attr values.'
        self.name_linedit.setText(self.name)
        self.filename_linedit.setText(self.filename)
        self.output_type_combox.setCurrentText(self.output_type.upper())
        
        # This must be called before setting the values of the width and height spinboxes. Mark 060621.
        self.aspect_ratio = float(self.width) / float(self.height)
        aspect_ratio_str = "%.3f to 1" % self.aspect_ratio
        self.aspect_ratio_value_label.setText(aspect_ratio_str)
        
        self.width_spinbox.setValue(self.width) # Generates signal.
        self.height_spinbox.setValue(self.height) # Generates signal.
    
    def done_msg(self):
        'Tell what message to print when the POV-Ray Scene node has been created or updated.'
        if self.node_is_new:
            return "%s created." % self.name
        else:
            return "%s updated." % self.name

    def create_or_update_node(self, params):
        'Create or update the POV-Ray Scene node.'
        if not self.node: 
            self.name = params[0]
            pov_params = params[1:]
            from PovrayScene import PovrayScene
            self.node = PovrayScene(self.win.assy, self.name, pov_params) #bruce 060620 revised this
        else:
            self.set_params( self.node, params)
        
        # Only write the POV-Ray Scene file if this is a new node. If we are editing the properties of an existing
        # POV-Ray Scene node, only change the node's parameters. Do not overwrite the <povrayscene_file>!
        if self.node_is_new: 
            errorcode, filename_or_errortext = self.node.write_povrayscene_file()
            if errorcode:
                # The Pov-Ray Scene file could not be written, so remove the node.
                self.remove_node()
                env.history.message( self.cmdname + redmsg(filename_or_errortext) )
        
        return self.node

    def set_params(self, struct, params): #bruce 060620, since pov params don't include name, but our params do
        # struct should be a PovrayScene node
        name = params[0]
        pov_params = params[1:]
        struct.name = name # this ought to be checked for being a legal name; maybe we should use try_rename ###e
        struct.set_parameters(pov_params)
            # Warning: code in this class assumes a specific order and set of params must be used here
            # (e.g. in gather_parameters), so it might be clearer if set_parameters was just spelled out here
            # as three assignments to attrs of struct. On the other hand, these three parameters (in that order)
            # are also known to the node itself, for use in its mmp record format. Probably that's irrelevant
            # and we should still make this change during the next cleanup of these files. ###@@@ [bruce 060620 comment]
        return
    
    def remove_node(self):
        'Delete this POV-Ray Scene node.'
        if self.node != None:
            self.node.kill()
            self.node = None
            self.win.mt.mt_update()

# Property manager standard button slots.

    def ok_btn_clicked(self):
        'Slot for the OK button'
        
        self.win.assy.current_command_info(cmdname = self.cmdname)
        
        # Need to do this now, before calling create_or_update_node() below.
        if self.node:
            addnode = False
        else:
            addnode = True
        
        params = self.gather_parameters()
        self.node = self.create_or_update_node(params)
        
        if addnode:
            self.win.assy.addnode(self.node)
            
        self.win.mt.mt_update()
            # Update model tree regardless whether it is a new node or not, 
            # since the user may have changed the name of an existing POV-Ray Scene node.
        
        if self.node:
            env.history.message(self.cmdname + self.done_msg())
        self.node = None
        QDialog.accept(self)
        
    def cancel_btn_clicked(self):
        'Slot for Cancel button.'
        self.win.assy.current_command_info(cmdname = self.cmdname + " (Cancel)")
        if self.node_is_new:
            self.remove_node()
            self._revert_node_number()
        else:
            self.set_params(self.node, self.previousParams)
        QDialog.accept(self)   
    
    def restore_defaults_btn_clicked(self):
        'Slot for Restore Defaults button.'
        self.name, self.width, self.height, self.output_type = self.previousParams
        self.update_widgets()
            
    def preview_btn_clicked(self):
        'Slot for Preview button.'
        
        # Need to do this now, before calling create_or_update_node() below.
        if not self.node:
            addnode = True
        else:
            addnode = False
        
        params = self.gather_parameters()
        self.node = self.create_or_update_node(params)
        
        if addnode:
            self.win.assy.addnode(self.node)
        
        self.win.win_update() # Update model tree regardless whether it is a new node or not.
        
        errorcode, errortext = self.node.render_scene()
        if errorcode:
            env.history.message( self.cmdname + redmsg(errortext) )
        
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
        self.height = int (self.width / self.aspect_ratio)
        self.disconnect(self.height_spinbox,SIGNAL("valueChanged(int)"),self.change_height)
        self.height_spinbox.setValue(self.height)
        self.connect(self.height_spinbox,SIGNAL("valueChanged(int)"),self.change_height)
    
    def change_height(self, height):
        'Slot for Height spinbox'
        self.height = height
        self.update_width()
        
    def update_width(self):
        'Updates width when height changes'
        self.width = int (self.height * self.aspect_ratio)
        self.disconnect(self.width_spinbox,SIGNAL("valueChanged(int)"),self.change_width)
        self.width_spinbox.setValue(self.width)
        self.connect(self.width_spinbox,SIGNAL("valueChanged(int)"),self.change_width)
        
# Property Manager groupbox button slots

    def toggle_grpbtn_1(self):
        'Slot for first groupbox toggle button'
        self.toggle_groupbox(self.grpbtn_1, self.line2,
                            self.name_label, self.name_linedit, 
                            self.filename_label, self.filename_linedit, self.filename_btn)

    def toggle_grpbtn_2(self):
        'Slot for second groupbox toggle button'
        self.toggle_groupbox(self.grpbtn_2, self.line3,
                            self.output_type_label, self.output_type_combox,
                            self.width_label, self.width_spinbox,
                            self.height_label, self.height_spinbox,
                            self.aspect_ratio_label, self.aspect_ratio_value_label)

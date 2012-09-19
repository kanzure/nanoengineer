# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
PovraySceneProp.py - the PovraySceneProp class, including all methods
needed by the POV-Ray Scene dialog.

@author: Mark
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:

mark 060602 - Created for NFR: "Insert > POV-Ray Scene".
"""

from PyQt4.Qt import SIGNAL, QDialog, QWhatsThis, QDialog
from commands.PovraySceneProperties.PovrayScenePropDialog import Ui_PovrayScenePropDialog
import foundation.env as env, os
from utilities.Log import redmsg, greenmsg
from PM.GroupButtonMixin import GroupButtonMixin
from sponsors.Sponsors import SponsorableMixin
from utilities.Comparison import same_vals

class PovraySceneProp(QDialog, SponsorableMixin, GroupButtonMixin, Ui_PovrayScenePropDialog):

    cmdname = greenmsg("Insert POV-Ray Scene: ")
    prefix = 'POVRayScene'
    extension = ".pov"

    def __init__(self, win):
        QDialog.__init__(self, win)  # win is parent.
        self.setupUi(self)
        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.cancel_btn_clicked)
        self.connect(self.done_btn,SIGNAL("clicked()"),self.ok_btn_clicked)
        self.connect(self.height_spinbox,SIGNAL("valueChanged(int)"),self.change_height)
        self.connect(self.ok_btn,SIGNAL("clicked()"),self.ok_btn_clicked)
        self.connect(self.preview_btn,SIGNAL("clicked()"),self.preview_btn_clicked)
        self.connect(self.restore_btn,SIGNAL("clicked()"),self.restore_defaults_btn_clicked)
        self.connect(self.sponsor_btn,SIGNAL("clicked()"),self.open_sponsor_homepage)
        self.connect(self.whatsthis_btn,SIGNAL("clicked()"),self.whatsthis_btn_clicked)
        self.connect(self.width_spinbox,SIGNAL("valueChanged(int)"),self.change_width)
        self.connect(self.abort_btn,SIGNAL("clicked()"),self.cancel_btn_clicked)
        self.connect(self.grpbtn_1,SIGNAL("clicked()"),self.toggle_grpbtn_1)
        self.connect(self.grpbtn_2,SIGNAL("clicked()"),self.toggle_grpbtn_2)
        self.win = win
        self.glpane = self.win.glpane
        self.node = None
        self.previousParams = None
        self.sponsor_btn.setWhatsThis("""<b>NanoEngineer-1 Sponsor</b>
        <p>Click on the logo to learn more
        about this NanoEngineer-1 sponsor.</p>""")
        self.name_linedit.setWhatsThis("""<b>Node Name</b>
        <p>The POV-Ray Scene file node name as it appears
        in the Model Tree.</p>""")
        self.output_type_combox.setWhatsThis("""<b>Image Format </b>- the output image format when rendering
        an image from this POV-Ray Scene file.""")

    def setup(self, pov=None):
        """
        Show the Properties Manager dialog. If <pov> is supplied,
        get the parameters from it and load the dialog widgets.
        """
        if not self.win.assy.filename:
            env.history.message( self.cmdname + redmsg("Can't insert POV-Ray Scene until the current part has been saved.") )
            return

        if not pov:
            self.node_is_new = True
            from model.PovrayScene import PovrayScene
            self.node = PovrayScene(self.win.assy, None)
        else:
            self.node_is_new = False
            self.node = pov

        self.name = self.originalName = self.node.name
        ini, self.originalPov, out = self.node.get_povfile_trio()
        self.width, self.height, self.output_type = self.node.get_parameters()

        self.update_widgets()
        self.previousParams = params = self.gather_parameters()
        self.show()

    def gather_parameters(self):
        """
        Returns a tuple with the current parameter values from the widgets.
        """
        self.node.try_rename(self.name_linedit.text()) # Next three lines fix bug 2026. Mark 060702.
        self.name_linedit.setText(self.node.name) # In case the name was illegal and "Preview" was pressed.
        name = self.node.name
        width = self.width_spinbox.value()
        height = self.height_spinbox.value()
        output_type = str(self.output_type_combox.currentText()).lower()
        return (name, width, height, output_type)

    def update_widgets(self):
        """
        Update the widgets using the current attr values.
        """
        self.name_linedit.setText(self.name)
        self.output_type_combox.setItemText(self.output_type_combox.currentIndex(),
                                                                            self.output_type.upper())

        # This must be called before setting the values of the width and height spinboxes. Mark 060621.
        self.aspect_ratio = float(self.width) / float(self.height)
        aspect_ratio_str = "%.3f to 1" % self.aspect_ratio
        self.aspect_ratio_value_label.setText(aspect_ratio_str)

        self.width_spinbox.setValue(self.width) # Generates signal.
        self.height_spinbox.setValue(self.height) # Generates signal.

    def update_node(self, ok_pressed=False):
        """
        Update the POV-Ray Scene node.
        """
        self.set_params( self.node, self.gather_parameters())

        ini, pov, out = self.node.get_povfile_trio()

        # If the node was renamed, rename the POV-Ray Scene file name, too.
        # Don't do this if the "Preview" button was pressed since the user could later
        # hit "Cancel". In that case we'd loose the original .pov file, which would not be good.
        # Mark 060702.
        if ok_pressed and self.originalName != self.node.name:
            if os.path.isfile(self.originalPov):
                if os.path.isfile(pov):
                    # Normally, I'd never allow the user to delete an existing POV-Ray Scene file without asking.
                    # For A8 I'll allow it since I've run out of time.
                    # This will be fixed when Bruce implements the new File class in A9 (or later). Mark 060702.
                    os.remove(pov)
                os.rename(self.originalPov, pov)

        # Write the POV-Ray Scene (.pov) file if this is a new node or if the node's ".pov" file doesn't exist.
        # Possible ways the ".pov" file could be missing from an existing node:
        #   1. the user renamed the node in the Model Tree, or
        #   2. the POV-Ray Scene node was deleted, which deletes the file in self.kill(), and then Undo was pressed, or
        #   3. the ".pov" file was deleted by the user another way (via OS).
        # In the future, the POV-Ray Scene should save the view quat in the MMP (info) record. Then it
        # would always be possible to regenerate the POV-Ray Scene file from the MMP record, even if
        # the node's .pov file didn't exist on disk anymore. Mark 060701.

        if self.node_is_new or not os.path.exists(pov):
            errorcode, filename_or_errortext = self.node.write_povrayscene_file()
            if errorcode:
                # The Pov-Ray Scene file could not be written, so remove the node.
                self.remove_node()
                env.history.message( self.cmdname + redmsg(filename_or_errortext) )
        return

    def set_params(self, node, params): #bruce 060620, since pov params don't include name, but our params do
        # <node> should be a PovrayScene node
        name = params[0]
        pov_params = params[1:]
        node.name = name # this ought to be checked for being a legal name; maybe we should use try_rename ###e
        node.set_parameters(pov_params)
            # Warning: code in this class assumes a specific order and set of params must be used here
            # (e.g. in gather_parameters), so it might be clearer if set_parameters was just spelled out here
            # as three assignments to attrs of struct. On the other hand, these three parameters (in that order)
            # are also known to the node itself, for use in its mmp record format. Probably that's irrelevant
            # and we should still make this change during the next cleanup of these files. ###@@@ [bruce 060620 comment]
        return

    def remove_node(self):
        """
        Delete this POV-Ray Scene node.
        """
        if self.node != None:
            #&&& self.node.kill(require_confirmation = False)
            # This version prompts the user to confirm deleting the node if its file exists (usually).
            self.node.kill() # Assume the user wants to delete the node's POV-Ray Scene file.
            self.node = None
            self.win.mt.mt_update()

# Property manager standard button slots.

    def ok_btn_clicked(self):
        """
        Slot for the OK button
        """
        self.win.assy.current_command_info(cmdname = self.cmdname)

        self.update_node(ok_pressed = True)

        if self.node_is_new:
            self.win.assy.addnode(self.node)

        self.node.update_icon() # In case we rewrote a lost POV-Ray Scene file in update_node().
        self.win.mt.mt_update()
            # Update model tree regardless whether it is a new node or not,
            # since the user may have changed the name of an existing POV-Ray Scene node.

        env.history.message(self.cmdname + self.done_msg())
        self.node = None
        QDialog.accept(self)

    def done_msg(self):
        """
        Returns the message to print after the OK button has been pressed.
        """
        if self.node_is_new:
            return "%s created." % self.name
        else:
            if not same_vals( self.previousParams, self.gather_parameters()):
                return "%s updated." % self.name
            else:
                return "%s unchanged." % self.name

    def cancel_btn_clicked(self):
        """
        Slot for Cancel button.
        """
        self.win.assy.current_command_info(cmdname = self.cmdname + " (Cancel)")
        if self.node_is_new:
            self.remove_node()
        else:
            self.set_params(self.node, self.previousParams)
        QDialog.accept(self)

    def restore_defaults_btn_clicked(self):
        """
        Slot for Restore Defaults button.
        """
        self.name, self.width, self.height, self.output_type = self.previousParams
        self.update_widgets()

    def preview_btn_clicked(self):
        """
        Slot for Preview button.
        """
        self.update_node()

        self.node.raytrace_scene()

        #&&& Should we print history message in this method or return the errorcode and text so the caller
        #&&& can decide what to do? I think it would be better to display the history msg in raytrace_scene. Mark 060701.
        #&&&errorcode, errortext = self.node.raytrace_scene()
        #&&&if errorcode:
        #&&&    env.history.message( self.cmdname + redmsg(errortext) )
        #&&&else:
        #&&&    env.history.message( self.cmdname + errortext ) # "Rendering finished" message.

    def whatsthis_btn_clicked(self):
        """
        Slot for the What's This button
        """
        QWhatsThis.enterWhatsThisMode()

# Property manager widget slots.

    def change_width(self, width):
        """
        Slot for Width spinbox
        """
        self.width = width
        self.update_height()

    def update_height(self):
        """
        Updates height when width changes
        """
        self.height = int (self.width / self.aspect_ratio)
        self.disconnect(self.height_spinbox,SIGNAL("valueChanged(int)"),self.change_height)
        self.height_spinbox.setValue(self.height)
        self.connect(self.height_spinbox,SIGNAL("valueChanged(int)"),self.change_height)

    def change_height(self, height):
        """
        Slot for Height spinbox
        """
        self.height = height
        self.update_width()

    def update_width(self):
        """
        Updates width when height changes
        """
        self.width = int (self.height * self.aspect_ratio)
        self.disconnect(self.width_spinbox,SIGNAL("valueChanged(int)"),self.change_width)
        self.width_spinbox.setValue(self.width)
        self.connect(self.width_spinbox,SIGNAL("valueChanged(int)"),self.change_width)

# Property Manager groupbox button slots

    def toggle_grpbtn_1(self):
        """
        Slot for first groupbox toggle button
        """
        self.toggle_groupbox_in_dialogs(self.grpbtn_1, self.line2,
                            self.name_linedit)

    def toggle_grpbtn_2(self):
        """
        Slot for second groupbox toggle button
        """
        self.toggle_groupbox_in_dialogs(self.grpbtn_2, self.line3,
                            self.output_type_label, self.output_type_combox,
                            self.width_label, self.width_spinbox,
                            self.height_label, self.height_spinbox,
                            self.aspect_ratio_label, self.aspect_ratio_value_label)

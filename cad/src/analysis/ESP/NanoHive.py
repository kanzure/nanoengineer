# Copyright 2005-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
NanoHive.py - dialog and control code for running ESP (and other?)
calculations using NanoHive

@author: Mark
@version: $Id$
@copyright: 2005-2009 Nanorex, Inc.  See LICENSE file for details.

Module classification: has ui/control/ops code; put in ui for now.
"""

from PyQt4.Qt import QWidget
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QDialog
from PyQt4.Qt import QString

import foundation.env as env

from utilities.constants import filesplit
from utilities.Log import redmsg, greenmsg, orangemsg

from analysis.ESP.NanoHiveDialog import Ui_NanoHiveDialog
from analysis.ESP.ESPImage import ESPImage
from analysis.ESP.NanoHiveUtils import run_nh_simulation

from analysis.ESP.NanoHive_SimParameters import NanoHive_SimParameters

cmd = greenmsg("Nano-Hive: ")

# _get_partname() should be a global function.  Mark 050915.
# [or, better, refile it as an assy method. bruce 071215]
def _get_partname(assy):
    """
    Returns the base name of the part.  If the filename is not set,
    returns "Untitled".
    """
    if assy.filename:
        junk, basename, ext = filesplit(assy.filename)
        return basename
    else:
        return "Untitled"

def _find_all_ESPImage_jigs_under( root):
    """
    Returns a list of ESPImage jigs.
    """
    # Code copied from node_indices.find_all_jigs_under().  Mark 050919.
    res = []
    def grab_if_ESP_Image_jig(node):
        if isinstance(node, ESPImage):
            res.append(node)
    root.apply2all( grab_if_ESP_Image_jig)
    return res

class NanoHive(QWidget, Ui_NanoHiveDialog):
    """
    The Nano-Hive dialog
    """
    def __init__(self, assy):
        QWidget.__init__(self)
        self.setupUi(self)
        self.connect(self.run_sim_btn, SIGNAL("clicked()"), self.accept)
        self.connect(self.cancel_btn, SIGNAL("clicked()"), self.reject)
        self.connect(self.MPQC_ESP_checkbox, SIGNAL("toggled(bool)"), self.update_ESP_window_combox)
        self.connect(self.MPQC_GD_checkbox, SIGNAL("toggled(bool)"), self.update_MPQC_GD_options_btn)
        self.connect(self.ESP_image_combox, SIGNAL("activated(int)"), self.set_ESP_window)
        self.connect(self.MPQC_GD_options_btn, SIGNAL("clicked()"), self.show_MPQC_GD_options_dialog)
        self.assy = assy
        self.part = assy.part
        self.esp_image_list = [] # List of ESP Image jigs.
        self.esp_image = None # The currently selected ESP Image.
        
        # This is where What's This descriptions should go for the Nano-Hive dialog.
        # Mark 050831.
        from ne1_ui.WhatsThisText_for_MainWindow import create_whats_this_descriptions_for_NanoHive_dialog
        create_whats_this_descriptions_for_NanoHive_dialog(self)
        
        return

    def showDialog(self, assy):
        """
        Display the dialog
        """
        self.assy = assy
        self.part = assy.part
        
        # Make sure there is something to simulate.
        if not self.part.molecules: # Nothing in the part to simulate.
            msg = redmsg("Nothing to simulate.")
            env.history.message(cmd + msg)
            return
        
        env.history.message(cmd + "Enter simulation parameters and select <b>Run Simulation.</b>")
        
        self._init_dialog()
        
        self.exec_()
        return
        
    def _init_dialog(self):
        
        # Fill in the name_linedit widget.
        self.name_linedit.setText(_get_partname(self.assy))
        
        self.MPQC_ESP_checkbox.setChecked(False)
        self.MPQC_GD_checkbox.setChecked(False)
        self.AIREBO_checkbox.setChecked(False)
        
        self.populate_ESP_image_combox() # Update the ESP Image combo box.
        
        self.Measurements_to_File_checkbox.setChecked(False)
        self.POVRayVideo_checkbox.setChecked(False)
        
    # == Slots for Nano-Hive Dialog
                
    def accept(self):
        """
        The slot method for the 'OK' button.
        """
        if self.run_nanohive():
            return
        QDialog.accept(self)
        
        
    def reject(self):
        """
        The slot method for the "Cancel" button.
        """
        QDialog.reject(self)
        
    def update_ESP_image_combox(self, toggle):
        """
        Enables/disables the ESP Image combo box.
        """
        if self.esp_image_list:
            self.ESP_image_combox.setEnabled(toggle)
        else:
            env.history.message("No ESP Image Jigs")
            self.MPQC_ESP_checkbox.setChecked(False)
            self.ESP_image_combox.setEnabled(False)
        
    def populate_ESP_image_combox(self):
        """
        Populates the ESP Image combo box with the names of all ESPImage jigs
        in the current part.
        """
        self.esp_image_list = _find_all_ESPImage_jigs_under(self.assy.tree)
        
        self.ESP_image_combox.clear()
        for jig in self.esp_image_list:
            self.ESP_image_combox.insertItem(100, jig.name)
            # 100 makes sure item is appended to list. [mark 2007-05-04]
        
        if self.esp_image_list:
            # Set default ESP Image to the first one in the list.
            self.esp_image = self.esp_image_list[0]
        else:
            # Must have at least one ESP Image in the part to select this plugin
            # self.MPQC_ESP_checkbox.setEnabled(False) # Disable the ESP Plane plugin. 
            self.ESP_image_combox.setEnabled(False)
            
    def set_ESP_image(self, indx):
        """
        Slot for the ESP Image combo box.
        """
        print "Index = ", indx
        
        if indx:
            self.esp_image = self.esp_image_list[indx]
            print "ESP Image Name =", self.esp_image.name
        else:
            self.esp_image = None
            print "ESP Image Name =", self.esp_image
        
    def update_MPQC_GD_options_btn(self, toggle):
        """
        Enables/disables the MPQC Gradient Dynamics Options button.
        """
        self.MPQC_GD_options_btn.setEnabled(toggle)
        
    def show_MPQC_GD_options_dialog(self):
        """
        Show the MPQC Gradient Dynamics Options dialog.
        """
        print "MPQC Gradient Dynamics Options dialog is not implemented yet."
        
    # ==

    def get_sim_id(self):
        """
        Return the simulation id (name) from the dialog's Name widget.
        If it is empty, return "Untitled" as the sim_name.
        """
        name = QString(self.name_linedit.text())
        bname = name.stripWhiteSpace() # make sure suffix is not just whitespaces

        if bname:
            sim_name = str(bname)
            # Brian H. says that "name" cannot have any whitespace characters. 
            # He suggests that we replace whitespace chars with underscores.
            # It is late and I don't have time to look up the Python function for this.
            # DON'T FORGET.  Mark 050915 at 11:45PM.  ZZZ.
        else:
            sim_name = "Untitled"
            
        return sim_name
        
    def get_sims_to_run(self):
        """
        Returns a list of the simulations to run.
        """
        sims_to_run = []
        
        if self.MPQC_ESP_checkbox.isChecked():
            sims_to_run.append("MPQC_ESP")
            
        if self.MPQC_GD_checkbox.isChecked():
            sims_to_run.append("MPQC_GD")
                
        if self.AIREBO_checkbox.isChecked():
            sims_to_run.append("AIREBO")
            
        return sims_to_run
        
    def get_results_to_save(self):
        """
        Returns a list of the simulations to run.
        """
        results_to_save = []
        
        if self.Measurements_to_File_checkbox.isChecked():
            results_to_save.append("MEASUREMENTS_TO_FILE")

        if self.POVRayVideo_checkbox.isChecked():
            results_to_save.append("POVRAYVIDEO")

        # NetCDF Plugin.  COMMENTED OUT FOR TESTING.
        if 0:
            results_to_save.append("NETCDF")
            
        return results_to_save
        
    def get_sim_data(self):
        """
        Return the set of parameters and data needed to run the Nano-Hive simulation.
        """
        sp = NanoHive_SimParameters()
        
        sp.desc = self.description_textedit.toPlainText()
        sp.iterations = self.nframes_spinbox.value() # Iterations = Frames
        sp.spf = self.stepsper_spinbox.value() * 1e-17 # Steps per Frame
        sp.temp = self.temp_spinbox.value() # Temp in Kelvin
        sp.esp_image = self.esp_image
        
        return sp
         
    def run_nanohive(self):
        """
        Slot for "Run Simulation" button.
        """
        sim_name = self.get_sim_name()
        sim_parms = self.get_sim_data()
        sims_to_run = self.get_sims_to_run()
        results_to_save = self.get_results_to_save()
        
        run_nh_simulation(self.assy, sim_name, sim_parms, sims_to_run, results_to_save)

    pass

# end

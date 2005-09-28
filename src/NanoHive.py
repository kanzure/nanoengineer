# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
NanoHive.py

$Id$

History:

Created by Mark.
'''
__author__ = "Mark"

from qt import *
from NanoHiveDialog import NanoHiveDialog
from HistoryWidget import redmsg, greenmsg, orangemsg
import env, os
from constants import *
from jigs_planes import ESPWindow
from files_nh import *
from NanoHiveUtils import *

debug_sim = 0 # DO NOT COMMIT with 1

cmd = greenmsg("Nano-Hive: ")

class NH_Sim_Parameters:
    pass
    
# get_partname() should be a global function.  Mark 050915.
def get_partname(assy):
    'Returns the base name of the part.  If the filename is None, returns'
    if assy.filename:
        from movieMode import filesplit
        junk, basename, ext = filesplit(assy.filename)
        return basename
    else:
        return "Untitled"

def find_all_ESP_window_jigs_under( root):
    '''Returns a list of ESP Window jigs.
    '''
    # Code copied from node_indices.find_all_jigs_under().  Mark 050919.
    res = []
    def grab_if_ESP_Window_jig(node):
        if isinstance(node, ESPWindow):
            res.append(node)
    root.apply2all( grab_if_ESP_Window_jig)
    return res

class NanoHive(NanoHiveDialog):
    '''The Nano-Hive dialog
    '''
       
    def __init__(self, assy):
        NanoHiveDialog.__init__(self)
        self.assy = assy
        self.part=assy.part
        self.esp_window_list = [] # List of ESP Window jigs.
        self.esp_window = None # The currently selected ESP Window.
        
        # This is where What's This descriptions should go for the Nano-Hive dialog.
        # Mark 050831.
        from whatsthis import create_whats_this_descriptions_for_NanoHive_dialog
        create_whats_this_descriptions_for_NanoHive_dialog(self)
        
        return

    def showDialog(self, assy):
        '''Display the dialog '''
        self.assy=assy
        self.part=assy.part
        
        # Make sure there is something to simulate.
        if not self.part.molecules: # Nothing in the part to simulate.
            msg = redmsg("Nothing to simulate.")
            env.history.message(cmd + msg)
            return
        
        env.history.message(cmd + "Enter simulation parameters and select <b>Run Simulation.</b>")
        
        self._init_dialog()
        
        self.exec_loop()
        return
        
    def _init_dialog(self):
        
        # Fill in the name_linedit widget.
        self.name_linedit.setText(get_partname(self.assy))
        
        self.MPQC_ESP_checkbox.setChecked(False)
        self.MPQC_GD_checkbox.setChecked(False)
        self.AIREBO_checkbox.setChecked(False)
        
        self.populate_ESP_window_combox() # Update the ESP Window combo box.
        
        self.Measurements_to_File_checkbox.setChecked(False)
        self.POVRayVideo_checkbox.setChecked(False)
        
# == Slots for Nano-Hive Dialog
                
    def accept(self):
        '''The slot method for the 'OK' button.'''
        if self.run_nanohive():
            return
        QDialog.accept(self)
        
        
    def reject(self):
        '''The slot method for the "Cancel" button.'''
        QDialog.reject(self)
        
    def update_ESP_window_combox(self, toggle):
        '''Enables/disables the ESP Window combo box.
        '''
        if self.esp_window_list:
            self.ESP_window_combox.setEnabled(toggle)
        else:
            env.history.message("No ESP Window Jigs")
            self.MPQC_ESP_checkbox.setChecked(False)
            self.ESP_window_combox.setEnabled(False)
        
    def populate_ESP_window_combox(self):
        '''Populates the ESP Window combo box with the names of all ESP Window jigs in the current part.
        '''
        self.esp_window_list = find_all_ESP_window_jigs_under(self.assy.tree)
        
        self.ESP_window_combox.clear()
        for jig in self.esp_window_list:
            self.ESP_window_combox.insertItem(jig.name)
        
        if self.esp_window_list:
            # Set default ESP Window to the first one in the list.
            self.esp_window = self.esp_window_list[0]
        else:
            # Must have at least one ESP Window in the part to select this plugin
            # self.MPQC_ESP_checkbox.setEnabled(False) # Disable the ESP Plane plugin. 
            self.ESP_window_combox.setEnabled(False)
            
    def set_ESP_window(self, indx):
        '''Slot for the ESP Window combo box.
        '''
        print "Index = ", indx
        
        if indx:
            self.esp_window = self.esp_window_list[indx]
            print "ESP Window Name =", self.esp_window.name
        else:
            self.esp_window = None
            print "ESP Window Name =", self.esp_window
        
    def update_MPQC_GD_options_btn(self, toggle):
        '''Enables/disables the MPQC Gradient Dynamics Options button.
        '''
        self.MPQC_GD_options_btn.setEnabled(toggle)
        
    def show_MPQC_GD_options_dialog(self):
        '''Show the MPQC Gradient Dynamics Options dialog.
        '''
        print "MPQC Gradient Dynamics Options dialog is not implemented yet."
        
# ==

    def get_sim_name(self):
        '''Return the simulation name from the dialog's Name widget.
        If it is empty, return "Untitled" as the sim_name.
        '''
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
        '''Returns a list of the simulations to run.
        '''
        sims_to_run = []
        
        if self.MPQC_ESP_checkbox.isChecked():
            sims_to_run.append("MPQC_ESP")
            
        if self.MPQC_GD_checkbox.isChecked():
            sims_to_run.append("MPQC_GD")
                
        if self.AIREBO_checkbox.isChecked():
            sims_to_run.append("AIREBO")
            
        return sims_to_run
        
    def get_results_to_save(self):
        '''Returns a list of the simulations to run.
        '''
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
        '''Return the set of parameters and data needed to run the Nano-Hive simulation.
        '''
        sp = NH_Sim_Parameters()
        
        sp.desc = self.description_textedit.text()
        sp.iterations = self.nframes_spinbox.value() # Iterations = Frames
        sp.spf = self.stepsper_spinbox.value() * 1e-17 # Steps per Frame
        sp.temp = self.temp_spinbox.value() # Temp in Kelvin
        sp.esp_window = self.esp_window
        
        return sp
         
    def run_nanohive(self):
        '''Slot for "Run Simulation" button.
        '''
        sim_name = self.get_sim_name()
        sim_parms = self.get_sim_data()
        sims_to_run = self.get_sims_to_run()
        results_to_save = self.get_results_to_save()
        
        run_nh_simulation(self.assy, sim_name, sim_parms, sims_to_run, results_to_save)
            
# end
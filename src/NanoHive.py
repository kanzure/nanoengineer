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
from jigs import ESPWindow

debug_sim = 0 # DO NOT COMMIT with 1

cmd = greenmsg("Nano-Hive: ")


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

    def run_nanohive(self):
        '''Run a Nano-Hive simulation.
        '''
        
        # Validate that the Nano-Hive executable exists.
        r = self._validate_nanohive_program()
        
        if r: # Nano-Hive program was not found/valid.
            return 1 # Simulation Cancelled.
            
        # Check that a valid ESP Window is selected if ESP Plane is checked.
#        if self.MPQC_ESP_checkbox.isChecked():
#            if not self.esp_window:
#                env.history.message(redmsg(cmd + "Please select an ESP Window."))
#                return 1
        
        # Retreive the filenames, output directory and part name.
        mmp_filename, \
        simspec_filename, \
        simflow_filename, \
        outdir, \
        partname = self.get_nanohive_filenames()
        
        # 1. Write the MMP file that Nano-Hive will use for the sim run.
        self.assy.writemmpfile(mmp_filename)
            
        # 2. Write the sim-spec file using the parameters from the Nano-Hive dialog widgets
        self.write_simspec_file(simspec_filename, simflow_filename, mmp_filename, outdir, partname)
        
        # 3. Write the Sim Flow file
        self.write_simflow_file(simflow_filename)
        
        # 3. Execute Nano-Hive, to be written by Brian H.
        
        # Informative messages (temporary).
        print "\n-------------------------------------"
        print "Here are the locations of the files that Nano-Hive needs:"
        print "MMP File: ", mmp_filename
        print "SimSpec File: ", simspec_filename
        print "SimFlow File: ", simflow_filename
        print "Brian H. will write the code for generating the SimFlow file."
        print "-------------------------------------\n"
        
        infotext = "-------------------------------------<br>"\
                        "Here are the locations of the files that Nano-Hive needs:<br>"\
                        "MMP File: " + mmp_filename + "<br>"\
                        "SimSpec File: " + simspec_filename + "<br>"\
                        "SimFlow File: " + simflow_filename + "<br>"\
                        "Brian H. will write the code for generating the SimFlow file." + "<br>"\
                        "-------------------------------------<br>"
        
        env.history.message(infotext)
        
        return 0
        

    def get_nanohive_filenames(self):
        '''Returns the file names for Nano-Hive in this order:
            1. MMP filename (full path)
            2. Simspec filename (full path)
            3. Simflow filename (full path)
            4. Nano-Hive directory where all the files are placed
            5. Partname, which is the base name of the current part (assy).
        '''
        from platform import find_or_make_Nanorex_subdir
        nhdir = find_or_make_Nanorex_subdir("Nano-Hive")
        n = QString(self.name_linedit.text())
        fn = n.stripWhiteSpace() # make sure suffix is not just whitespaces

        if fn:
            name = str(fn)
            # Brian H. says that "name" cannot have any whitespace characters. 
            # He suggests that we replace whitespace chars with underscores.
            # It is late and I don't have time to look up the Python function for this.
            # DON'T FORGET.  Mark 050915 at 11:45PM.  ZZZ.
        else:
            name = "Untitled"
            
        mmp_fn = os.path.join(nhdir,str(name)+".mmp")
        simspec_fn = os.path.join(nhdir,str(name)+"_simspec.xml")
        simflow_fn = os.path.join(nhdir,str(name)+"_simflow.tcl")
        
        return mmp_fn, simspec_fn, simflow_fn, nhdir, name
        
    def write_simspec_file(self, filename, simflow_filename, mmp_filename, outdir, partname):
        '''Writes the Nano-Hive Sim Spec file, which is an XML file that describes the
        simulation environment, plugin selection and plugin parameters.
        '''
        
        # The Nano-Hive Sim Spec file has 4 different sections that must be written in the following order:
        # 1. Header Section
        # 2. Physical Interaction Plugin(s) Section
        # 3. Results Plugin(s) Section
        # 4. Footer Section.
        # Mark 050915.
        
        iterations = self.nframes_spinbox.value() # Iterations = Frames
        spf = self.stepsper_spinbox.value() * 1e-17 # Steps per Frame
        temp = self.temp_spinbox.value() # Temp in Kelvin
        
        # Retreive the Nano-Hive home directory by stripping off the last two directories
        # from the Nano-Hive executable path.
        nanohive_exe = env.prefs[nanohive_path_prefs_key]
        head, tail = os.path.split(nanohive_exe)
        nh_home, tail = os.path.split(head)
        
        # print "NanoHive.write_simspec_file(): Nano-Hive Home:", nh_home
        
        f = open(filename,'w') # Open Nano-Hive Sim Spec file.
        
        # Write SimSpec header ########################################
        
        f.write ('<simulation>\n')
        f.write('  <description>%s</description>\n' % self.description_textedit.text())
        f.write('  <parameter name="timeQuantumLength" value="%e" />\n' % spf)
        f.write('  <parameter name="environmentTemperature" value="%d" />\n' % temp)
        f.write('  <parameter name="startIteration" value="0" />\n')
        f.write('  <parameter name="iterations" value="%d" />\n' % iterations)
        f.write('\n')
        f.write('  <simulationFlow file="%s">\n' % simflow_filename)
        f.write('    <input type="nanorexMMP" file="%s" />\n' % mmp_filename)
        
        # This traverser is for the local machine.
        f.write('    <traverser name="traverser" plugin="RC_Traverser" />\n')
        
        # The bond calculator
        f.write('    <calculator name="bondCalculator" plugin="BondCalculator" />\n')
        
        # Physical Interaction Plugins ########################################
        
        if self.MPQC_ESP_checkbox.isChecked():
            
            cpnt = self.esp_window.center * 1e-10
            centerPoint = (float(cpnt[0]), float(cpnt[1]), float(cpnt[2]))
            #print "ESP Window CenterPoint =", centerPoint
            
            npnt = self.esp_window.getaxis() * 1e-10
            normalPoint = (float(npnt[0]), float(npnt[1]), float(npnt[2]))
            #print "ESP Window NormalPoint =", normalPoint
            
            outputLength = self.esp_window.width * 1e-10
            #print "ESP Window outputLength =", outputLength
            
            resolution = self.esp_window.resolution
            # print "ESP Window Resolution =", resolution

            f.write('\n')
            f.write('    <calculator name="qmCalculator" plugin="MPQC_SClib">\n')
            f.write('      <parameter name="logDirectory" value="%s/log" />\n' % nh_home)
            f.write('      <parameter name="dataDirectory" value="%s/data/MQPC_SClib" />\n' % nh_home)
            f.write('      <parameter name="basis" value="STO-3G" />\n')
            f.write('      <parameter name="method" value="HF" />\n')
            f.write('      <parameter name="gradientDynamics" value="no" />\n')
            f.write('      <parameter name="outputType" value="ESPplane" />\n')
            f.write('      <parameter name="resolution" value="%d" />\n' % resolution)
            f.write('      <parameter name="centerPoint" value="%e,%e,%e" />\n' % centerPoint)
            f.write('      <parameter name="normalPoint" value="%e,%e,%e" />\n' % normalPoint)
            f.write('      <parameter name="outputLength" value="%e" />\n' % outputLength)
            f.write('      <parameter name="cutoffHeight" value="1.0e-10" />\n')
            f.write('      <parameter name="cutoffWidth" value="0.5e-10" />\n')
            f.write('    </calculator>\n')
            
        if self.MPQC_GD_checkbox.isChecked():
            f.write('\n')
            f.write('    <calculator name="qmDynamicsInteraction" plugin="MPQC_SClib">\n')
            f.write('      <parameter name="logDirectory" value="%s/log" />\n' % nh_home)
            f.write('      <parameter name="dataDirectory" value="%s/data/MQPC_SClib" />\n' % nh_home)
            f.write('      <parameter name="basis" value="STO-3G" />\n')
            f.write('      <parameter name="method" value="HF" />\n')
            f.write('      <parameter name="gradientDynamics" value="yes" />\n')
            f.write('      <parameter name="deltaTbyTau" value="1.0" />\n')
            f.write('    </calculator>\n')
                
        if self.AIREBO_checkbox.isChecked():
            f.write('\n')
            f.write('    <calculator name="physicalInteraction" plugin="REBO_MBM">\n')
            f.write('      <parameter name="dataDirectory" value="%s/data/REBO_MBM" />\n' % nh_home)
            f.write('    </calculator>\n')

        # Results Plugins ########################################
        
        if self.Measurements_to_File_checkbox.isChecked():
            f.write('\n')
            f.write('    <result name="MeasurementSetToFile" plugin="MeasurementSetToFile">\n')
            f.write('      <parameter name="outputInterval" value="1" />\n')
            f.write('      <parameter name="outputFile"\n')
            f.write('        value="%s/data.txt" />\n' % outdir)
            f.write('      <parameter name="datumSeparator" value="\t" />\n')
            f.write('    </result>\n')

        if self.POVRayVideo_checkbox.isChecked():
            # Need subdirectory for all the POV-Ray pov files.
            # Also need to add lighting, scene setup, background color, etc.
            f.write('\n')
            f.write('    <result name="POVRayVideo" plugin="POVRayVideo">\n')
            f.write('      <parameter name="outputInterval" value="1" />\n')
            f.write('      <parameter name="lengthMultiplier" value="1e10" />\n')
            f.write('      <parameter name="outputDirectory"\n')
            f.write('        value="%s/povray" />\n' % outdir)
            f.write('      <parameter name="outputIdentifier" value="%s" />\n' % partname)
            # POV-Ray template.  Mark needs to write the include file for lighting and camera angle(s)
            # and put that file in the appropriate place (outdir/povray).
            f.write('      <parameter name="povTemplateFilename"\n')
            f.write('        value="%s/data/pov.tmplt" />')
            f.write('      <parameter name="mpegTemplateFilename"\n')
            f.write('        value="%s/data/mpeg_encode.param.tmplt" />\n' % nh_home)
            f.write('    </result>\n')

        # NetCDF Plugin
        f.write('\n')
        f.write('    <result name="simResult" plugin="NetCDF_DataSet">\n')
        f.write('      <parameter name="outputInterval" value="1" />\n')
        f.write('      <parameter name="outputDirectory"\n')
        f.write('        value="%s" />\n' % outdir)
        f.write('      <parameter name="maxDataSets" value="-1" />\n')
        f.write('    </result>\n')
        
        # Footer
        f.write('\n')
        f.write('  </simulationFlow>\n')
        f.write('</simulation>\n')
        
        f.close()
        
    def write_simflow_file(self, filename):
        '''Writes the Nano-Hive Sim Flow file, which is a TCL script used by Nano-Hive to
        run the simulation.  It describes the workflow of the simulation.
        '''
        # Brian H. to code this method.
        pass
        

# This is not implemented yet.         
    def _validate_nanohive_program(self):
        '''Private method:
        Checks that the Nano-Hive program path exists in the user pref database
        and that the file it points to exists.  If the Nano-Hive path does not exist, the
        user will be prompted with the file chooser to select the Nano-Hive executable.
        This function does not check whether the Nano-Hive path is actually Nano-Hive.
        Returns:  0 = Valid
                        1 = Invalid
        '''
        # Get Nano-Hive executable path from the prefs db
        nanohive_exe = env.prefs[nanohive_path_prefs_key]
        
        if not nanohive_exe:
            msg = "The Nano-Hive executable path is not set.\n"
        elif os.path.exists(nanohive_exe):
            return 0
        else:
            msg = nanohive_exe + " does not exist.\n"
            
        # Nano-Hive Dialog is the parent for messagebox and file chooser.
        ret = QMessageBox.warning( self, "Nano-Hive Executable Path",
            msg + "Please select OK to set the location of Nano-Hive for this computer.",
            "&OK", "Cancel", None,
            0, 1 )
                
        if ret==0: # OK
            #from UserPrefs import get_gamess_path
            #self.server.program = get_gamess_path(parent)
            from UserPrefs import get_filename_and_save_in_prefs
            nanohive_exe = \
                get_filename_and_save_in_prefs(self, nanohive_path_prefs_key, 'Choose Nano-Hive Executable')
            if not nanohive_exe:
                return 1 # Cancelled from file chooser.
            
        elif ret==1: # Cancel
            return 1

        return 0

# end
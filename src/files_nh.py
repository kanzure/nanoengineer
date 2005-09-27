# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
files_nh.py

$Id$

History:

Created by Mark.
'''
__author__ = "Mark"

from NanoHiveUtils import *

def write_nh_simspec_file(sim_name, sim_parms, sims_to_run, results_to_save, output_dir):
    '''Writes the Nano-Hive Sim specification file, which is an XML file that describes the
    simulation environment, plugin selection and plugin parameters.
    '''
    
    # The Nano-Hive Sim Spec file has 4 different sections that must be written in the following order:
    # 1. Header Section
    # 2. Physical Interaction Plugin(s) Section
    # 3. Results Plugin(s) Section
    # 4. Footer Section.
    # Mark 050915.
    
    simspec_fname = get_nh_simspec_filename(sim_name)
    workflow_fname = get_nh_workflow_filename(sim_name)
    mmp_fname = get_nh_mmp_filename(sim_name)
    
    f = open(simspec_fname,'w') # Open Nano-Hive Sim Spec file.
    
    sp = sim_parms
    
    write_nh_header(f, sp.desc, sp.iterations, sp.spf, sp.temp, workflow_fname, mmp_fname)
    
    # Need to ask Brian about conditions for Bond record to be written.
    if 0: 
        write_nh_bond_calc_rec(f)
    
    # Physical Interaction Plugins ########################################
    
    if "MPQC_ESP" in sims_to_run:
        write_nh_mpqc_esp_plane_rec(f, sp.esp_window, output_dir)
        
    if "MPQC_GD" in sims_to_run:
        write_nh_mpqc_gd_rec(f)
            
    if "AIREBO" in sims_to_run:
        write_nh_airebo_rec(f)

    # Results Plugins ########################################
    
    if "MEASUREMENTS_TO_FILE" in results_to_save:
        write_nh_measurements_to_file_results_rec(f, output_dir)

    if "POVRAYVIDEO" in results_to_save:
        write_nh_povrayvideo_results_rec(f, sim_name, output_dir)

    if "NETCDF" in results_to_save:
        write_nh_netcdf_results_rec(f, output_dir)
    
    # Footer ########################################
    write_nh_footer(f)
    
    f.close()
            
def write_nh_workflow_file(sim_name):
    '''Writes the Nano-Hive Workflow file, which is a TCL script used by Nano-Hive to
    run the simulation.  It describes the workflow of the simulation.
    '''
    
    workflow_fname = get_nh_workflow_filename(sim_name)
    
    f = open(workflow_fname,'w')

    f.write ('NH_Import $inFile\n\n')
    f.write ('NH_Calculate 0 $traverser\n')
    f.write ('NH_Calculate 0 $espWindow $traverser\n')
    f.write ('NH_Intermediate 0 $simResult\n\n')
    f.write ('NH_Final $simResult\n')
    
    f.close()


    
def write_nh_header(f, desc, iter, spf, temp, workflow_fname, mmp_fname):
#def write_simspec_file(self, filename, workflow_filename, mmp_filename, outdir, partname):
    '''Writes the Nano-Hive Sim specification file, which is an XML file that describes the
    simulation environment, plugin selection and plugin parameters.
    '''
    
    # The Nano-Hive Sim Spec file has 4 different sections that must be written in the following order:
    # 1. Header Section
    # 2. Physical Interaction Plugin(s) Section
    # 3. Results Plugin(s) Section
    # 4. Footer Section.
    # Mark 050915.
    
    #iterations = self.nframes_spinbox.value() # Iterations = Frames
    #spf = self.stepsper_spinbox.value() * 1e-17 # Steps per Frame
    #temp = self.temp_spinbox.value() # Temp in Kelvin
    
    nh_home = get_nh_home()
    
    print "files_nh.write_nh_header(): Nano-Hive Home:", nh_home
    
#    f = open(filename,'w') # Open Nano-Hive Sim Spec file.
    
    # Write SimSpec header ########################################
    
    f.write ('<simulation>\n')
    f.write('  <description>%s</description>\n' % desc)
    f.write('\n')
    f.write('  <parameter name="timeQuantumLength" value="%e" />\n' % spf)
    f.write('  <parameter name="environmentTemperature" value="%d" />\n' % temp)
    f.write('  <parameter name="startIteration" value="0" />\n')
    f.write('  <parameter name="iterations" value="%d" />\n' % iter)
    f.write('\n')
    f.write('  <simulationFlow file="%s">\n' % workflow_fname)
    f.write('    <input name="inFile" type="nanorexMMP" file="%s" />\n' % mmp_fname)
    
    # This traverser is for the local machine.
    f.write('    <traverser name="traverser" plugin="RC_Traverser" />\n')
    
def write_nh_footer(f):

    f.write('\n')
    f.write('  </simulationFlow>\n')
    f.write('</simulation>\n')

def write_nh_bond_calc_rec(f):
    f.write('    <calculator name="bondCalculator" plugin="BondCalculator" />\n')
    
# == Physical Interaction Plug-ins ==========================
    
def write_nh_mpqc_esp_plane_rec(f, esp_window, output_dir):
    
    nh_home = get_nh_home()
    
    cpnt = esp_window.center * 1e-10
    centerPoint = (float(cpnt[0]), float(cpnt[1]), float(cpnt[2]))
    #print "ESP Window CenterPoint =", centerPoint
        
    npnt = esp_window.getaxis() * 1e-10
    
    # This is a temporary workaround until Brian fixes the normalPoint Y value issue (must be positive).
    # This forces ESP Windows to be oriented in the X-Z plane until it is fixed.
    # Mark 050927.
    normalPoint = (float(npnt[0]), 0.5, float(npnt[2])) 
    # normalPoint = (float(npnt[0]), float(abs(npnt[1])), float(npnt[2])) # KEEP THIS!!!
    #print "ESP Window NormalPoint =", normalPoint
        
    resolution = esp_window.resolution
    # print "ESP Window Resolution =", resolution
        
    cutoffHeight = esp_window.window_offset * 1e-10
    #print "ESP Window cutoffHeight =", cutoffHeight
    cutoffWidth = esp_window.edge_offset * 1e-10
    #print "ESP Window cutoffWidth =", cutoffWidth
    outputLength = esp_window.width * 1e-10
    #print "ESP Window outputLength =", outputLength

    f.write('\n')
    f.write('    <calculator name="espWindow" plugin="MPQC_SClib">\n')
    f.write('      <parameter name="logDirectory" value="%s/log" />\n' % nh_home)
    f.write('      <parameter name="dataDirectory" value="%s/data/MPQC_SClib" />\n' % nh_home)
    f.write('      <parameter name="basis" value="STO-3G" />\n')
    f.write('      <parameter name="method" value="HF" />\n')
    f.write('      <parameter name="desiredEnergyAccuracy" value="1.0e-3" />\n')
    f.write('      <parameter name="multiplicity" value="1" />\n')
    f.write('\n')
    f.write('      <parameter name="outputType" value="ESPplane" />\n')
    f.write('      <parameter name="resolution" value="%d" />\n' % resolution)
    f.write('\n')
    f.write('      <parameter name="centerPoint" value="%.1e %.1e %.1e" />\n' % centerPoint)
    f.write('      <parameter name="normalPoint" value="%1.1e %1.1e %1.1e" />\n' % normalPoint)
    f.write('      <parameter name="cutoffHeight" value="%1.1e" />\n' % cutoffHeight)
    f.write('      <parameter name="cutoffWidth" value="%1.1e" />\n' % cutoffWidth)
    f.write('      <parameter name="outputLength" value="%1.1e" />\n' % outputLength)
    f.write('    </calculator>\n')
    f.write('\n')
    f.write('    <result name="simResult" plugin="_ESP_Image">\n')
    f.write('      <parameter name="outputFilename" value="%s\\%s.png" />\n' % (output_dir, esp_window.name))
    f.write('    </result>\n')

def write_nh_mpqc_gd_rec(f):

    nh_home = get_nh_home()
    
    f.write('\n')
    f.write('    <calculator name="qmDynamicsInteraction" plugin="MPQC_SClib">\n')
    f.write('      <parameter name="logDirectory" value="%s/log" />\n' % nh_home)
    f.write('      <parameter name="dataDirectory" value="%s/data/MPQC_SClib" />\n' % nh_home)
    f.write('      <parameter name="basis" value="STO-3G" />\n')
    f.write('      <parameter name="method" value="HF" />\n')
    f.write('      <parameter name="gradientDynamics" value="yes" />\n')
    f.write('      <parameter name="deltaTbyTau" value="1.0" />\n')
    f.write('    </calculator>\n')
            

def write_nh_mpqc_gd_rec(f):
        
    nh_home = get_nh_home()
    
    f.write('\n')
    f.write('    <calculator name="physicalInteraction" plugin="REBO_MBM">\n')
    f.write('      <parameter name="dataDirectory" value="%s/data/REBO_MBM" />\n' % nh_home)
    f.write('    </calculator>\n')

#== Results Plug-ins ==========================

def write_nh_measurements_to_file_results_rec(f, output_dir):
    
    f.write('\n')
    f.write('    <result name="MeasurementSetToFile" plugin="MeasurementSetToFile">\n')
    f.write('      <parameter name="outputInterval" value="1" />\n')
    f.write('      <parameter name="outputFile"\n')
    f.write('        value="%s/data.txt" />\n' % output_dir)
    f.write('      <parameter name="datumSeparator" value="\t" />\n')
    f.write('    </result>\n')

def write_nh_povrayvideo_results_rec(f, output_dir, partname):
    
    nh_home = get_nh_home()
        
    # Need subdirectory for all the POV-Ray pov files.
    # Also need to add lighting, scene setup, background color, etc.
    f.write('\n')
    f.write('    <result name="POVRayVideo" plugin="POVRayVideo">\n')
    f.write('      <parameter name="outputInterval" value="1" />\n')
    f.write('      <parameter name="lengthMultiplier" value="1e10" />\n')
    f.write('      <parameter name="outputDirectory"\n')
    f.write('        value="%s/povray" />\n' % output_dir)
    f.write('      <parameter name="outputIdentifier" value="%s" />\n' % partname)
    # POV-Ray template.  Mark needs to write the include file for lighting and camera angle(s)
    # and put that file in the appropriate place (outdir/povray).
    f.write('      <parameter name="povTemplateFilename"\n')
    f.write('        value="%s/data/pov.tmplt" />')
    f.write('      <parameter name="mpegTemplateFilename"\n')
    f.write('        value="%s/data/mpeg_encode.param.tmplt" />\n' % nh_home)
    f.write('    </result>\n')

def write_nh_netcdf_results_rec(f, output_dir):
    
    f.write('\n')
    f.write('    <result name="simResult" plugin="NetCDF_DataSet">\n')
    f.write('      <parameter name="outputInterval" value="1" />\n')
    f.write('      <parameter name="outputDirectory"\n')
    f.write('        value="%s" />\n' % output_dir)
    f.write('      <parameter name="maxDataSets" value="-1" />\n')
    f.write('    </result>\n')

# end
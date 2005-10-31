# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
PlotTool.py

$Id$

bruce 050913 used env.history in some places.
'''
__author__ = "Mark"

from PlotToolDialog import *
from qt import *
import time
import sys, os, string, linecache
from HistoryWidget import redmsg, greenmsg
from movie import find_saved_movie #bruce 050329 fix bug 499
from platform import open_file_in_editor
import env

cmd = greenmsg("Plot Tool: ")

class PlotTool(PlotToolDialog):
    def __init__(self, assy, movie): #bruce 050326 added movie arg
        parent = assy.w
        PlotToolDialog.__init__(self, parent)
        self.movie = movie # before bruce 050326 was assy.current_movie
        self.setup()
        self.show() # Fixed bug 440-1.  Mark 050802.

    def setup(self):
        """Setup the Plot Tool dialog, including populating the combobox with plotting options.
        """
        # To setup the Plot Tool, we need to do the following:
        # 1. Make sure there is a valid DPB file. This is temporary since the Plot Tool will
        #     soon allow the user to open and plot any trace file.
        # 2. From the DPB filename, construct the trace filename and GNUplot filename.
        # 3. Read the header from the trace file to obtain:
        #   - Date and time
        #   - Trajectory (DPB) filename.  This is redundant now, but will be necessary when
        #      Plot Tool allows the user to open and plot any trace file.
        #   - The number of columns of data in the trace file so we can...
        # 4. Populate the plot combobox with the graph names
        
        # Make sure there is a DPB file for the assy. 
        if not self.movie or not self.movie.filename:
            msg = redmsg("No tracefile exists for this part.  To create one, run a simulation.")
            env.history.message(cmd + msg)
            return 1
        
        # Construct the trace file name.
        self.traceFile = self.movie.get_trace_filename()
#        print "PlotTool: Trace file = ", self.traceFile
        
        # Make sure the tracefile exists
        if not os.path.exists(self.traceFile):
            msg = redmsg("Trace file [" + self.traceFile + "] is missing.  Plot aborted.")
            env.history.message(cmd + msg)
            return 1
            
        # Construct the GNUplot filename.
        self.plotFile = self.movie.get_GNUplot_filename()
#        print "Plot file = ", self.plotFile
        
        # Now we read specific lines of the traceFile to read parts of the header we need.
        # I will change this soon so that we can find this header info without knowing what line they are on.
        # Mark 050310
        
        # If we've opened the tracefile once during this session, we
        # must check to see if the trace file has changed on disk.
        # Doesn't appear to be an issue calling checkcache before getline.
        #linecache.checkcache() 

        #Open trace file to read.
        traceFile = open(self.traceFile)
        traceLines = traceFile.readlines()        

        # Get Date from trace file from line #3 in the header.
        #header = linecache.getline(self.traceFile, 3)
        header = traceLines[2]
        hlist = string.split(header, ": ")
        self.date = hlist[1][:-1]
        
        # Get trajectory file name from trace file from line #5 in the header.
        header =  traceLines[4]#linecache.getline(self.traceFile, 5)
        hlist = string.split(header, ": ")
        self.dpbname = hlist[1][:-1]
#        print "Trajectory file name = ", self.dpbname
        
        # Get number of columns, located in line 14 of the header.
        hloc = 12 # Line number in file contain the "# n columns"
        header = traceLines[hloc-1]#linecache.getline(self.traceFile, hloc)
        hlist = string.split(header, " ")
        ncols = int(hlist[1])
#        print "Columns header:", header
#        print "ncols =", ncols
            
        # Populate the plot combobox with plotting options.
        if ncols:
            for i in range(ncols):
                gname =  traceLines[hloc + i]#linecache.getline(self.traceFile, hloc + 1 + i)
                self.plot_combox.insertItem(gname[2:-1])
        else: # No jigs in the part, so nothing to plot.  Revised msgs per bug 440-2.  Mark 050731.
            msg = redmsg("The part contains no jigs that write data to the trace file.  Nothing to plot.")
            env.history.message(cmd + msg)
            msg = "The following jigs write output to the tracefile: Measure Distance jigs, Rotary Motors, Linear Motors, Grounds, Thermostats and Thermometers."
            env.history.message(msg)
            return 1
        
        self.lastplot = 0
        
        traceFile.close()
        

    def genPlot(self):
        """Generates GNUplot plotfile, then calls self.runGNUplot.
        """
        col = self.plot_combox.currentItem() + 2 # Column number to plot
#        print "Selected plot # column =", col, "\n"
        
        # If this plot was the same as the last plot, just run GNUplot on the plotfile.
        # This allows us to edit the current plotfile in a text editor via "Open GNUplot File"
        # and replot without overwriting it.
        if col == self.lastplot: 
            self.runGNUplot(self.plotFile)
            return
        else:
            self.lastplot = col
            
        title = str(self.plot_combox.currentText()) # Plot title
        tlist = string.split(title, ":")
        ytitle = str(tlist[1]) # Y Axis title
        
        # Write GNUplot file
        f = open(self.plotFile,"w")
        
        if sys.platform == 'darwin': 
            f.write("set terminal aqua\n") # GNUplot for Mac needs this.
            
        f.write("set title \"%s\\n Trace file: %s\\n Created: %s\"\n"%(title, self.traceFile,self.date))
        f.write("set key left box\n")
        f.write("set xlabel \"time  (picoseconds)\"\n")
        f.write("set ylabel \"%s\"\n"%(ytitle))
        f.write("plot '%s' using 1:%d title \"Data Points\" with lines lt 2,\\\n"%(self.traceFile,col))
        f.write("       '%s' using 1:%d:(0.5) smooth acsplines title \"Average\" lt 3\n"%(self.traceFile,col))
        
        if sys.platform == 'win32': 
            # The plot will stay up until the OK or Cancel button is clicked.
            f.write("pause mouse \"Click OK or Cancel to Quit\"") 
        else: 
            # "pause mouse" doesn't work on Linux as it does on Windows.
            # I suspect this is because QProcess doesn't spawn a child, but forks a sibling process.
            # The workaround is thus: plot will stick around for 3600 seconds (1 hr).
            # Mark 050310
            f.write("pause 3600")
        
        f.close()

        self.runGNUplot(self.plotFile)

    def runGNUplot(self, plotfile):
        """Sends plotfile to GNUplot.
        """
        
        # Make sure plotfile exists
        if not os.path.exists(plotfile):
            msg = redmsg("Plotfile [" + program + "] is missing.  Plot aborted.")
            env.history.message(cmd + msg)
            return
            
        # filePath = the current directory NE-1 is running from.
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        # "program" is the full path to the GNUplot executable. 
        if sys.platform == 'win32': 
            program = os.path.normpath(filePath + '/../bin/wgnuplot.exe')
        else:
            program = os.path.normpath(filePath + '/../bin/gnuplot')

        #Huaicai 3/18:  set environment variable to make gluplot use a specific AquaTerm on Mac
        environVb = None
        if sys.platform == 'darwin':
            aquaPath = os.path.join(os.path.normpath(filePath + '/../bin'), 'AquaTerm.app')
            environVb =  QStringList(QString('AQUATERM_PATH=%s' % aquaPath))
	 
	        #The other option is to set it in the parent process using the Python way, 
	        # but the previous way is better.    
            #os.environ['AQUATERM_PATH']=aquaPath
        

        # Make sure GNUplot executable exists
        if not os.path.exists(program):
            msg = redmsg("GNUplot executable [" + program + "] is missing.  Plot aborted.")
            env.history.message(cmd + msg)
            return
        
        # Create arguments list for plotProcess.
#        args = [program, self.plotFile]
        args = [program, plotfile]
#        print "args = ", args
        arguments = QStringList()
        for arg in args:
            arguments.append(arg)
        
        # Run GNUplot as a separate process
        plotProcess = None
        try:
            plotProcess = QProcess()
            plotProcess.setArguments(arguments)
            rst = plotProcess.start(environVb)
               
            if not rst: 
                env.history.message(redmsg("GNUplot failed to run!"))
            else: 
                env.history.message("Running GNUplot file: " + plotfile)
            
        except: # We had an exception.
            print"exception in GNUplot; continuing: "
            if plotProcess:
                print "Killing process"
                plotProcess.kill()
                plotProcess = None
                
    def openTraceFile(self):
        """Opens the current tracefile in an editor.
        """
        open_file_in_editor(self.traceFile)

    def openGNUplotFile(self):
        """Opens the current GNUplot file in an editor.
        """
        open_file_in_editor(self.plotFile)

# == 

def simPlot(assy): # moved here from MWsemantics method, bruce 050327
    """Opens the Plot Tool dialog (and waits until it's dismissed),
    for the current movie if there is one, otherwise for a previously saved
    dpb file with the same name as the current part, if one can be found.
    Returns the dialog, after it's dismissed (probably useless),
    or None if no dialog was shown.
    """
    #bruce 050326 inferred docstring from code, then revised to fit my recent changes
    # to assy.current_movie, but didn't yet try to look for alternate dpb file names
    # when the current part is not the main part. (I'm sure that we'll soon have a wholly
    # different scheme for letting the user look around for preexisting related files to use,
    # like movie files applicable to the current part.)
    #    I did reorder the code, and removed the check on the current part having atoms
    # (since plotting from an old file shouldn't require movie to be valid for current part).
    #    This method should be moved into some other file.

    if assy.current_movie and assy.current_movie.filename:
        # (bruce 050326 asks: can an existing movie ever not have a filename? Depends on whether stored on error...)
        return PlotTool(assy, assy.current_movie) # Open Plot Tool dialog [and wait until it's dismissed]
        # [bruce comment 050324-27: retval is stored in main window as win.plotcntl,
        #  but never used. Conceivably, keeping it matters due to its refcount, but I doubt it.]

    # no valid current movie, look for saved one with same name as assy
    msg = redmsg("No simulation has been run yet.")
    env.history.message(cmd + msg)
    if assy.filename:
        if assy.part is not assy.tree.part:
            msg = redmsg("Warning: Looking for saved movie for main part, not for displayed clipboard item.")
            env.history.message(cmd + msg)
        mfile = assy.filename[:-4] + ".dpb"
        movie = find_saved_movie( assy, mfile)
            # just checks existence, not validity for current part or main part
        if movie:
            #e should we set this as current_movie? I don't see a good reason to do that,
            # user can open it if they want to. But I'll do it if we don't have one yet.
            if not assy.current_movie:
                assy.current_movie = movie
            #e should we switch to the part for which this movie was made?
            # No current way to tell how to do that, and this might be done even if it's not valid
            # for any loaded Part. So let's not... tho we might presume (from filename choice we used)
            # it was valid for Main Part. Maybe print warning for clip item, and for not valid? #e
            msg = "Using previously saved movie for this part."
            env.history.message(cmd + msg)
            return PlotTool(assy, movie)
        else:
            msg = redmsg("Can't find previously saved movie for this part.")
            env.history.message(cmd + msg)
    return

# end

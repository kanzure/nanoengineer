# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
PlotTool.py

$Id$
'''
__author__ = "Mark"

from PlotToolDialog import *
from qt import *
import time
import sys, os, string, linecache
from HistoryWidget import redmsg

class PlotTool(PlotToolDialog):
    def __init__(self, assy):
        PlotToolDialog.__init__(self)
        self.assy = assy
        if self.setup(): return
        self.exec_loop()

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
        if not self.assy.m.filename:
            msg = "Plot Tool: No tracefile exists for this part.  To create one, run a simulation."
            self.assy.w.history.message(redmsg(msg))
            return 1
        
        # Construct the trace file name.
        self.traceFile = self.assy.m.get_trace_filename()
#        print "PlotTool: Trace file = ", self.traceFile
        
        # Make sure the tracefile exists
        if not os.path.exists(self.traceFile):
            msg = "Plot Tool: Trace file [" + self.traceFile + "] is missing.  Plot aborted."
            self.assy.w.history.message(redmsg(msg))
            return 1
            
        # Construct the GNUplot filename.
        self.plotFile = self.assy.m.get_GNUplot_filename()
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
                self.plotCB.insertItem(gname[2:-1])
        else: # No jigs in the part, so nothing to plot.
            msg = "Plot Tool: No jigs in this part.  Nothing to plot."
            self.assy.w.history.message(redmsg(msg))
            return 1
        
        self.lastplot = 0
        
        traceFile.close()
        

    def genPlot(self):
        """Generates GNUplot plotfile, then calls self.runGNUplot.
        """
        col = self.plotCB.currentItem() + 2 # Column number to plot
#        print "Selected plot # column =", col, "\n"
        
        # If this plot was the same as the last plot, just run GNUplot on the plotfile.
        # This allows us to edit the current plotfile in a text editor via "Open GNUplot File"
        # and replot without overwriting it.
        if col == self.lastplot: 
            self.runGNUplot(self.plotFile)
            return
        else:
            self.lastplot = col
            
        title = str(self.plotCB.currentText()) # Legend title
        tlist = string.split(title, ":")
        ytitle = str(tlist[1]) # Y Axis title
        
        # Write GNUplot file
        f = open(self.plotFile,"w")
        
        if sys.platform == 'darwin': 
            f.write("set terminal aqua\n") # GNUplot for Mac needs this.
            
        f.write("set title \"Trace file: %s\\n Created: %s\"\n"%(self.traceFile,self.date))
        f.write("set key left box\n")
        f.write("set xlabel \"time  (picoseconds)\"\n")
        f.write("set ylabel \"%s\"\n"%(ytitle))
        f.write("plot '%s' using 1:%d title \"%s\" with lines lt 2,\\\n"%(self.traceFile,col,title))
        f.write("       '%s' using 1:%d:(0.5) smooth acsplines title \"%s\" lt 3\n"%(self.traceFile,col,title))
        
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
            msg = "Plot Tool: Plotfile [" + program + "] is missing.  Plot aborted."
            self.assy.w.history.message(redmsg(msg))
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
	 #print "aquaPath: ", aquaPath
             environVb =  QStringList(QString('AQUATERM_PATH= %s' % aquaPath))
	 
	 #It seems the environment variable passed to the QProcess is not working, so set it in the parent process using the Python way.      
             os.environ['AQUATERM_PATH']=aquaPath
        
        #It seems the environment variable passed to the QProcess is not working, so disable it.
        environVb = None        

        # Make sure GNUplot executable exists
        if not os.path.exists(program):
            msg = "Plot Tool: GNUplot executable [" + program + "] is missing.  Plot aborted."
            self.assy.w.history.message(redmsg(msg))
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
                self.assy.w.history.message(redmsg("GNUplot failed to run!"))
            else: 
                self.assy.w.history.message("Running GNUplot file: " + plotfile)
            
        except: # We had an exception.
            print"exception in GNUplot; continuing: "
            if plotProcess:
                print "Killing process"
                plotProcess.kill()
                plotProcess = None
                
    def openTraceFile(self):
        """Opens the current tracefile in an editor.
        """
        self.openPlotFile(self.traceFile)

    def openGNUplotFile(self):
        """Opens the current GNUplot file in an editor.
        """
        self.openPlotFile(self.plotFile)

    def openPlotFile(self, file):
        """Opens a file in a standard text editor.
        """
        editor = self.get_text_editor()
        
        if os.path.exists(editor):
            args = [editor, file]
#            print  "editor = ",editor
#            print  "Spawnv args are %r" % (args,)

            try:
                # Spawn the editor.
                kid = os.spawnv(os.P_NOWAIT, editor, args)
            except: # We had an exception.
                print_compact_traceback("Exception in editor; continuing: ")
                msg = "Cannot open file " + file + ".  Trouble spawning editor " + editor
                self.assy.w.history.message(redmsg(msg))
        else:
            msg = "Cannot open file " + file + ".  Editor " + editor + " not found."
            self.assy.w.history.message(redmsg(msg))
            
    def get_text_editor(self):
        """Returns then name of a text editor for this platform.
        """
        if sys.platform == 'win32': # Windows
            editor = "C:/WINDOWS/notepad.exe"
        elif sys.platform == 'darwin': # MacOSX
            editor = "/usr/bin/open"
        else: # Linux
            editor = "/usr/bin/kwrite"
            
        return editor
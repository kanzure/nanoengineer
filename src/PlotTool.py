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
        self.setup()
        self.exec_loop()

    def setup(self):

        print "Movie file = [", self.assy.m.filename, "]"
        fullpath, ext = os.path.splitext(self.assy.m.filename)
        self.traceFile = fullpath + "-trace.txt"
        self.plotFile = fullpath + '.plt'
        print "Trace file = ", self.traceFile
        print "Plot file = ", self.plotFile
        
        # Get Date from trace file.
        header = linecache.getline(self.traceFile, 3)
        hlist = string.split(header, ": ")
        self.date = hlist[1][:-1]
        
        # Get trajectory file name from trace file.
        header = linecache.getline(self.traceFile, 5)
        hlist = string.split(header, ": ")
        self.dpbname = hlist[1][:-1]
        print "Trajectory file name = ", self.dpbname
        
        # Get number of columns
        hloc = 14 # Line number in file contain the "# n columns"
        header = linecache.getline(self.traceFile, hloc)
        hlist = string.split(header, " ")
        ncols = int(hlist[1])
        
        # Populate the plot combobox with plotting options.
        for i in range(ncols):
            gname = linecache.getline(self.traceFile, hloc + 1 + i)
            self.plotCB.insertItem(gname[2:-1])

    def genPlot(self):
        """Plots the selected graph using GNUplot.
        """
        col = self.plotCB.currentItem() + 2 # Column number to plot
#        print "Selected plot # column =", col, "\n"
        title = str(self.plotCB.currentText()) # Legend title
        tlist = string.split(title, ":")
        ytitle = str(tlist[1]) # Y Axis title
        
        # Write GNUplot file
        f = open(self.plotFile,"w")
        f.write("set title \"Trajectory file: %s\\n Created %s\"\n"%(self.dpbname,self.date))
        f.write("set key left box\n")
        f.write("set xlabel \"time  (picoseconds)\"\n")
        f.write("set ylabel \"%s\"\n"%(ytitle))
        f.write("plot '%s' using 1:%d title \"%s\" with lines lt 2,\\\n"%(self.traceFile,col,title))
        f.write("       '%s' using 1:%d:(0.5) smooth acsplines title \"%s\" lt 3\n"%(self.traceFile,col,title))
        f.write("pause -1 \"Click OK or Cancel to Quit\"")
        f.close()
        
        # filePath = the current directory NE-1 is running from.
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        # "program" is the full path to the GNUplot executable. 
        if sys.platform == 'win32': 
            program = os.path.normpath(filePath + '/../bin/pgnuplot.exe')
        else:
            program = os.path.normpath(filePath + '/../bin/pgnuplot')
        
        # Make sure GNUplot exists
        if not os.path.exists(program):
            msg = "GNUplot [" + program + "] is missing.  Plot aborted."
            self.assy.w.history.message(redmsg(msg))
            return
        
        args = [program, self.plotFile]
#        print "args = ", args

        # Create arguments list for plotProcess.
        arguments = QStringList()
        for arg in args:
            arguments.append(arg)

        # Run GNUplot as a separate process
        plotProcess = None
        try:
            plotProcess = QProcess()
            plotProcess.setArguments(arguments)
            if not plotProcess.start(): print "GNUplot failed to run"
            
        except: # We had an exception.
            print"exception in GNUplot; continuing: "
            if plotProcess:
                print "Killing process"
                plotProcess.kill()
                plotProcess = None
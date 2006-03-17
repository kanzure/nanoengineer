# Copyright (c) 2005-2006 Nanorex, Inc.  All rights reserved.
'''
PlotTool.py

$Id$

bruce 050913 used env.history in some places.

bruce 060105 revised trace file header parsing to fix bug 1266
and make it more likely to keep working with future revisions
to trace file format.
'''
__author__ = "Mark"

from PlotToolDialog import *
from qt import *
import time
import sys, os, string
from HistoryWidget import redmsg, greenmsg, orangemsg
from movie import find_saved_movie
from platform import open_file_in_editor
import env

debug_plottool = False

cmd = greenmsg("Plot Tool: ") #### this is bad, needs to be removed, but that's hard to do safely [bruce 060105 comment]

class PlotTool(PlotToolDialog):
    # Bug 1484, wware 060317 - PlotTool requires a trace file and a plot file.
    def __init__(self, assy, basefilename):
        parent = assy.w
        PlotToolDialog.__init__(self, parent)
        try:
            tracefilename = basefilename[:-4] + "-xyztrace.txt"
            inf = open(tracefilename)
            inf.close()
        except IOError:
            tracefilename = basefilename[:-4] + "-trace.txt"
        plotfilename = basefilename[:-4] + "-plot.txt"
        self.traceFile = tracefilename
        self.plotFile = plotfilename
        self.setup()
        self.show() # Fixed bug 440-1.  Mark 050802.

    def setup(self):
        """Setup the Plot Tool dialog, including populating the combobox with plotting options.
        """
        # To setup the Plot Tool, we need to do the following:
        # 1. Read the header from the trace file to obtain:
        #   - Date and time
        #   - Trajectory (DPB) filename.  This is redundant now, but will be necessary when
        #      Plot Tool allows the user to open and plot any trace file.
        #   - The number of columns of data in the trace file so we can...
        # 2. Populate the plot combobox with the graph names
        # Make sure the tracefile exists
        if not os.path.exists(self.traceFile):
            msg = redmsg("Trace file [" + self.traceFile + "] is missing.  Plot aborted.")
            env.history.message(cmd + msg)
            return 1
            
        # Now we read specific lines of the traceFile to read parts of the header we need.
        # I will change this soon so that we can find this header info without knowing what line they are on.
        # Mark 050310
        
        #bruce 060105: changing this now, to fix bug 1266.
        
        # If we've opened the tracefile once during this session, we
        # must check to see if the trace file has changed on disk.
        # To avoid this issue we reopen it every time and make sure to close it
        # and don't use any sort of line cache.
        # Mark had a comment about this but I [bruce 060105] am not sure what he meant by it:
            # Doesn't appear to be an issue calling checkcache before getline.
            #linecache.checkcache() 
        # He also had some commented out code such as "#linecache.getline(self.traceFile, 5)"
        # which I've removed (as of rev 1.32).

        #Open trace file to read.
        traceFile = open(self.traceFile, 'rU') #bruce 060105 added 'rU'
        traceLines = traceFile.readlines() #e could optim by reading only the first XXX lines (100 or 1000)
        traceFile.close()
        headerLines = [] # all lines of header (used to count line numbers and for column headings)
        field_to_content = {} # maps fieldname to content,
            # where entire line is "#" + fieldname + ":" + content, but we strip outer whitespace on field and content
        columns_lineno = -1 # line number (0-based) of "%d columns" (-1 == not yet known)
        number_of_columns = 0 # will be changed to correct value when that's found
        for line in traceLines:
            # loop over lines, but stop when we find end of header, and partly stop when we find "%d columns".
            if not line.startswith("#"): # note: most start with "# ", but some are just "#" and nothing more.
                break # first non-comment line ends the header
            # header line
            headerLines.append(line)
            if ":" in line and columns_lineno == -1: # not all of these contain ": "
                field, content = line.split(":", 1)
                field = field[1:].strip() # get rid of "#" before stripping field
                content = content.strip() # (note: zaps final newline as well as blanks)
                if field.endswith(" columns"):
                    # assume we found "# <nnn> columns:" and column-header lines will follow (but no more field:content lines)
                    columns_lineno = len(headerLines) - 1 # 0-based, since purpose is internal indexing
                        # note: this assignment also makes this loop stop looking for field:content lines
                    number_of_columns = int(field.split()[0])
                else:
                    field_to_content[field] = content
                pass
            pass
        del traceLines

        if debug_plottool:
            print "columns_lineno (0-based) =", columns_lineno
            print "  that line is:", headerLines[columns_lineno]
            print "number_of_columns =", number_of_columns
            print "field_to_content = %r" % (field_to_content,)

        # figure out column headers all at once
        column_header = {}
        for i in range(number_of_columns):
            column_header[i] = headerLines[columns_lineno + 1 + i][2:-1]
                # strip off "# " and final newline (would .strip be better or worse??)
            if debug_plottool:
                print "column header %d is %r" % (i, column_header[i],)
            pass

        # use the parsed header
        # (the code above depends only on the trace file format;
        #  the code below depends only on our use of it here)
        
        self.date = field_to_content["Date and Time"]
            # Mark's code had [:-1] after that -- I'm guessing it was to zap final newline, now done by .strip(),
            # so I'm leaving it out for now. [bruce 060105]
        
        # Get trajectory file name
        self.dpbname = field_to_content["Output File"]
        
        ncols = number_of_columns
        
        # Populate the plot combobox with plotting options.
        if ncols:
            for i in range(ncols):
                self.plot_combox.insertItem( column_header[i] )
        else: # No jigs in the part, so nothing to plot.  Revised msgs per bug 440-2.  Mark 050731.
            msg = redmsg("The part contains no jigs that write data to the trace file.  Nothing to plot.")
            env.history.message(cmd + msg)
            msg = "The following jigs write output to the tracefile: Measurement jigs, Rotary Motors, Linear Motors, Anchors, Thermostats and Thermometers."
            env.history.message(msg)
            return 1
        
        self.lastplot = 0
        return

    def genPlot(self):
        """Generates GNUplot plotfile, then calls self.runGNUplot.
        """
        col = self.plot_combox.currentItem() + 2 # Column number to plot
        
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
        return PlotTool(assy, assy.current_movie.filename)
    # wware 060317, bug 1484
    if assy.filename:
        return PlotTool(assy, assy.filename)

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

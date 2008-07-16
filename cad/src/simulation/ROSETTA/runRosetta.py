"""
runRosetta.py -- setting up and running rosetta simulations

@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

History:
Urmi copied this file from runSim.py and then modified it.

To do: implement rosetta design for highlighted protein chunk
"""
from files.pdb.files_pdb import writepdb
from files.pdb.files_pdb import insertpdb
from model.chunk import Chunk
from utilities.debug import print_compact_traceback
from platform_dependent.PlatformDependent import find_or_make_Nanorex_subdir
import os, sys, time
from widgets.StatusBar import AbortHandler
from datetime import datetime
from PyQt4.Qt import QApplication, QCursor, Qt, QStringList
from PyQt4.Qt import QProcess, QFileInfo
from utilities.Log import redmsg, greenmsg, orangemsg, quote_html, _graymsg
import foundation.env as env
from geometry.VQT import A, vlen
import re
from utilities.constants import filesplit
from processes.Process import Process
from processes.Plugins import checkPluginPreferences
from utilities.prefs_constants import rosetta_enabled_prefs_key
from utilities.prefs_constants import rosetta_path_prefs_key, rosetta_database_prefs_key
from protein.model.Protein import write_rosetta_resfile


def getScoreFromOutputFile(pdbFilePath):
    
    f = open(pdbFilePath, 'r')
    if f:
        doc = f.readlines()
        for line in doc:
            #first instance of score
            valFind = line.find("score")
            if valFind!=-1:
            #process this line to read the total score
                words = line[15:]
                score = words.strip()
                f.close()
                return score
    else:
        print "Output Pdb file cannot be read to obtain score"
    f.close()
    return None
    

def processFastaFile(fastaFilePath):
    proteinSeqTupleList = []
    f = open(fastaFilePath, 'r')

    if f:
        doc = f.readlines()
        line1 = doc[0]
        i = 0
        while i < len(doc):
            proteinName = line1[2:len(line1)-1]
            if proteinName.find(".pdb")!= -1:
                proteinName = proteinName[0:len(proteinName)-4]
            #this line is bound to be the sequence    
            i = i + 1    
            line2 = doc[i]    
            proteinSeq = line2[0:len(line2)-1]
            # in case of long sequences, these lines may have part of sequences
            i = i + 1
            if i >= len(doc):
                tupleEntry = (proteinName, proteinSeq)
                proteinSeqTupleList.append(tupleEntry)
                break

            line3 = doc[i]
            while 1:
                if line3.find(">")!= -1:
                    #indicates begining of new protein sequence
                    line1 = line3
                    tupleEntry = (proteinName, proteinSeq)
                    proteinSeqTupleList.append(tupleEntry)
                    break
                
                #part of the old sequence
                proteinSeq = proteinSeq + line3[0:len(line3)-1]
                i = i + 1
                #writing the last sequence
                if i >= len(doc):
                    tupleEntry = (proteinName, proteinSeq)
                    proteinSeqTupleList.append(tupleEntry)
                    break

                line3 = doc[i]

    else:
        print "File cannot be read"
    
    f.close()

    return proteinSeqTupleList

def highlightDifferencesInSequence(proteinSeqList):
    modList = [proteinSeqList[0][1]]
    baseList = proteinSeqList[0][1]
    count = 0
    for i in range(1,len(proteinSeqList)):
        currentProtSeq = proteinSeqList[i][1]
        
        tempSeq = ""
        for j in range(0, len(baseList)):
            if baseList[j] == currentProtSeq[j]:
                tempSeq = tempSeq + baseList[j]
                count = count + 1
            else:
                tempSeq = tempSeq + "<font color=red>" + currentProtSeq[j] + "</font>"
        modList.append(tempSeq)
        
        #Similarity measurement for the original protein and protein with minimum 
        #score
        simMeasure = (float)((count * 100)/len(baseList))
        similarity = str(simMeasure) + "%"
    return modList, similarity

class RosettaRunner:
    """
    Class for running the rosetta simulator.
    [subclasses can run it in special ways, maybe]
    """
    PREPARE_TO_CLOSE = False
    used_atoms = None
    
    def __init__(self, part, mflag,
                 simaspect = None,
                 cmdname = "Rosetta Design",
                 cmd_type = 'Fixed_Backbone_Sequence_Design',
                 useRosetta = False,
                 background = False,
                 ):
            
        """
        set up external relations from the part we'll operate on;
        take mflag arg, since someday it'll specify the subclass to use.
        """
        self.assy = assy = part.assy #
        self.win = assy.w  
        self.part = part 
        self.mflag = mflag 
        self.simaspect = simaspect 
        self.errcode = 0 # public attr used after we're done;
            # 0 or None = success (so far), >0 = error (msg emitted)
        self.said_we_are_done = False 
        self.useRosetta = useRosetta
        self.background = background
        self.rosettaLog = None
        self.tracefileProcessor = None
        self.cmdname = cmdname
        self.cmd_type = cmd_type #060705
        return
    
    def sim_input_filename(self, part):
    #write the pdb for the part that is in the NE-1 window now and set the 
    #filename to that pdb
        
        pdbId, chunk = self.getPDBIDFromChunk(part)
        if pdbId is None:
            return None
        
        fileName = pdbId + '.pdb'
        dir = os.path.dirname(self.tmp_file_prefix)
        fileLocation = dir + '/' + fileName
        writepdb(part, fileLocation) 
        
        return fileName
    
    def getPDBIDFromChunk(self, part):
        chunkList = []     
        def getAllChunks(node):
            if isinstance(node, Chunk):
                chunkList.append(node)
        part.topnode.apply2all(getAllChunks)    
        for chunk in chunkList:
            if chunk.isProteinChunk():
                pdbID = chunk.protein.get_pdb_id()   
                chainID = chunk.protein.get_chain_id()
                if chainID =='':
                    return pdbID, chunk
                else:
                    pdbID = pdbID + chainID
                    return pdbID, chunk
        return None, None
    
    def removeOldOutputPDBFiles(self):
        dir = os.path.dirname(self.tmp_file_prefix)
        infile = self.sim_input_file
        outpath = infile[0:len(infile) - 4] + '*' + '_0001.pdb'
        from fnmatch import fnmatch
        for file in os.listdir(dir):
            fullname = os.path.join( dir, file)
            if os.path.isfile(fullname):
                if fnmatch( file, outpath):
                    os.remove(fullname)
        return
    
    def setup_sim_args(self):
        """
        Set up arguments for the simulator,
        by constructing a command line for the standalone executable simulator,
        
        """
        
        use_command_line = True
        movie = self._movie # old-code compat kluge
        self.totalFramesRequested = movie.totalFramesRequested
        self.update_cond = movie.update_cond
        program = self.program
        path = self.path
        infile = self.sim_input_file
        self.outfile = infile[0:len(infile) - 4] + '_out'
        mflag = self.mflag
        self._simopts = self._simobj = self._arguments = None # appropriate subset of these is set below
        #bug in rosetta: simulation does not work in  pdbID_0001.pdb exists in 
        #this directory, hence always remove it
        self.removeOldOutputPDBFiles()
        
            
        if use_command_line:
            
            #Urmi 20080709 Support for fixed backbone sequence design for now
            args = [
                    '-paths',  str(self.path),
                    '-design',
                    '-fixbb',
                    '-profile',
                    '-resfile', str(self.resFile),
                    '-pdbout', str(self.outfile),
                    '-s', infile]
            
            self._arguments = args
        
        return # from setup_sim_args    
    
    def set_options_errQ(self): #e maybe split further into several setup methods? #bruce 051115 removed unused 'options' arg
        """
        Figure out and set filenames, including sim executable path.
        All inputs and outputs are self attrs or globals or other obj attrs...
        except, return error code if sim executable missing
        or on other errors detected by subrs.
        """
        part = self.part
        movie = self._movie
        
        # simFilesPath = "~/Nanorex/RosettaDesignFiles".
        simFilesPath = find_or_make_Nanorex_subdir('RosettaDesignFiles')

        # Create temporary part-specific filename, for example:
        # "partname-minimize-pid1000".
        # We'll be appending various extensions to tmp_file_prefix to make temp
        # file names for sim input and output files as needed (e.g. mmp, xyz,
        # etc.)
        
        pdbId, chunk = self.getPDBIDFromChunk(part)
        #write the residue file
        resFile = pdbId + ".resfile"
        resFilePath = os.path.join(simFilesPath, resFile)
        success = write_rosetta_resfile(resFilePath, chunk)
        if success:
            self.resFile = resFile
        else:
            print "Residue file could not be written"
        
        #remove all previously existing fasta files
        fastaFile = pdbId + "_out_design.fasta"
        checkPointFile = pdbId + "_out_design.checkpoint"
        checkPointPath = os.path.join(simFilesPath, checkPointFile)
        fastaFilePath = os.path.join(simFilesPath, fastaFile)
        if os.path.exists(fastaFilePath):
            os.remove(fastaFilePath)
        
        if os.path.exists(checkPointPath):
            os.remove(checkPointPath)
            
        if pdbId is None:
            basename = "Untitled"
        else:
            basename = pdbId
        timestampString = ""
        if (self.background):
            # Add a timestamp to the pid so that multiple backgrounded
            # calculations don't clobber each other's files.
            timestamp = datetime.today()
            timestampString = timestamp.strftime(".%y%m%d%H%M%S")
        self.tmp_file_prefix = \
            os.path.join(simFilesPath,
                         "%s-rosetta-design-pid%d%s" % (basename, os.getpid(),
                                                  timestampString))

        
        #get program path, database path and write path.txt
        self.program = self.getExecutablePluginPath()
        if self.program is None:
            msg = redmsg("The simulator program is missing.  Simulation aborted.")
            env.history.message(self.cmdname + ": " + msg)
            return -1
        databasePath = self.getDatabasePluginPath()
        if databasePath is None:
            msg = redmsg("The protein database is missing.  Simulation aborted.")
            env.history.message(self.cmdname + ": " + msg)
            return -1
        self.path = self.getPathLocation(databasePath, simFilesPath)
        
        return None # no error
    
    def getPathLocation(self,dataBasePath, simFilesPath):
        #simplest would be to overwrite the path's file everytime, instead of
        #doing text processing to figure out if the file has changed
        # paths.txt is small enough to do so
        simFilesPath = simFilesPath + '/'
        pathFile = simFilesPath + "paths.txt"
        f = open(pathFile, "w+")
        line = "Rosetta Input/Output Paths (order essential)\n"
        f.write(line)
        line = "path is first '/', './',or  '../' to next whitespace, must end with '/'\n"
        f.write(line)
        line = "INPUT PATHS:\n"
        f.write(line)
        word = ["Temp", "Temp"]
        
        # input files wil always be in this directory
        tempWord = "pdb1"
        word[0] = "%-32s" % tempWord
        #simFilesPath = "/Users/marksims/Nanorex/RosettaDesignFiles/"
        tempWord = simFilesPath + "\n"
        word[1] = tempWord
        line = ''.join(word)
        f.write(line)
        
        tempWord = "pdb2"
        word[0] = "%-32s" % tempWord
        tempWord = simFilesPath + "\n"
        word[1] = tempWord
        line = ''.join(word)
        f.write(line)

        tempWord = "alternate data files"
        word[0] = "%-32s" % tempWord
        word[1] = dataBasePath + '/\n'
        line = ''.join(word)
        f.write(line)

        tempWord = "fragments"
        word[0] = "%-32s" % tempWord
        tempWord = simFilesPath + "\n"
        word[1] = tempWord
        line = ''.join(word)
        f.write(line)

        tempWord = "structure dssp,ssa (dat,jones)"
        word[0] = "%-32s" % tempWord
        tempWord = simFilesPath + "\n"
        word[1] = tempWord
        line = ''.join(word)
        f.write(line)

        tempWord = "sequence fasta,dat,jones"
        word[0] = "%-32s" % tempWord
        tempWord = simFilesPath + "\n"
        word[1] = tempWord
        line = ''.join(word)
        f.write(line)

        tempWord = "constraints"
        word[0] = "%-32s" % tempWord
        tempWord = simFilesPath + "\n"
        word[1] = tempWord
        line = ''.join(word)
        f.write(line)

        tempWord = "starting structure"
        word[0] = "%-32s" % tempWord
        tempWord = simFilesPath + "\n"
        word[1] = tempWord
        line = ''.join(word)
        f.write(line)

        tempWord = "data files"
        word[0] = "%-32s" % tempWord
        tempWord = dataBasePath + "/\n"
        word[1] = tempWord
        line = ''.join(word)
        f.write(line)

        line = "OUTPUT PATHS:\n"
        f.write(line)

        tempWord = "movie"
        word[0] = "%-32s" % tempWord
        tempWord = simFilesPath + "\n"
        word[1] = tempWord
        line = ''.join(word)
        f.write(line)

        tempWord = "pdb path"
        word[0] = "%-32s" % tempWord
        tempWord = simFilesPath + "\n"
        word[1] = tempWord
        line = ''.join(word)
        f.write(line)

        tempWord = "score"
        word[0] = "%-32s" % tempWord
        tempWord = simFilesPath + "\n"
        word[1] = tempWord
        line = ''.join(word)
        f.write(line)

        tempWord = "status"
        word[0] = "%-32s" % tempWord
        tempWord = simFilesPath + "\n"
        word[1] = tempWord
        line = ''.join(word)
        f.write(line)

        tempWord = "user"
        word[0] = "%-32s" % tempWord
        tempWord = simFilesPath + "\n"
        word[1] = tempWord
        line = ''.join(word)
        f.write(line)

        line = "FRAGMENTS: (use '*****' in place of pdb name and chain)\n"
        f.write(line)

        tempWord = "2"
        word[0] = "%-39s" % tempWord
        tempWord = "number of valid fragment files\n"
        word[1] = tempWord
        line = ''.join(word)
        f.write(line)

        tempWord = "3"
        word[0] = "%-39s" % tempWord
        tempWord = "frag file 1 size\n"
        word[1] = tempWord
        line = ''.join(word)
        f.write(line)

        tempWord = "aa*****03_05.200_v1_3"
        word[0] = "%-39s" % tempWord
        tempWord = "name\n"
        word[1] = tempWord
        line = ''.join(word)
        f.write(line)

        tempWord = "9"
        word[0] = "%-39s" % tempWord
        tempWord = "frag file 2 size\n"
        word[1] = tempWord
        line = ''.join(word)
        f.write(line)

        tempWord = "aa*****09_05.200_v1_3"
        word[0] = "%-39s" % tempWord
        tempWord = "name\n"
        word[1] = tempWord
        line = ''.join(word)
        f.write(line)
        f.close()
        return pathFile
    
    def getExecutablePluginPath(self):
        
        plugin_name = "ROSETTA"
        plugin_prefs_keys = (rosetta_enabled_prefs_key, rosetta_path_prefs_key)
            
        errorcode, errortext_or_path = \
                 checkPluginPreferences(plugin_name, plugin_prefs_keys)
        if errorcode:
            msg = redmsg("Verify Plugin: %s (code %d)" % (errortext_or_path, errorcode))
            env.history.message(msg)
            return None
        program_path = errortext_or_path
        
        return program_path
    
    
    def getDatabasePluginPath(self):
        
        plugin_name = "ROSETTA_DATABASE"
        #Urmi 20080710: using the same code as exectuables. Its kind of bad
        # but probably ok before RosettaCon
        plugin_prefs_keys = (rosetta_enabled_prefs_key, rosetta_database_prefs_key)
            
        errorcode, errortext_or_path = \
                 checkPluginPreferences(plugin_name, plugin_prefs_keys)
        if errorcode:
            msg = redmsg("Verify Plugin: %s (code %d)" % (errortext_or_path, errorcode))
            env.history.message(msg)
            return None
        dataBase_path = errortext_or_path
        return dataBase_path
    
    def run_using_old_movie_obj_to_hold_sim_params(self, movie):
        self._movie = movie 
        #set the program path, database path and write the paths.txt in here
        self.errcode = self.set_options_errQ( )
        if self.errcode: # used to be a local var 'r'
            return
        self.sim_input_file = self.sim_input_filename(self.part)
        if self.sim_input_file is None:
            return
           
        self.set_waitcursor(True)
        progressBar = self.win.statusBar().progressBar
        
        # Disable some QActions (menu items/toolbar buttons) while the sim is running.
        self.win.disable_QActions_for_sim(True)

        try: #bruce 050325 added this try/except wrapper, to always restore cursor
            self.simProcess = None #bruce 051231
            self.setup_sim_args()
            progressBar.setRange(0, 0)
            progressBar.reset()
            progressBar.show()
            env.history.statusbar_msg("Running Rosetta")
            
            rosettaFullBaseFileName = self.tmp_file_prefix 
            rosettaFullBaseFileInfo = QFileInfo(rosettaFullBaseFileName)
            rosettaWorkingDir = rosettaFullBaseFileInfo.dir().absolutePath()
            rosettaBaseFileName = rosettaFullBaseFileInfo.fileName()
            
            
                 
            rosettaProcess = Process()
            rosettaProcess.setProcessName("rosetta")
            rosettaProcess.redirect_stdout_to_file("%s-rosetta-stdout.txt" %
                rosettaFullBaseFileName)
            rosettaProcess.redirect_stderr_to_file("%s-rosetta-stderr.txt" %
                rosettaFullBaseFileName)
            rosettaStdOut = rosettaFullBaseFileName + "-rosetta-stdout.txt"
            rosettaProcess.setWorkingDirectory(rosettaWorkingDir)
            environmentVariables = rosettaProcess.environment()
            rosettaProcess.setEnvironment(environmentVariables)
            msg = greenmsg("Starting Rosetta sequence design")
            env.history.message(self.cmdname + ": " + msg)
            env.history.message("%s: Rosetta files at %s%s%s.*" %
                (self.cmdname, rosettaWorkingDir, os.sep,
                 rosettaFullBaseFileInfo.completeBaseName()))
            
            abortHandler = AbortHandler(self.win.statusBar(), "rosetta")
            errorCode = rosettaProcess.run(self.program, self._arguments, False, abortHandler)
            
            abortHandler = None
            if (errorCode != 0):
                if errorCode == -2: # User pressed Abort button in progress dialog.
                    msg = redmsg("Aborted.")
                    env.history.message(self.cmdname + ": " + msg)
                    env.history.statusbar_msg("")
                    if self.simProcess: #bruce 051231 added condition (since won't be there when use_dylib)
                        self.simProcess.kill()
                else: 
                    msg = redmsg("Rosetta sequence design failed. For details check" + rosettaStdOut)
                    env.history.message(self.cmdname + ": " + msg)
                    self.errcode = 2;
                    env.history.statusbar_msg("")
            else:
                #run has been successful
                #open pdb file
                env.history.statusbar_msg("")
                errorInStdOut = self.checkErrorInStdOut(rosettaStdOut)
                if errorInStdOut:
                    msg = redmsg("Rosetta sequence design failed, Rosetta returned %d" % errorCode)
                    env.history.message(self.cmdname + ": " + msg)
                    env.history.statusbar_msg("")
                else:    
                    env.history.message(self.cmdname + ": " + msg)
                    outputFile = self.outfile + '_0001.pdb'
                    outPath = os.path.join(os.path.dirname(self.tmp_file_prefix), outputFile)
                    if os.path.exists(outPath):
                        msg = greenmsg("Rosetta sequence design succeeded")
                        env.history.message(self.cmdname + ": " + msg)
                        insertpdb(self.assy, outPath, None)
                        env.history.statusbar_msg("")
                        fastaFile = self.outfile + "_design.fasta" 
                        fastaFilePath = os.path.join(os.path.dirname(self.tmp_file_prefix), fastaFile)
                        proteinSeqList = processFastaFile(fastaFilePath)
                        score = getScoreFromOutputFile(outPath)
                        if score is not None and proteinSeqList is not []:
                            self.showResults(score, proteinSeqList)
                        
                    else:
                        msg1 = redmsg("Rosetta sequence design failed. ")
                        msg2 = redmsg(" %s file was never created by Rosetta." % outputFile)
                        msg = msg1 + msg2
                        env.history.message(self.cmdname + ": " + msg)
                        env.history.statusbar_msg("")
        
        except:
            print_compact_traceback("bug in simulator-calling code: ")
            self.errcode = -11111
        self.set_waitcursor(False)
        self.win.disable_QActions_for_sim(False)
        env.history.statusbar_msg("")
        if not self.errcode:
            return # success
        
        return # caller should look at self.errcode
    
    def showResults(self, score, proteinSeqList):
        
        from foundation.wiki_help import WikiHelpBrowser
        html = "Score of this fixed backbone sequence design using starting"
        html = html + " structure " + self.sim_input_file
        html = html + " and residue file " + self.resFile
        html = html + " is " + "<font face=Courier New color=red>" + score + "</font>"
        html = html + "<p>The original protein sequence and the designed sequence"
        html = html + " are shown below with differences in designed sequence "
        html = html + "shown in red: <br>"
        modSeqList, similarity = highlightDifferencesInSequence(proteinSeqList)
        for i in range(len(proteinSeqList)):
            html = html + "<font face=Courier New>" + proteinSeqList[i][0] + "</font> "+ "<br>"
            html = html + "<font face=Courier New>" + modSeqList[i] + "</font>" + "<br>"
        html = html + "</p>"
        html = html + "<p>Sequence Similarity = " + similarity + "</p>"
        w = WikiHelpBrowser(html, parent = self.win, caption = "Rosetta Results")
        w.show()
        return
    
    def checkErrorInStdOut(self, rosettaStdOut):
    
        f = open(rosettaStdOut, 'r')
        doc = f.read()
        if doc.find("ERROR") == -1:
            return 0
        else: 
            return 1
        
    def set_waitcursor(self, on_or_off): 
        """
        For on_or_off True, set the main window waitcursor.
        For on_or_off False, revert to the prior cursor.
        
        """
        if on_or_off:
            QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        else:
            QApplication.restoreOverrideCursor() # Restore the cursor

        return
    
    
    
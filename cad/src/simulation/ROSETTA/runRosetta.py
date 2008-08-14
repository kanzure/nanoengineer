"""
runRosetta.py -- setting up and running rosetta simulations

@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

History:
Urmi copied this file from runSim.py and then modified it.
This file is very different from runSim.py, partly because rosetta simulation
is quite different from gromacs simulation
"""
from files.pdb.files_pdb import writepdb
from files.pdb.files_pdb import insertpdb
from model.chunk import Chunk
from utilities.debug import print_compact_traceback
from platform_dependent.PlatformDependent import find_or_make_Nanorex_subdir
import os, sys, time, string
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
from utilities.prefs_constants import rosetta_enabled_prefs_key, rosetta_path_prefs_key
from utilities.prefs_constants import rosetta_database_enabled_prefs_key, rosetta_dbdir_prefs_key
from protein.model.Protein import write_rosetta_resfile
from foundation.wiki_help import WikiHelpBrowser

#global counter so that repeat run of rosetta can produce uniquely named
#output file.
count = 1
#same with backrub
count_backrub = 1

def showRosettaScore(tmp_file_prefix, scorefile, win):
    """
    Show the rosetta score of the current protein sequence
    
    @param tmp_file_prefix: file prefix from which directory of the score file 
                            could be extracted
    @type tmp_file_prefix: str
    
    @param scorefile: name of the rosetta score file
    @type scorefile: str
    
    @param win: NE-1 window
    @type win: L{gl_pane}
    
    """
    dir1 = os.path.dirname(tmp_file_prefix)
    scorefile = scorefile + '.sc'
    scoreFilePath = os.path.join(dir1, scorefile)   
    fileObject1 = open(scoreFilePath, 'r')
    if fileObject1:
        doc = fileObject1.readlines()
        copied_lines = []
        for line in doc:
            #put a comma after each word
            i = 0
            firstSpace = True
            for c in line: 
                if i > 0 and c == ' ' and firstSpace == True:
                    line = line[0:i] + ',' + line[i+1:]
                    firstSpace = False
                if c != ' ' and firstSpace == False:
                    firstSpace = True
                i = i + 1    
                if i == len(line):
                    copied_lines.append(line)
        
        array_Name = copied_lines[0].split(',')
        array_Score = copied_lines[1].split(',')
        i = 0 
        for i in range(len(array_Name)):
            array_Name[i] = array_Name[i].strip()
            array_Score[i] = array_Score[i].strip()
        i = 0 
        html = ""
        for i in range(len(array_Name)):
            html = html + "<p><b>" + array_Name[i].upper() + "</b> = "
            html = html + "<font color = red> " + array_Score[i] + "</font></p>"
        w = WikiHelpBrowser(html, parent = win, caption = "Rosetta Scoring Results", size = 1)
        w.show()    
    return

def createUniquePDBOutput(tmp_file_prefix, proteinName, win):
    """
    Create a uniquely named output file for rosetta backrub motion simulation
    
    @param tmp_file_prefix: file prefix from which directory of the pdb file to 
                            be saved could be extracted
    @type tmp_file_prefix: str
    
    @param proteinName: name of the input protein
    @type proteinName: str
    
    @param win: NE-1 window
    @type win: L{gl_pane}
    
    @return: output protein name and  output pdb file path
    """
    pdbFile = 'backrub_low.pdb' 
    dir1 = os.path.dirname(tmp_file_prefix)
    pdbFilePath = os.path.join(dir1, pdbFile)   
    fileObject1 = open(pdbFilePath, 'r')
    outFile = proteinName + '_' + pdbFile
    #make sure that this outfile does not already exists, 
    #if it exists, then we should assign the out protein a unique name such that
    # its easy to browse through the set of available proteins in the model tree
    for mol in win.assy.molecules:
        #if an output protein chunk with the same name exists, we need to 
        #rename the output protein
        tempPdb = outFile[0:len(outFile)-4].lower() + ' '
        if mol.isProteinChunk() and tempPdb == mol.name:
            global count_backrub 
            outFile = tempPdb + '_' + str(count_backrub) + '.pdb'
            count_backrub = count_backrub + 1
            print "using global count backrub", count_backrub
    
    outputPdbFilePath = os.path.join(dir1, outFile) 
    if fileObject1:
        fileObject2 = open(outputPdbFilePath, 'w+')  
    else:
        return None
    doc = fileObject1.readlines()
    fileObject2.writelines(doc)
    fileObject1.close()
    fileObject2.close()
    
    outProteinName = outFile[0:len(outFile)-4]
    return outProteinName, outputPdbFilePath

def getScoreFromBackrubOutFile(outputPdbFilePath):
    """
    Get score from backrub_low.pdb for the current protein sequence deisgn with
    backrub motion
    
    @param outputPdbFilePath: path location of the output pdb file in the disk
    @type outputPdbFilePath: str
    
    @return: a string 
    """
    #a separate function for this is needed since we have only one pdb file 
    #with backrub that is backrub_low and hence the score is much more easily
    #obtainable from the header
    fileObject1 = open(outputPdbFilePath, 'r')
    if fileObject1:     
        doc = fileObject1.readlines()
    else:
        return None
    for line in doc:
        #first instance of score
        valFind = line.find("SCORE")
        if valFind!=-1:
            #process this line to read the total score
            words = line[16:]
            score = words.strip()
            pdbFile = os.path.basename(outputPdbFilePath)
            print "For output pdb file " + pdbFile + ", score = ", score
            fileObject1.close()
            return score
    return None

def getProteinNameAndSeq(inProtein, outProtein, win):
    """
    Get the protein name for inProtein and outProtein chunk and the corresponding
    sequence to be displayed in the popup result dialog
    
    @param inProtein: input protein chunk
    @type inProtein: L{Chunk}
    
    @param outProtein:  output protein chunk
    @type outProtein: L{Chunk}
    
    @param  win: NE-1 window
    @type win: L{gl_pane}
    
    @return: a list of two tuples [(inProtein Name, sequence), (outProtein Name, sequence)]
    """
    proteinSeqTupleList = []
    seqList1 = ""
    seqList2 = ""
    #no idea what insert pdb does to put a space at the end of the chunk name!
    outProtein = outProtein.lower() + ' '
    for mol in win.assy.molecules:
        if mol.isProteinChunk() and inProtein == mol.name:
            seqList1 = mol.protein.get_sequence_string()
            tupleEntry1 =  (inProtein, seqList1) 
        if mol.isProteinChunk() and outProtein == mol.name:
            seqList2 = mol.protein.get_sequence_string()
            tupleEntry2 =  (outProtein, seqList2)
    proteinSeqTupleList = [tupleEntry1, tupleEntry2]   
    if seqList1 is "":
        return []
    return proteinSeqTupleList
    
def getScoreFromOutputFile(tmp_file_prefix, outfile, numSim):
    """
    Extract the best score from the output file
    
    @param tmp_file_prefix: directory path for the pdb files
    @type tmp_file_prefix: str
    
    @param outfile: Name of the outfile file (pdb file)
    @type outfile: str
    
    @param numSim: number of simulation
    @type numSim: int
    
    @return: best score from the pdb file, name of the pdb file with the best
             score
    """
    scoreList = []
    for i in range(numSim):
        if len(str(i+1)) == 1:
            extension = '000' + str(i+1)
        elif  len(str(i+1)) == 2:
            extension = '00' + str(i+1)
        elif  len(str(i+1)) == 3:
            extension = '0' + str(i+1)   
        else:
            #Urmi 20080716: what to do beyond 4 digits?
            extension = str(i+1)
        pdbFile = outfile + '_' + extension + '.pdb' 
        dir = os.path.dirname(tmp_file_prefix)
        pdbFilePath = os.path.join(dir, pdbFile)    
            
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
                    print "For output pdb file " + pdbFile + ", score = ", score
                    score1 = float(score) 
                    f.close()
                    scoreList.append(score1)
                    break
        else:
            print "Output Pdb file cannot be read to obtain score"
            f.close()
            return None, None
        
    sortedList = sorted(scoreList)    
    minScore = sortedList[0]
    index = scoreList.index(minScore)
    if len(str(index + 1)) == 1:
            extension = '000' + str(index + 1)
    elif  len(str(index)) == 2:
        extension = '00' + str(index + 1)
    elif  len(str(index + 1)) == 3:
        extension = '0' + str(index + 1)   
    else:
        #Urmi 20080716: what to do beyond 4 digits?
        extension = str(index + 1)
    pdbFile = outfile + '_' + extension + '.pdb' 
    return str(minScore), pdbFile
    

def processFastaFile(fastaFilePath, bestSimOutFileName, inputProtein):
    """
    Process fasta file to extract output protein sequence
    
    @param fastaFilePath: path of the fasta file containing all the protein pdb 
                          ids and their corresponding sequences
    @type fastaFilePath: str
    
    @param bestSimOutFileName: pdb id with the lowest score
    @type bestSimoutFileName: str
    
    @param inputProtein: pdb id of the protein, input to the Rosetta simulation
    @type inputProtein: str
    
    @return: a list of (protein name, protein sequence) tuples
    """
    
    proteinSeqTupleList = []
    f = open(fastaFilePath, 'r')
    desiredOutProtein = bestSimOutFileName[0:len(bestSimOutFileName)-4]
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
            #fasta files do that for better readability
            i = i + 1
            #but you can reach EOF while doing increments within a loop
            #hence you need to write the last protein (name, sequence) tuple
            #before you exit the loop
            if i >= len(doc):
                if proteinName == desiredOutProtein or proteinName == inputProtein:
                    tupleEntry = (proteinName, proteinSeq)
                    proteinSeqTupleList.append(tupleEntry)
                break

            line3 = doc[i]
            while 1:
                if line3.find(">")!= -1:
                    #indicates begining of new protein sequence
                    line1 = line3
                    if proteinName == desiredOutProtein or proteinName == inputProtein:
                        tupleEntry = (proteinName, proteinSeq)
                        proteinSeqTupleList.append(tupleEntry)
                    break
                
                #part of the old sequence, since the sequence spans over multiple lines
                proteinSeq = proteinSeq + line3[0:len(line3)-1]
                i = i + 1
                #writing the last sequence, see comment for similar situation above
                if i >= len(doc):
                    if proteinName == desiredOutProtein or proteinName == inputProtein:
                        tupleEntry = (proteinName, proteinSeq)
                        proteinSeqTupleList.append(tupleEntry)
                    break
                line3 = doc[i]
    else:
        print "File cannot be read"
    f.close()
    return proteinSeqTupleList

def highlightDifferencesInSequence(proteinSeqList):
    """
    Highlight the differences between input rosetta protein sequence and output
    rosetta protein sequence with the lowest score.
    
    @param proteinSeqList: List of size 2 containing input protein and output
                           protein pdb ids and their corresponding sequences
                           in a tuple
    @type proteinSeqList: list
    
    @return: a list of amino acids, some of which have been colored red, to 
             indicate that they are different from that of the input protein,
             percentage sequence similarity 
    """
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
        Constructor for Rosetta Runner
        set up external relations from the part we'll operate on;
        
        @param part: NE-1 part
        @type part: L{Part}
    
        @param mflag: Movie flag
        @type mflag: int
        @note: mflag is not used at all since we are running only one type of 
               simulation for now
    
        @param simaspect: simulation aspect
        @type simaspect: 
    
        @param cmdname: name of the command
        @type cmdname: str
    
        @param cmd_type: name of type of command
        @type cmd_type: str
        
        @param useRosetta: whether we should use rosetta or not
        @type useRosetta: bool
        @note: Since we are using only Rosetta to run protein simlations, this 
               is unnecessary for now. May be we will use it some day when we 
               are using multiple simulators
               
        @param background: dictates whether a rosetta simulation should run in
                           the background or not
        @type useRosetta: bool
        @note: Rosetta is running in the foreground only for now.       
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
    
    def sim_input_filename(self, args):
        """    
        write the pdb for the part that is in the NE-1 window now and set the 
        filename to that pdb
        
        @param part: NE-1 part
        @type part: L{Part}
    
        @param args: name of the protein for which simulation should be run
        @type args: str
        
        @return: name of the pdb file which is going to be the starting structure 
                 for the current rosetta simulation
        """
        # if we run rosetta from within build protein mode, then we can run
        # rosetta for the current protein which is args
        #if we are outside this mode, we can run rosetta for a selected protein
        #chunk, if there's one
        if args != "":
            pdbId = args
            for mol in self.win.assy.molecules:
                if mol.name == args:
                    chunk = mol
                    break     
        else:    
            #run it for the first available protein in chunklist
            pdbId, chunk = self.getPDBIDFromChunk()
            if pdbId is None:
                return None
        #input filename
        fileName = pdbId + '.pdb'
        dir = os.path.dirname(self.tmp_file_prefix)
        fileLocation = os.path.join(dir, fileName)
        #since the starting structure could be in arbitrary location in users
        #hard disk, we write a pdb file for the imported/inserted/fetched protein
        #chunk in RosettaDesignFiles directory under Nanorex
        writepdb(self.part, str(fileLocation), singleChunk = chunk) 
        return fileName
    
    def getPDBIDFromChunk(self):
        """
        Get the first available protein chunk from NE-1 part
        
        @return: pdb id of the first protein chunk and the chunk as well
        """
        for chunk in self.win.assy.molecules:
            if chunk.isProteinChunk():
                return chunk.name, chunk
        return None, None    
    
    
    def removeOldOutputPDBFiles(self):
        """
        remove all the old output files for rosetta simulatiosn run on the same
        starting structure before running a new rosetta simulation
        
        @note: bug in rosetta: a new simulation refuses to run if there's 
               pdbid_0001.pdb or any other parameters you have have provided with
               -pdbout in rosetta simulation. We think that pdbid_0001.pdb is 
               created first as the main output file at the end of the simulation
               and then its copied to parameter with -pdbout. Hence we need to 
               remove all output files related to starting structure pdbid.pdb
               before running a new simulation.
        """
        dir = os.path.dirname(self.tmp_file_prefix)
        infile = self.sim_input_file
        #remove all output files previously created for this pdb
        #In this regular expression match, the first * is for any pdbout name, 
        #we generate based on the input name and the second * is for 
        #all the numbers of output pdb files that are generated based on the
        #number of simulations        
        outpath = infile[0:len(infile) - 4] + '*' + '_' + '*' + '.pdb'
        from fnmatch import fnmatch
        for file in os.listdir(dir):
            fullname = os.path.join( dir, file)
            if os.path.isfile(fullname):
                if fnmatch( file, outpath):
                    os.remove(fullname)
        return
    
    def setupArgsFromPopUpDialog(self, args):
        """
        Besides the default set of arguments there are many command line options
        that the user can specify. This parses the user input and generates a list
        of those options
        
        @param args: a string of various command line options
                                    for running rosetta separated by space(s)
        @type args: str  
        """
        argStringListFromPopUpDialog = []
        #argument 0 is for number of simulations, already handled
        #Index of each argument known ahead of time
             
        if args != "": 
            #break the string into individual words and make a list and extend 
            # the argument list
            tempString = args.replace('\n', ' ')
            extraArgs = tempString.split(" ")
            #strip extra space around each of these options
            extraArgs1 = []
            for i in range(len(extraArgs)):
                word = extraArgs[i].strip()
                if word != '':
                    extraArgs1.append(word)
            argStringListFromPopUpDialog.extend(extraArgs1)
            
        return argStringListFromPopUpDialog
    
    def setup_sim_args(self, argsFromPopUpDialog, backrubArgs = []):
        """
        Set up arguments for the simulator,
        by constructing a command line for the standalone executable simulator,
        
        @param argsFromPopUpDialog: a string of various command line options
                                    for running rosetta separated by space(s)
        @type argsFromPopUpDialog: str                            
        """
        argListFromPopUpDialog = self.setupArgsFromPopUpDialog(argsFromPopUpDialog)
        use_command_line = True
        movie = self._movie # old-code compat kluge
        self.totalFramesRequested = movie.totalFramesRequested
        self.update_cond = movie.update_cond
        program = self.program
        path = self.path
        infile = self.sim_input_file
        self.outfile = infile[0:len(infile) - 4] + '_out'
        self.scorefile = infile[0:len(infile) - 4] + '_score'
        #if any of the protein chunks in NE-1 part matches the outfile name,
        #rename the outfile
        #this is necessary, otherwise two chunks with the same name will be
        #created in the model tree and its not easy to figure out in the build
        #protein mode which rosetta run generated it
        tempPdb = infile[0:len(infile) - 5] + '([A-Z]|[a-z])' + '_out' + '_' + '[0-9][0-9][0-9][0-9]' + '([A-Z]|[a-z])'
        
        for mol in self.win.assy.molecules:
            #if an output protein chunk with the same name exists, we need to 
            #rename the output protein
            if mol.isProteinChunk() and re.match(tempPdb, mol.name) is not None:
                global count 
                self.outfile = infile[0:len(infile) - 4] + '_' + str(count) + '_out'
                count = count + 1
        #bug in rosetta: simulation does not work in  pdbID_0001.pdb exists in 
        #this directory, hence always remove it
        self.removeOldOutputPDBFiles()
        args = []
        if use_command_line:
            #Urmi 20080709 Support for fixed backbone sequence design for now
            if self.cmd_type == "ROSETTA_FIXED_BACKBONE_SEQUENCE_DESIGN":
                args = [
                    '-paths',  str(self.path),
                    '-design',
                    '-fixbb',
                    '-profile',
                    '-ndruns', str(self.numSim),
                    '-resfile', str(self.resFile),
                    '-pdbout', str(self.outfile),
                    '-s', infile]
                args.extend(argListFromPopUpDialog)
            elif self.cmd_type == "BACKRUB_PROTEIN_SEQUENCE_DESIGN":
                args = [
                    '-paths',  str(self.path),
                    '-ntrials', str(self.numSim),
                    '-pose1',
                    '-backrub_mc',
                    '-resfile', str(self.resFile),
                    '-s', infile]
                args.extend(argListFromPopUpDialog)
                args.extend(backrubArgs)
                
            elif self.cmd_type == "ROSETTA_SCORE":
                args =[
                    '-paths',  str(self.path),
                    '-scorefile', str(self.scorefile),
                    '-score',
                    '-s', infile]
            else:
                args = []
            self._arguments = args
        return # from setup_sim_args    
    
    def set_options_errQ(self, args):  
        """
        Figure out and set filenames, including sim executable path.
        All inputs and outputs are self attrs or globals or other obj attrs...
        except, return error code if sim executable missing
        or on other errors detected by subrs.
        
        @param args: name of the protein for which rosetta simulation is run and 
                     if its empty then it is run for the first available chunk
        @type args: str
        """
        movie = self._movie
        simFilesPath = find_or_make_Nanorex_subdir('RosettaDesignFiles')

        # Create temporary part-specific filename, for example:
        # "partname-minimize-pid1000".
        # We'll be appending various extensions to tmp_file_prefix to make temp
        # file names for sim input and output files as needed 
        if args != "":
            pdbId = args
            for mol in self.win.assy.molecules:
                if mol.name == args:
                    chunk = mol
                    break
        else:    
            pdbId, chunk = self.getPDBIDFromChunk()
            
        if self.cmd_type == "BACKRUB_PROTEIN_SEQUENCE_DESIGN":
            backrubSetupCorrect = chunk.protein.is_backrub_setup_correctly()
            #Urmi 20080807: The backrub motion is so poorly documented that
            #I do not have any idea what is the threshold value
            #my experiments with 2gb1 seems to show that its 3, but I dont know for sure
            if not backrubSetupCorrect:
                msg = redmsg("Rosetta sequence design with backrub motion failed. Please edit your residues properly from Edit REsidues command.")
                env.history.message(self.cmdname + "," + self.cmd_type + ": " + msg)
                return -1
        #write the residue file
        resFile = pdbId + ".resfile"
        resFilePath = os.path.join(simFilesPath, resFile)
        success = write_rosetta_resfile(resFilePath, chunk)
        if success:
            self.resFile = resFile
        else:
            #Shall we refuse to run the program if we cannot write the residue file?
            print "Residue file could not be written"
            return -1
        #remove all previously existing fasta files
        #may not be needed. But we are doing with out pdb, might as well do it 
        #fasta and design files as well
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
            #We are not running Rosetta in the background now, so may not be useful
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
    
    def getPathLocation(self, dataBasePath, simFilesPath):
        """
        Write the paths.txt file required for a rosetta simulation
        
        @param dataBasePath: path for rosetta databae
        @type dataBasePath: str
        
        @param simFilesPath: path for rosetta executable
        @type simFilesPath: str
        
        @see: rosetta documentation on explanation of the paths.txt file
        @return: paths.txt file path
        """
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
        
        # input files will always be in this directory
        tempWord = "pdb1"
        word[0] = "%-32s" % tempWord
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
        """
        Get the path of the rosetta executable from the preferences dialog
        
        @return: path for the rosetta executable
        """
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
        """
        Get the path of the rosetta database from the preferences dialog
        
        @return: path for the rosetta database
        """
        plugin_name = "ROSETTA_DATABASE"
        #Urmi 20080710: using the same code as exectuables. Its kind of bad
        # but probably ok before RosettaCon
        plugin_prefs_keys = (rosetta_database_enabled_prefs_key, rosetta_dbdir_prefs_key)     
        errorcode, errortext_or_path = \
                 checkPluginPreferences(plugin_name, plugin_prefs_keys)
        if errorcode:
            msg = redmsg("Verify Plugin: %s (code %d)" % (errortext_or_path, errorcode))
            env.history.message(msg)
            return None
        dataBase_path = errortext_or_path
        return dataBase_path
    
    def run_rosetta(self, movie, args):
        """
        Main method that executes the rosetta simulation
        
        @param movie: simulation object
        @type movie: L{Movie}
        
        @param args: list of simulation arguments
        @type args: list
        
        @note: This method needs to be refactored very badly
        """
        self._movie = movie 
        assert args >= 1
        #we have set it up such that the first element in arg[0] is number of simulations
        self.numSim = args[0][0]
        #set the program path, database path and write the paths.txt in here
        #we have set it up such that the third argument in args[0] always have
        # the name of the protein we are running rosetta simulation for
        #also we say that an error has occurred if we cannot write the resfile.
        #not sure if this should be the case
        self.errcode = self.set_options_errQ( args[0][2])
        if self.errcode: # used to be a local var 'r'
            return
        #get the starting pdb structure for rosetta simulation 
        self.sim_input_file = self.sim_input_filename(args[0][2])
        if self.sim_input_file is None:
            return
        #this marks the beginning of the simulation. Although technically we are yet
        # to call QProcess, it seems like a good place to set the waitcursor to True
        self.set_waitcursor(True)
        progressBar = self.win.statusBar().progressBar
        # Disable some QActions (menu items/toolbar buttons) while the sim is running.
        self.win.disable_QActions_for_sim(True)

        try: 
            self.simProcess = None 
            #sets up the argument list for running rosetta including the ones
            #that were provided in the pop up dialog
            backRubArgs = []
            if len(args) == 3:
                backRubArgs = args[2]
            self.setup_sim_args(args[0][1], backRubArgs)
            progressBar.setRange(0, 0)
            progressBar.reset()
            progressBar.show()
            env.history.statusbar_msg("Running Rosetta on " + self.sim_input_file[0:len(self.sim_input_file) - 4])
            #this is used to name all the files related to this simulation
            #we make sure that the pdb id is there in the filename so that it is
            #easy to identify for which protein chunk we are running the simulation
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
            #rosetta files are all put in RosettaDesignFiles under Nanorex
            rosettaProcess.setWorkingDirectory(rosettaWorkingDir)
            environmentVariables = rosettaProcess.environment()
            rosettaProcess.setEnvironment(environmentVariables)
            msg = greenmsg("Starting Rosetta sequence design")
            env.history.message(self.cmdname + ": " + msg)
            env.history.message("%s: Rosetta files at %s%s%s.*" %
                (self.cmdname, rosettaWorkingDir, os.sep,
                 rosettaFullBaseFileInfo.completeBaseName()))
            
            abortHandler = AbortHandler(self.win.statusBar(), "rosetta")
            #main rosetta simulation call
            errorCode = rosettaProcess.run(self.program, self._arguments, False, abortHandler)
            abortHandler = None
            if (errorCode != 0):
                if errorCode == -2: # User pressed Abort button in progress dialog.
                    msg = redmsg("Aborted.")
                    env.history.message(self.cmdname + ": " + msg)
                    env.history.statusbar_msg("")
                    if self.simProcess: 
                        self.simProcess.kill()
                else: 
                    #the stdout will tell the user for what other reason,
                    #the simulation may fail
                    msg = redmsg("Rosetta sequence design failed. For details check" + rosettaStdOut)
                    env.history.message(self.cmdname + ": " + msg)
                    self.errcode = 2;
                    env.history.statusbar_msg("")
            else:
                #Error code is not zero but there's in reality error in stdout
                #check if that be the case 
                env.history.statusbar_msg("")
                errorInStdOut = self.checkErrorInStdOut(rosettaStdOut)
                if errorInStdOut:
                    msg = redmsg("Rosetta sequence design failed, Rosetta returned %d" % errorCode)
                    env.history.message(self.cmdname + "," + self.cmd_type + ": " + msg)
                    env.history.statusbar_msg("")
                else:    
                    #bug in rosetta: often for some reason or the other rosetta
                    #run does not produce an o/p file. One instance is that if
                    # you already have an output file for this starting structure
                    #already in the directory rosetta refuses to optimize the 
                    #structue again even if your residue file has changed
                    #since we remove all related output files before any run on
                    #the same protein, this is not a possible source of error
                    #in our case but there can be other similar problems
                    #Hence we always check the desired output file actually exists 
                    #in the RosettaDesignFiles directory before we actually declare
                    #that it has been a successful run
                    if self.cmd_type == "ROSETTA_FIXED_BACKBONE_SEQUENCE_DESIGN":
                        outputFile = self.outfile + '_0001.pdb'
                        outPath = os.path.join(os.path.dirname(self.tmp_file_prefix), outputFile)
                        if os.path.exists(outPath): 
                            #if there's the o/p pdb file, then rosetta design "really"
                            #succeeded
                            msg = greenmsg("Rosetta sequence design succeeded")
                            env.history.message(self.cmdname + "> " + self.cmd_type + ": " + msg)
                            #find out best score from all the generated outputs
                            #may be we will do it some day, but for now we only output
                            #the chunk with the lowest energy (Score)
                            score, bestSimOutFileName = getScoreFromOutputFile(self.tmp_file_prefix, self.outfile, self.numSim)
                            chosenOutPath = os.path.join(os.path.dirname(self.tmp_file_prefix), bestSimOutFileName)
                            insertpdb(self.assy, str(chosenOutPath), None)
                            #set the secondary structure of the rosetta output protein
                            #to that of the inpput protein
                            outProtein = self._set_secondary_structure_of_rosetta_output_protein(bestSimOutFileName)
                            #update the protein combo box in build protein mode with
                            #newly created protein chunk
                            self._updateProteinComboBoxInBuildProteinMode(outProtein)
                            env.history.statusbar_msg("")
                            fastaFile = self.outfile + "_design.fasta" 
                            fastaFilePath = os.path.join(os.path.dirname(self.tmp_file_prefix), fastaFile)
                            #process th fasta file to find the sequence of the protein
                            #with lowest score
                            proteinSeqList = processFastaFile(fastaFilePath, bestSimOutFileName, self.sim_input_file[0:len(self.sim_input_file)-4])
                            #show a pop up dialog to show the best score and most
                            #optimized sequence
                            if score is not None and proteinSeqList is not []:
                                self.showResults(score, proteinSeqList)
                        else:
                            #even when there's nothing in stderr or errocode is zero,
                            #rosetta may not output anything. 
                            msg1 = redmsg("Rosetta sequence design failed. ")
                            msg2 = redmsg(" %s file was never created by Rosetta." % outputFile)
                            msg = msg1 + msg2
                            env.history.message(self.cmdname + ": " + msg)
                            env.history.statusbar_msg("")
                            
                    if self.cmd_type == "BACKRUB_PROTEIN_SEQUENCE_DESIGN":
                        #its important to set thi pref key to False so that if the
                        #subsequent rosetta run is with fixed backbone then the 
                        #resfile is correctly written
                        from utilities.prefs_constants import rosetta_backrub_enabled_prefs_key    
                        env.prefs[rosetta_backrub_enabled_prefs_key] = False  
                        #Urmi 20080807: first copy the backrub_low.pdb to a new pdb
                        #file with the pdb info also added there
                        outProteinName, outPath = createUniquePDBOutput(self.tmp_file_prefix, self.sim_input_file[0:len(self.sim_input_file)-4], self.win)
                        if outProteinName is None:
                            msg1 = redmsg("Rosetta sequence design with backrub motion has failed. ")
                            msg2 = redmsg(" backrub_low.pdb was never created by Rosetta.")
                            msg = msg1 + msg2
                            env.history.message(self.cmdname + "," + self.cmd_type + ": " + msg)
                            env.history.statusbar_msg("")
                        else:
                            env.history.statusbar_msg("")
                            msg = greenmsg("Rosetta sequence design with backrub motion allowed, succeeded")
                            env.history.message(self.cmdname + "> " + self.cmd_type + ": " + msg)
                            insertpdb(self.assy, str(outPath), None)
                            outProtein = self._set_secondary_structure_of_rosetta_output_protein(outProteinName + ".pdb")
                            self._updateProteinComboBoxInBuildProteinMode(outProtein)  
                            inProteinName = self.sim_input_file[0:len(self.sim_input_file)-4]
                            proteinSeqList = getProteinNameAndSeq(inProteinName, outProteinName, self.win)
                            score = getScoreFromBackrubOutFile(outPath)
                            if score is not None and proteinSeqList is not []:
                                self.showResults(score, proteinSeqList)

                    if self.cmd_type == "ROSETTA_SCORE":
                        msg = greenmsg("Rosetta scoring has succeeded")
                        env.history.message(self.cmdname + "> " + self.cmd_type + ": " + msg)
                        showRosettaScore(self.tmp_file_prefix, self.scorefile, self.win)
        except:
            print_compact_traceback("bug in simulator-calling code: ")
            self.errcode = -11111
        self.set_waitcursor(False)
        self.win.disable_QActions_for_sim(False)
        env.history.statusbar_msg("")
        if not self.errcode:
            return # success
        return # caller should look at self.errcode
    
    def _updateProteinComboBoxInBuildProteinMode(self, outProtein):
        """
        update protein combo box in build protein mode with the newly generated
        output protein
        
        @param outProtein: rosetta outputted protein chunk
        @type outProtein: L{Chunk}
        """
        
        from utilities.GlobalPreferences import MODEL_AND_SIMULATE_PROTEINS
        if MODEL_AND_SIMULATE_PROTEINS:
            command = self.win.commandSequencer.find_innermost_command_named('MODEL_AND_SIMULATE_PROTEIN')
        else:    
            command = self.win.commandSequencer.find_innermost_command_named('BUILD_PROTEIN')
        if command:
            command.propMgr.structureComboBox.addItem(outProtein.name)
            command.propMgr.protein_name_list.append(outProtein.name)
            command.propMgr.protein_chunk_list.append(outProtein)
        
        return
    
    
    def _set_secondary_structure_of_rosetta_output_protein(self, bestSimOutFileName):
        """
        Set the secondary struture of the rosetta protein to that of the input
        protein
        
        @param bestSimOutFileName: output pdb id with lowest energy score
        @type bestSimOutFileName: str
        
        @return: output protein chunk with its secondary structure set
        
        @note: rosetta fixed bb sequence design does not do anything to the secondary
               structure of the output protein. As it remains constant, we simply
               copy it from the input protein
        """
        #since this method is called only if a simulation be successful,
        #input and output protein are both bound to be there and hence there's
        #no else block
        matchForFixedBB = bestSimOutFileName[0:len(bestSimOutFileName)-4].lower() + 'A'
        matchForBackRub = bestSimOutFileName[0:len(bestSimOutFileName)-4].lower() + ' '
        outMatch = ""
        if self.cmd_type == "ROSETTA_FIXED_BACKBONE_SEQUENCE_DESIGN":
            outMatch = matchForFixedBB
        if self.cmd_type == "BACKRUB_PROTEIN_SEQUENCE_DESIGN":
            outMatch = matchForBackRub
        outProtein = None
        for mol in self.win.assy.molecules:
            if mol.isProteinChunk() and mol.name == self.sim_input_file[0:len(self.sim_input_file)-4]:
                inProtein = mol
            if mol.isProteinChunk() and mol.name == outMatch:
                outProtein = mol
        if outProtein:        
            outProtein.protein.set_rosetta_protein_secondary_structure(inProtein)
        return outProtein
    
    def showResults(self, score, proteinSeqList):
        """
        Display the rosetta simulation results in a pop up dialog at the end
        of a successful simulation
        
        @param score: Score from the most optimized sequence
        @type score: str
        
        @param proteinSeqList: list of size 2, with (protein, sequence) tuple, 
                                containing the input protein and its sequence
                                and the output protein and its corresponding
                                sequence
        @type proteinSeqList: list
        """
        html = "Score of this fixed backbone sequence design using starting"
        html = html + " structure " + self.sim_input_file
        html = html + " and residue file " + self.resFile
        html = html + " is " + "<font face=Courier New color=red>" + score + "</font>"
        html = html + "<p>The original protein sequence and the designed sequence"
        html = html + " are shown below with differences in designed sequence "
        html = html + "shown in red: <br>"
        #highlight the differences in sequence between the original protein
        #and the new protein
        modSeqList, similarity = highlightDifferencesInSequence(proteinSeqList)
        for i in range(len(proteinSeqList)):
            html = html + "<font face=Courier New>" + proteinSeqList[i][0] + "</font> "+ "<br>"
            html = html + "<font face=Courier New>" + modSeqList[i] + "</font>" + "<br>"
        html = html + "</p>"
        html = html + "<p>Sequence Similarity = " + similarity + "</p>"
        w = WikiHelpBrowser(html, parent = self.win, caption = "Rosetta Sequence Design Results", size = 2)
        w.show()
        return
    
    def checkErrorInStdOut(self, rosettaStdOut):
        """
        check for error in Rosetta outputted pdb file
        
        @param rosettaStdOut: rosetta outputted pdb file
        @type rosettaStdOut: str
        
        @return: 1 if there's an error and if not, then 0
        """
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
    
    
    

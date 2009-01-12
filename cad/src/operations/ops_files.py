# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
ops_files.py - provides fileSlotsMixin for MWsemantics,
with file slot methods and related helper methods.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

Note: most other ops_*.py files provide mixin classes for Part,
not for MWsemantics like this one.

History:

bruce 050907 split this out of MWsemantics.py.
[But it still needs major cleanup and generalization.]

mark 060730 removed unsupported slot method fileNew();
refined and added missing docstrings
"""

import re
import sys
import os
import shutil
import time

from PyQt4.Qt import Qt
from PyQt4.Qt import QFileDialog, QMessageBox, QString, QSettings
from PyQt4.Qt import QApplication
from PyQt4.Qt import QCursor
from PyQt4.Qt import QProcess
from PyQt4.Qt import QStringList

import foundation.env as env
from utilities import debug_flags

from platform_dependent.PlatformDependent import find_or_make_Nanorex_subdir

from model.assembly import Assembly
from model.chem import move_atoms_and_normalize_bondpoints

from simulation.runSim import readGromacsCoordinates

from files.pdb.files_pdb import insertpdb, writepdb
from files.pdb.files_pdb import EXCLUDE_BONDPOINTS, EXCLUDE_HIDDEN_ATOMS
from files.mmp.files_mmp import readmmp, insertmmp, fix_assy_and_glpane_views_after_readmmp
from files.amber_in.files_in import insertin
from files.ios.files_ios import exportToIOSFormat,importFromIOSFile

from graphics.rendering.povray.writepovfile import writepovfile
from graphics.rendering.mdl.writemdlfile import writemdlfile
from graphics.rendering.qutemol.qutemol import write_qutemol_pdb_file


from utilities.debug import print_compact_traceback
from utilities.debug import linenum
from utilities.debug import begin_timing, end_timing

from utilities.Log import greenmsg, redmsg, orangemsg, _graymsg

from utilities.prefs_constants import getDefaultWorkingDirectory
from utilities.prefs_constants import workingDirectory_prefs_key
from utilities.prefs_constants import toolbar_state_prefs_key

from utilities.debug_prefs import Choice_boolean_False
from utilities.debug_prefs import debug_pref

from utilities.constants import SUCCESS, ABORTED, READ_ERROR
from utilities.constants import str_or_unicode

from ne1_ui.FetchPDBDialog import FetchPDBDialog
from PyQt4.Qt import SIGNAL
from urllib import urlopen

debug_babel = False   # DO NOT COMMIT with True

def set_waitcursor(on_or_off):
    """
    For on_or_off True, set the main window waitcursor.
    For on_or_off False, revert to the prior cursor.
    [It might be necessary to always call it in matched pairs,
     I don't know [bruce 050401].]
    """
    if on_or_off:
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
    else:
        QApplication.restoreOverrideCursor() # Restore the cursor
    return

debug_part_files = False #&&& Debug prints to history. Change to False after QA. [Mark 060703]

def _fileparse(name):
    """
    DEPRECATED; in new code use filesplit (not compatible) instead.
    
    Breaks name into directory, main name, and extension in a tuple.

    Example:
    _fileparse('~/foo/bar/gorp.xam') ==> ('~/foo/bar/', 'gorp', '.xam')
    """
    # bruce 050413 comment: deprecated in favor of filesplit
    # wware 060811: clean things up using os.path functions
    #   [REVIEW: did that change behavior in edge cases like "/"?
    #    bruce 071030 question]
    # bruce 071030: renamed to make it private.
    dir, x = os.path.split(name)
    if not dir:
        dir = '.'
    fil, ext = os.path.splitext(x)
    return dir + os.path.sep, fil, ext

def _convertFiletypesForMacFileDialog(filetypes):
    """
    Returns a QString file type list that includes "- suffix" 
    in the name of each file type so that the extension (suffix)
    will appear in the file dialog file type menu.
    
    @note: Mac only.
    @see: QFileDialog
    """
    
    if sys.platform != "darwin":
        return filetypes
    
    def munge_ext(filetype):
        """
        Return filetype with "- suffix " just before "(*.ext")
        """
        
        if filetype.find("(*.*)") != -1: 
            return filetype # Was found.
     
        # rsplit based on the last open paren
        _tmpstr = filetype.rsplit("(",1)
        # save the front part as the type description,
        # also replace "." in the descriptor with a " " as extra "."'s can cause 
        # display problems on Mac computers.
        type_descriptor = _tmpstr[0].strip().replace(".", " ")
    
        # split based on the matching close paren 
        _tmpstr = _tmpstr[1].rsplit(")",1)
        # save the end of the string for later
        type_end = _tmpstr[1]
        filter_string = _tmpstr[0]
        
        # if the filter is empty or has parens, return it
        if len(filter_string.strip()) < 1 or filter_string.count("(") > 0 or \
           filter_string.count(")") > 0:
            return filetype

        # replace all occurances of ";" inside because we don't care about that
        # for the purposes of splitting up the file types, then split on " "
        typelist = filter_string.replace(";"," ").strip().split(" ")

        # run a list comprehension to append the separate strings and remove 
        # "*" and "."
        type_filter = "".join(\
            [" "+x.replace('*','').replace('.','') for x in typelist]).strip()

        #assemble the string back together in the new format
        if type_descriptor != "":
            filetype = "%s - %s (%s)%s" % \
                       (type_descriptor, type_filter, filter_string, type_end)
        else:
            filetype = "%s (%s)%s" % \
                       (type_filter, filter_string, type_end)
        return filetype

    separator = ";;"
    filetypes = str(filetypes)
    if filetypes.endswith(separator):
        filetypeList = filetypes.split(separator)
    else:
        filetypeList = [filetypes, ""]
    
    _newFileTypes = ""
    
    # Rebuild and return the file type list string.
    for ftype in filetypeList[:-1]:
        _newFileTypes += munge_ext(ftype) + separator
    _newFileTypes.rstrip(";")
    return QString(_newFileTypes)

class fileSlotsMixin: #bruce 050907 moved these methods out of class MWsemantics
    """
    Mixin class to provide file-related methods for class MWsemantics.
    May not be safe to mix in to any other class, as it creates an
    Assembly(self), and Assembly expects an MWsemantics.  Has slot
    methods and their helper methods.
    """
    #UM 20080702: required for fetching pdb files from the internet
    _pdbCode = ''

    currentOpenBabelImportDirectory = None
    currentImportDirectory = None
    currentPDBSaveDirectory = None
    currentFileInsertDirectory = None
    currentFileOpenDirectory = None

    
    def getCurrentFilename(self, extension = False):
        """
        Returns the filename of the current part.
        
        @param extension: If True, include the filename extension (i.e. .mmp).
                          The default is False.
        @type  extension: boolean
        
        @return: the fullpath of the current part. If the part hasn't been 
                 saved by the user yet, the fullpath returned will be
                 '$CURRENT_WORKING_DIRECTORY/Untitled'.
        @rtype:  string
        
        @note: Callers typically call this method to get a fullpath to supply as
               an argument to QFileDialog, which displays the basename in the
               filename field. Normally, we'd like to include the extension
               so that it is included in the filename field of the QFileDialog,
               but when the user changes the filter (i.e. *.mmp to *.pdb),  
               the extension in the filename field does not get updated to
               match the selected filter. This is a Qt bug and is why we do
               not return the extension by default.
        """
        if self.assy.filename:
            
            fullpath, ext = os.path.splitext(self.assy.filename)
        else: 
            # User hasn't saved the current part yet.
            fullpath = \
                     os.path.join(env.prefs[workingDirectory_prefs_key], 
                                  "Untitled" ) 
            
        if extension:
            return fullpath + ".mmp" # Only MMP format is supported now.
        else:
            return fullpath

    def fileOpenBabelImport(self): # Code copied from fileInsert() slot method. Mark 060731. 
        """
        Slot method for 'File > Import'.
        """
        cmd = greenmsg("Import File: ")
        
        # This format list generated from the Open Babel wiki page: 
        # http://openbabel.sourceforge.net/wiki/Babel#File_Formats
        formats = _convertFiletypesForMacFileDialog(\
            "All Files (*.*);;"\
            "Molecular Machine Part (*.mmp);;"\
            "Accelrys/MSI Biosym/Insight II CAR (*.car);;"\
            "Alchemy (*.alc);;"\
            "Amber Prep (*.prep);;"\
            "Ball and Stick (*.bs);;"\
            "Cacao Cartesian (*.caccrt);;"\
            "CCC (*.ccc);;"\
            "Chem3D Cartesian 1 (*.c3d1);;"\
            "Chem3D Cartesian 2 (*.c3d2);;"\
            "ChemDraw Connection Table (*.ct);;"\
            "Chemical Markup Language (*.cml);;"\
            "Chemical Resource Kit 2D diagram (*.crk2d);;"\
            "Chemical Resource Kit 3D (*.crk3d);;"\
            "CML Reaction (*.cmlr);;"\
            "DMol3 coordinates (*.dmol);;"\
            "Dock 3.5 Box (*.box);;"\
            "FastSearching Index (*.fs);;"\
            "Feature (*.feat);;"\
            "Free Form Fractional (*.fract);;"\
            "GAMESS Output (*.gam);;"\
            "GAMESS Output (*.gamout);;"\
            "Gaussian98/03 Output (*.g03);;"\
            "Gaussian98/03 Output (*.g98);;"\
            "General XML (*.xml);;"\
            "Ghemical (*.gpr);;"\
            "HyperChem HIN (*.hin);;"\
            "Jaguar output (*.jout);;"\
            "MacroModel (*.mmd);;"\
            "MacroModel (*.mmod);;"\
            "MDL MOL (*.mdl);;"\
            "MDL MOL (*.mol);;"\
            "MDL MOL (*.sd);;"\
            "MDL MOL (*.sdf);;"\
            "MDL RXN (*.rxn);;"\
            "MOPAC Cartesian (*.mopcrt);;"\
            "MOPAC Output (*.mopout);;"\
            "MPQC output (*.mpqc);;"\
            "MSI BGF (*.bgf);;"\
            "NWChem output (*.nwo);;"\
            "Parallel Quantum Solutions (*.pqs);;"\
            "PCModel (*.pcm);;"\
            "Protein Data Bank (*.ent);;"\
            "Protein Data Bank (*.pdb);;"\
            "PubChem (*.pc);;"\
            "Q-Chem output (*.qcout);;"\
            "ShelX (*.ins);;"\
            "ShelX (*.res);;"\
            "SMILES (*.smi);;"\
            "Sybyl Mol2 (*.mol2);;"\
            "TurboMole Coordinate (*.tmol);;"\
            "UniChem XYZ (*.unixyz);;"\
            "ViewMol (*.vmol);;"\
            "XYZ cartesian coordinates (*.xyz);;"\
            "YASARA YOB (*.yob);;")

        if (self.currentOpenBabelImportDirectory == None):
            self.currentOpenBabelImportDirectory = self.currentWorkingDirectory
        import_filename = QFileDialog.getOpenFileName(self, 
                                 "Open Babel Import", 
                                 self.currentOpenBabelImportDirectory, 
                                 formats
                                 ) 
        
        if not import_filename:
            env.history.message(cmd + "Cancelled")
            return
        
        if import_filename:
            import_filename = str(import_filename)
            if not os.path.exists(import_filename):
                #bruce 050415: I think this should never happen;
                # in case it does, I added a history message (to existing if/return code).
                env.history.message( cmd + redmsg( "File not found: [ " + import_filename + " ]") )
                return

            # Anything that isn't an MMP file, we will import with Open Babel.
            # Its coverage of MMP files is imperfect so it makes mistakes, but
            # it would be good to use it enough to find those mistakes.

            if import_filename[-3:] == "mmp":
                try:
                    success_code = insertmmp(self.assy, import_filename)
                except:
                    print_compact_traceback( "MWsemantics.py: fileInsert(): error inserting MMP file [%s]: " % import_filename )
                    env.history.message( cmd + redmsg( "Internal error while inserting MMP file: [ " + import_filename +" ]") )
                else:
                    ###TODO: needs history message to depend on success_code
                    # (since Insert can be cancelled or see a syntax error or
                    #  read error). [bruce 080606 comment]
                    self.assy.changed() # The file and the part are not the same.
                    env.history.message( cmd + "MMP file inserted: [ " + os.path.normpath(import_filename) + " ]" ) # fix bug 453 item. ninad060721

# Is Open Babel better than our own? Someone should test it someday.
# Mark 2007-06-05      
#           elif import_filename[-3:] in ["pdb","PDB"]:
#               try:
#                   insertpdb(self.assy, import_filename)
#               except:
#                   print_compact_traceback( "MWsemantics.py: fileInsert(): error inserting PDB file [%s]: " % import_filename )
#                   env.history.message( redmsg( "Internal error while inserting PDB file: [ " + import_filename + " ]") )
#               else:
#                   self.assy.changed() # The file and the part are not the same.
#                   env.history.message( cmd + "PDB file inserted: [ " + os.path.normpath(import_filename) + " ]" )

            else: # All other filetypes, which will be translated to MMP and inserted into the part.
                dir, fil, ext = _fileparse(import_filename)
                tmpdir = find_or_make_Nanorex_subdir('temp')
                mmpfile = os.path.join(tmpdir, fil + ".mmp")
                result = self.launch_ne1_openbabel(in_format = ext[1:], infile = import_filename, 
                                                   out_format = "mmp", outfile = mmpfile)
                if result:
                    success_code = insertmmp(self.assy, mmpfile)
                    # Theoretically, we have successfully imported the file at this point.
                    # But there might be a warning from insertmmp.                    
                    # We'll assume it went well. Mark 2007-06-05
                    ###TODO: needs history message to depend on success_code
                    # (since Insert can be cancelled or see a syntax error or
                    #  read error). [bruce 080606 comment]
                    msg = cmd + "File imported: [ " + os.path.normpath(import_filename) + " ]"
                    env.history.message(msg)

                else:
                    print "Open Babel had problem converting ", import_filename, "->", mmpfile
                    env.history.message(cmd + redmsg("File translation failed."))
            
            self.glpane.scale = self.assy.bbox.scale()
            self.glpane.gl_update()
            self.mt.mt_update()
            
            dir, fil = os.path.split(import_filename)
            self.currentOpenBabelImportDirectory = dir
            self.setCurrentWorkingDirectory(dir)
            
    def fileIOSImport(self): #Urmi 20080618
        """
        Slot method for 'File > Import'.
        Imports IOS file outputted by Parabon Computation Inc 
        Optimizer into the NE-1 model.
        """
        
        #IOS files do not have positional info, hence a structure has to be existing
        # in the screen for this to work.
        # Note that the optimized sequences only get assigned if the structure on
        # the NE-1 window matches the structure in the IOS file
        
        cmd = greenmsg("IOS Import: ")
      
        #check if screen is empty
        if hasattr(self.assy.part.topnode, 'members'):
            numberOfMembers = len(self.assy.part.topnode.members)
        else:
            #Its a clipboard part, probably a chunk or a jig not contained in 
            #a group.
            print "No support for clipboard at this time"
            return
        
        if numberOfMembers == 0:
            msg = "IOS import aborted since there aren't any DNA strands in "\
                "the current model."
            from PyQt4.Qt import QMessageBox
            QMessageBox.warning(self.assy.win, "Warning!", msg)
            return
        
        formats = \
            "Extensive Markup Language (*.xml);;"

        if (self.currentImportDirectory == None) :
            self.currentImportDirectory = currentWorkingDirectory
        import_filename = QFileDialog.getOpenFileName(self, 
                                 "IOS Import", 
                                 self.currentImportDirectory, 
                                 formats
                                 ) 
        if not import_filename:
            env.history.message(cmd + "Cancelled")
            return
        
        success = importFromIOSFile(self.assy, import_filename)
        if success:
            env.history.message(cmd + "Successfully imported optimized strands from " + import_filename)
            
            dir, fil = os.path.split(import_filename)
            self.currentImportDirectory = dir
            self.setCurrentWorkingDirectory(dir)
        else:
            env.history.message(cmd + redmsg("Cannot import " + import_filename))
        return 
    
    def fileIOSExport(self): #Urmi 20080610
        """
        Slot method for 'File > Export'.
        Creates File in IOS format to be used by Parabon Computation Inc 
        Optimizer from the NE-1 model.
        """
        
        cmd = greenmsg("IOS Export: ")
        
        
        if hasattr(self.assy.part.topnode, 'members'):
            numberOfMembers = len(self.assy.part.topnode.members)
        else:
            #Its a clipboard part, probably a chunk or a jig not contained in 
            #a group.
            print "No support for clipboard at this time"
            return
        
        if numberOfMembers == 0:
            print "Nothing to export"
            return
        
        currentFilename = self.getCurrentFilename()
        sfilter = QString("Extensive Markup Language (*.xml)")
        formats = \
            "Extensive Markup Language (*.xml);;"
        export_filename = \
            QFileDialog.getSaveFileName(self, 
                                        "IOS Export", 
                                        currentFilename,
                                        formats,
                                        sfilter
                                       )
        if not export_filename:
            env.history.message(cmd + "Cancelled")
            return
        dir, fil, ext = _fileparse(str(export_filename))
        
        if ext == "":
            export_filename = str(export_filename)  + ".xml"
        
        exportToIOSFormat(self.assy, export_filename)
        env.history.message(cmd + "Successfully exported structure info to " + export_filename)
        return
            
            
    def fileOpenBabelExport(self): # Fixed up by Mark. 2007-06-05
        """
        Slot method for 'File > Export'.
        Exported files contain all atoms, including invisible and hidden atoms.
        This is considered a bug.
        """
        # To Do: Mark 2007-06-05
        #
        # - Export only visible atoms, etc.

        if debug_flags.atom_debug:
            linenum()
            print "start fileOpenBabelExport()"
            
        cmd = greenmsg("Export File: ")
        
        # This format list generated from the Open Babel wiki page: 
        # http://openbabel.sourceforge.net/wiki/Babel#File_Formats

        # -- * * * NOTE * * * --
        # The "MDL" file format used for Animation Master is not the
        # MDL format that Open Babel knows about. It is an animation
        # format, not a chemistry format.
        # Chemistry: http://openbabel.sourceforge.net/wiki/MDL_Molfile
        # Animation: http://www.hash.com/products/am.asp
        # For file export, we will use Open Babel's chemistry MDL format.
        
        currentFilename = self.getCurrentFilename()

        sfilter = _convertFiletypesForMacFileDialog(
            QString("Protein Data Bank format (*.pdb)"))

        formats = _convertFiletypesForMacFileDialog(\
            "Alchemy format (*.alc);;"\
            "MSI BGF format (*.bgf);;"\
            "Dock 3.5 Box format (*.box);;"\
            "Ball and Stick format (*.bs);;"\
            "Chem3D Cartesian 1 format (*.c3d1);;"\
            "Chem3D Cartesian 2 format (*.c3d2);;"\
            "Cacao Cartesian format (*.caccrt);;"\
            "CAChe MolStruct format (*.cache);;"\
            "Cacao Internal format (*.cacint);;"\
            "Chemtool format (*.cht);;"\
            "Chemical Markup Language (*.cml);;"\
            "CML Reaction format (*.cmlr);;"\
            "Gaussian 98/03 Cartesian Input (*.com);;"\
            "Copies raw text (*.copy);;"\
            "Chemical Resource Kit 2D diagram format (*.crk2d);;"\
            "Chemical Resource Kit 3D format (*.crk3d);;"\
            "Accelrys/MSI Quanta CSR format (*.csr);;"\
            "CSD CSSR format (*.cssr);;"\
            "ChemDraw Connection Table format  (*.ct);;"\
            "DMol3 coordinates format (*.dmol);;"\
            "Protein Data Bank format (*.ent);;"\
            "Feature format (*.feat);;"\
            "Fenske-Hall Z-Matrix format (*.fh);;"\
            "SMILES FIX format (*.fix);;"\
            "Fingerprint format (*.fpt);;"\
            "Free Form Fractional format (*.fract);;"\
            "FastSearching (*.fs);;"\
            "GAMESS Input (*.gamin);;"\
            "Gaussian 98/03 Cartesian Input (*.gau);;"\
            "Ghemical format (*.gpr);;"\
            "GROMOS96 format (*.gr96);;"\
            "HyperChem HIN format (*.hin);;"\
            "InChI format (*.inchi);;"\
            "GAMESS Input (*.inp);;"\
            "Jaguar input format (*.jin);;"\
            "Compares first molecule to others using InChI (*.k);;"\
            "MacroModel format (*.mmd);;"\
            "MacroModel format (*.mmod);;"\
            "Molecular Machine Part format (*.mmp);;"\
            "MDL MOL format (*.mol);;"\
            "Sybyl Mol2 format (*.mol2);;"\
            "MOPAC Cartesian format (*.mopcrt);;"\
            "Sybyl descriptor format (*.mpd);;"\
            "MPQC simplified input format (*.mpqcin);;"\
            "NWChem input format (*.nw);;"\
            "PCModel Format (*.pcm);;"\
            "Protein Data Bank format (*.pdb);;"\
            "Protein Data Bank for QuteMolX (*.qdb);;"\
            "POV-Ray input format (*.pov);;"\
            "Parallel Quantum Solutions format (*.pqs);;"\
            "Q-Chem input format (*.qcin);;"\
            "Open Babel report format (*.report);;"\
            "MDL MOL format (*.mdl);;"\
            "MDL RXN format (*.rxn);;"\
            "MDL MOL format (*.sd);;"\
            "MDL MOL format (*.sdf);;"\
            "SMILES format (*.smi);;"\
            "Test format (*.test);;"\
            "TurboMole Coordinate format (*.tmol);;"\
            "Tinker MM2 format (*.txyz);;"\
            "UniChem XYZ format (*.unixyz);;"\
            "ViewMol format (*.vmol);;"\
            "XED format (*.xed);;"\
            "XYZ cartesian coordinates format (*.xyz);;"\
            "YASARA YOB format (*.yob);;"\
            "ZINDO input format (*.zin);;")

        export_filename = \
            QFileDialog.getSaveFileName(self, 
                                        "Open Babel Export", 
                                        currentFilename,
                                        formats,
                                        sfilter
                                       )
        if not export_filename:
            env.history.message(cmd + "Cancelled")
            if debug_flags.atom_debug:
                linenum()
                print "fileOpenBabelExport cancelled because user cancelled"
            return
        export_filename = str(export_filename)

        sext = re.compile('(.*)\(\*(.+)\)').search(str(sfilter))
        assert sext is not None
        formatName = sext.group(1)
        sext = sext.group(2)
        if not export_filename.endswith(sext):
            export_filename += sext

        if debug_flags.atom_debug:
            linenum()
            print "export_filename", repr(export_filename)

        dir, fil, ext = _fileparse(export_filename)
        if ext == ".mmp":
            self.save_mmp_file(export_filename, brag = True)
            
        elif formatName.startswith("Protein Data Bank for QuteMolX"):
            write_qutemol_pdb_file(self.assy.part, export_filename,
                                   EXCLUDE_BONDPOINTS | EXCLUDE_HIDDEN_ATOMS)
        else:
            # Anything that isn't an MMP file we will export with Open Babel.
            # Its coverage of MMP files is imperfect so it makes mistakes, but
            # it would be good to use it enough to find those mistakes.
            dir, fil, ext = _fileparse(export_filename)
            if debug_flags.atom_debug:
                linenum()
                print "dir, fil, ext :", repr(dir), repr(fil), repr(ext)
            
            tmpdir = find_or_make_Nanorex_subdir('temp')
            tmp_mmp_filename = os.path.join(tmpdir, fil + ".mmp")
            
            if debug_flags.atom_debug:
                linenum()
                print "tmp_mmp_filename :", repr(tmp_mmp_filename)
                
            # We simply want to save a copy of the MMP file, not its Part Files, too.
            # savePartFiles = False does this. Mark 2007-06-05
            self.saveFile(tmp_mmp_filename, brag = False, savePartFiles = False)
            
            result = self.launch_ne1_openbabel(in_format = "mmp", infile = tmp_mmp_filename, 
                                               out_format = sext[1:], outfile = export_filename)
            
            if result and os.path.exists(export_filename):
                if debug_flags.atom_debug:
                    linenum()
                    print "file translation OK"
                env.history.message( cmd + "File exported: [ " + export_filename + " ]" )
            else:
                if debug_flags.atom_debug:
                    linenum()
                    print "file translation failed"
                print "Problem translating ", tmp_mmp_filename, '->', export_filename
                env.history.message(cmd + redmsg("File translation failed."))

        if debug_flags.atom_debug:
            linenum()
            print "finish fileOpenBabelExport()"

    def launch_ne1_openbabel(self, in_format, infile, out_format, outfile):
        """
        Runs NE1's own version of Open Babel for translating to/from MMP and
        many chemistry file formats. It will not work with other versions of
        Open Babel since they do not support MMP file format (yet).
        
        <in_format> - the chemistry format of the input file, specified by the
                      file format extension.
        <infile> is the input file.
        <out_format> - the chemistry format of the output file, specified by the
                      file format extension.
        <outfile> is the converted file.

        @return: boolean success code (*not* error code)
        
        Example: babel -immp methane.mmp -oxyz methane.xyz
        """
        # filePath = the current directory NE-1 is running from.
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        # "program" is the full path to *NE1's own* Open Babel executable.
        if sys.platform == 'win32': 
            program = os.path.normpath(filePath + '/../bin/babel.exe')
        else:
            program = os.path.normpath(filePath + '/../bin/babel')
            
        if not os.path.exists(program):
            print "Babel program not found here: ", program
            return False # failure
        
        # Will (Ware) had this debug arg for our version of Open Babel, but
        # I've no idea if it works now or what it does. Mark 2007-06-05.
        if debug_flags.atom_debug:
            debugvar = "WWARE_DEBUG=1"
            print "debugvar =", debugvar
        else:
            debugvar = None
        
        if debug_flags.atom_debug:
            print "program =", program
            
        infile = os.path.normpath(infile)
        outfile = os.path.normpath(outfile)
        
        in_format = "-i"+in_format
        out_format = "-o"+out_format
            
        arguments = QStringList()
        i = 0
        for arg in [in_format, infile, out_format, outfile, debugvar]:
            if not arg:
                continue # For debugvar.
            if debug_flags.atom_debug:
                print "argument", i, " :", repr(arg)
            i += 1
            arguments.append(arg)
                    
        # Looks like Will's special debugging code. Mark 2007-06-05
        if debug_babel:
            # wware 060906  Create a shell script to re-run Open Babel
            outf = open("rerunbabel.sh", "w")
            # On the Mac, "-f" prevents running .bashrc
            # On Linux it disables filename wildcards (harmless)
            outf.write("#!/bin/sh -f\n")
            for a in arguments:
                outf.write(str(a) + " \\\n")
            outf.write("\n")
            outf.close()
        
        # Need to set these environment variables on MacOSX so that babel can
        # find its libraries. Brian Helfrich 2007/06/05
        if sys.platform == 'darwin':
            babelLibPath = os.path.normpath(filePath + '/../Frameworks')
            os.environ['DYLD_LIBRARY_PATH'] = babelLibPath
            babelLibPath = babelLibPath + '/openbabel'
            os.environ['BABEL_LIBDIR'] = babelLibPath

        print "launching openbabel:", program, [str_or_unicode(arg) for arg in arguments]
        
        proc = QProcess()
        proc.start(program, arguments) # Mark 2007-06-05

        if not proc.waitForFinished (100000): 
            # Wait for 100000 milliseconds (100 seconds)
            # If not done by then, return an error.
            print "openbabel timeout (100 sec)"
            return False # failure
    
        exitStatus = proc.exitStatus()
        stderr = str(proc.readAllStandardError())[:-1]
        stderr2 = str(stderr.split(os.linesep)[-1])
        stderr2 = stderr2.strip()
        success = (exitStatus == 0 and stderr2 == "1 molecule converted")
        if not success or debug_flags.atom_debug:
            print "exit status:", exitStatus
            print "stderr says:", stderr
            print "stderr2 says:"%stderr2
            print "'success' is:", success
            print "stderr2 == str(1 molecule converted)?" , (stderr2 == "1 molecule converted")
            print "finish launch_ne1_openbabel(%s, %s)" % (repr(infile), repr(outfile))
        return success

    def fileInsertMmp(self):
        """
        Slot method for 'Insert > Molecular Machine Part file...'.
        """
        formats = \
                "Molecular Machine Part (*.mmp);;"\
                "All Files (*.*)"
        self.fileInsert(formats)
    
    #UM 20080702: methods for fetching pdb files from the internet 
    def fileFetchPdb(self):
        """
        Slot method for 'File > Fetch > Fetch PDB...'.
        """      
        form = FetchPDBDialog(self)
        self.connect(form, SIGNAL('editingFinished()'), self.getPDBFileFromInternet)
        return
    
    def checkIfCodeIsValid(self, code):
        """
        Check if the PDB ID I{code} is valid. 
        
        @return: ok, code
        
        If a five letter code is entered and the last character is '_' it 
        is altered to ' '
        """            
        #first check if the length is correct
        if not (len(code) == 4 or  len(code) == 5):
            return False, code
        if len(code) == 4:
            end = len(code)
        else:
            end = len(code) - 1
        if not code[0].isdigit(): 
            return False, code
        for i in range(1, end):
            if not (code[i].isdigit() or code[i].isalpha()):
                return False, code
        #special treatment for the fifth character
        if len(code) == 5:
            if not (code[4].isdigit() or code[4].isalpha() or code[4] == '_'):
                return False, code
            if code[4] == '_':
                tempCode = code[0:3] + ' '
                code = tempCode
        return True, code
    
    def getAndWritePDBFile(self, code):
        """
        Fetch a PDB file from the internet (RCSB databank) and write it to a 
        temporary location that is later removed.
        
        @return: The full path to the PDB temporary file fetched from RCSB.
        @rtype: string
        """
        
        try:
            # Display the "wait cursor" since this might take some time.
            from ne1_ui.cursors import showWaitCursor
            showWaitCursor(True) 
            
            urlString = "http://www.rcsb.org/pdb/download/downloadFile.do?fileFormat=pdb&compression=NO&structureId=" + code
            doc = urlopen(urlString).read()
            if doc.find("No File Found") != -1:
                msg = "No protein exists in the PDB with this code."
                QMessageBox.warning(self, "Attention!", msg)
                showWaitCursor(False)
                return ''
        except:
            msg = "Error connecting to RCSB using URL [%s]" % urlString
            print_compact_traceback( msg )
            env.history.message( redmsg( msg ) )
            showWaitCursor(False)
            return ''
        
        # Create full path to Nanorex temp directory for pdb file.
        tmpdir = find_or_make_Nanorex_subdir('temp')
        pdbTmpFile = os.path.join(tmpdir, code + ".pdb")
        
        f = open(pdbTmpFile, 'w')
        f.write(doc)
        f.close()
        
        showWaitCursor(False) # Revert to the previous cursor.
        return pdbTmpFile   
    
    def insertPDBFromURL(self, filePath, chainID):
        """
        read the pdb file
        """
        try:
            if chainID is not None:
                insertpdb(self.assy, filePath, chainID)
            else:
                insertpdb(self.assy, filePath)
        except:
            print_compact_traceback( "MWsemantics.py: fileInsert(): error inserting PDB file [%s]: " % filePath )
            env.history.message( redmsg( "Internal error while inserting PDB file: [ " + filePath + " ]") )
        else:
            self.assy.changed() # The file and the part are not the same.
            env.history.message( "PDB file inserted: [ " + os.path.normpath(filePath) + " ]" )
            
        self.glpane.scale = self.assy.bbox.scale()
        self.glpane.gl_update()
        self.mt.mt_update()
        return
    
    def savePDBFileIfDesired(self, code, filePath):
        """
        Since the downloaded pdb file is stored in a temporary location, this
        allows the user to store it permanently.
        """
        # ask the user if he wants to save the file otherwise its deleted

        msg = "Do you want to save a copy of this PDB file in its original "\
            "format to your system disk before continuing?"

        ret = QMessageBox.warning( self, "Attention!",
                                   msg,
                                   "&Yes", "&No", "",
                                   0,   # Enter  = button 0 (yes)
                                   1)   # Escape = button 1 (no)
        if ret: 
            return # User selected 'No'.
        
        # Save this file
        formats = \
                "Protein Data BanK (*.pdb);;"
        if (self.currentPDBSaveDirectory == None):
            self.currentPDBSaveDirectory = self.currentWorkingDirectory
        directory = self.currentPDBSaveDirectory
        fileName = code + ".pdb"
        currentFilename = directory + '/' + fileName
        sfilter = QString("Protein Data Bank (*.pdb)")
        fn = QFileDialog.getSaveFileName(self, 
                                         "Save PDB File", 
                                         currentFilename,
                                         formats,
                                         sfilter)
        fileObject1 = open(filePath, 'r')
        if fn:
            fileObject2 = open(fn, 'w+') 
                #@ Review: fileObject2 will be overwritten if it exists.
                # You should get confirmation from user first!
                # mark 2008-07-03
        else:
            return
        doc = fileObject1.readlines()
        # we will write to this pdb file everything, irrespective of
        # what the chain id is. Its too complicated to parse the info related
        # to this particular chain id
        fileObject2.writelines(doc)
        fileObject1.close()
        fileObject2.close()
        dir, fil = os.path.split(str(fn))
        self.currentPDBSaveDirectory = dir
        self.setCurrentWorkingDirectory(dir)
        env.history.message( "PDB file saved: [ " + os.path.normpath(str(fn)) + " ]")
        
        return    

    def getPDBFileFromInternet(self):
        """
        slot method for PDBFileDialog
        """
        checkIfCodeValid, code = self.checkIfCodeIsValid(self._pdbCode)  
        if not checkIfCodeValid:
            msg = "'%s' is an invalid PDB ID. Download aborted." % code
            env.history.message(redmsg(msg))
            QMessageBox.warning(self, "Attention!", msg)
            return
        
        filePath = self.getAndWritePDBFile(code[0:4])    
        if not filePath:
            return
        if len(code) == 5:
            self.insertPDBFromURL(filePath, code[4])
        else:
            self.insertPDBFromURL(filePath, None)
        self.savePDBFileIfDesired(code, filePath)
        # delete the temp PDB file
        os.remove(filePath)
        return
    
    def setPDBCode(self, code):
        """
        Sets the pdb code 
        """
        self._pdbCode = code  
        return
    
    def fileInsertPdb(self):
        """
        Slot method for 'Insert > Protein Data Bank file...'.
        """
        formats = \
                "Protein Data Bank (*.pdb);;"\
                "All Files (*.*)"
        self.fileInsert(formats)
    
    def fileInsertIn(self):
        """
        Slot method for 'Insert > AMBER .in file fragment...'.
        """
        formats = \
                "AMBER internal coordinates file fragment (*.in_frag);;"\
                "All Files (*.*)"
        self.fileInsert(formats)
    
    def fileInsert(self, formats):
        """
        Inserts a file in the current part.
        
        @param formats: File format options in chooser filter. 
        @type  formats: list of strings
        """
        
        env.history.message(greenmsg("Insert File:"))
        
        if (self.currentFileInsertDirectory == None):
            self.currentFileInsertDirectory = self.currentWorkingDirectory
        fn = QFileDialog.getOpenFileName(self, 
                                         "Insert File", 
                                         self.currentFileInsertDirectory, 
                                         formats)
                        
        if not fn:
            env.history.message("Cancelled")
            return
        
        if fn:
            fn = str(fn)
            if not os.path.exists(fn):
                #bruce 050415: I think this should never happen;
                # in case it does, I added a history message (to existing if/return code).
                env.history.message( redmsg( "File not found: [ " + fn+ " ]") )
                return

            if fn[-3:] == "mmp":
                try:
                    success_code = insertmmp(self.assy, fn)
                except:
                    print_compact_traceback( "MWsemantics.py: fileInsert(): error inserting MMP file [%s]: " % fn )
                    env.history.message( redmsg( "Internal error while inserting MMP file: [ " + fn+" ]") )
                else:
                    ###TODO: needs history message to depend on success_code
                    # (since Insert can be cancelled or see a syntax error or
                    #  read error). [bruce 080606 comment]
                    self.assy.changed() # The file and the part are not the same.
                    env.history.message( "MMP file inserted: [ " + os.path.normpath(fn) + " ]" )# fix bug 453 item. ninad060721
            
            if fn[-3:] in ["pdb","PDB"]:
                try:
                    insertpdb(self.assy, fn)
                except:
                    print_compact_traceback( "MWsemantics.py: fileInsert(): error inserting PDB file [%s]: " % fn )
                    env.history.message( redmsg( "Internal error while inserting PDB file: [ " + fn + " ]") )
                else:
                    self.assy.changed() # The file and the part are not the same.
                    env.history.message( "PDB file inserted: [ " + os.path.normpath(fn) + " ]" )

            if fn[-7:] == "in_frag":
                try:
                    success_code = insertin(self.assy, fn)
                except:
                    print_compact_traceback( "MWsemantics.py: fileInsert(): error inserting IN_FRAG file [%s]: " % fn )
                    env.history.message( redmsg( "Internal error while inserting IN_FRAG file: [ " + fn+" ]") )
                else:
                    ###TODO: needs history message to depend on success_code
                    # (since Insert can be cancelled or see a syntax error or
                    #  read error). [bruce 080606 comment]
                    self.assy.changed() # The file and the part are not the same.
                    env.history.message( "IN file inserted: [ " + os.path.normpath(fn) + " ]" )# fix bug 453 item. ninad060721
            
            self.glpane.scale = self.assy.bbox.scale()
            self.glpane.gl_update()
            self.mt.mt_update()
            
            # Update the current working directory (CWD). Mark 060729.
            dir, fil = os.path.split(fn)
            self.currentFileInsertDirectory = dir
            self.setCurrentWorkingDirectory(dir)

    def fileOpen(self, recentFile = None):
        """
        Slot method for 'File > Open'.
        
        By default, we assume user wants to specify file to open
        through 'Open File' dialog.

        @param recentFile: if provided, specifies file to open,
                           assumed to come from the 'Recent Files' menu list;
                           no Open File dialog will be used.
                           The file may or may not exist.
        @type recentFile: string
        """
        env.history.message(greenmsg("Open File:"))

        warn_about_abandoned_changes = True
            # note: this is turned off later if the user explicitly agrees
            # to discard unsaved changes [bruce 080909]

        if self.assy.has_changed():
            ret = QMessageBox.warning( self, "Warning!",
                "The part contains unsaved changes.\n"
                "Do you want to save the changes before opening a new part?",
                "&Save", "&Discard", "Cancel",
                0,      # Enter == button 0
                2 )     # Escape == button 2
            
            if ret == 0:
                # Save clicked or Alt+S pressed or Enter pressed.
                #Huaicai 1/6/05: If user now cancels save operation, return 
                # without letting user open another file
                if not self.fileSave():
                    return
            elif ret == 1:
                # Discard
                warn_about_abandoned_changes = False
                    # note: this is about *subsequent* discards on same old
                    # model, if any (related to exit_is_forced)
                #Huaicai 12/06/04: don't clear assy, since user may cancel the file open action below
                pass ## self._make_and_init_assy()
            elif ret == 2:
                # Cancel clicked or Alt+C pressed or Escape pressed
                env.history.message("Cancelled.")              
                return
            else:
                assert 0 #bruce 080909

        if recentFile:
            if not os.path.exists(recentFile):
                if hasattr(self, "name"):
                    name = self.name()
                else:
                    name = "???"
                QMessageBox.warning( self, name,
                                     "The file [ " + recentFile + " ] doesn't exist any more.",
                                     QMessageBox.Ok, QMessageBox.NoButton)
                return
            
            fn = recentFile
        else:
            formats = \
                    "Molecular Machine Part (*.mmp);;"\
                    "GROMACS Coordinates (*.gro);;"\
                    "All Files (*.*)"
            
            if (self.currentFileOpenDirectory == None):
                self.currentFileOpenDirectory = self.currentWorkingDirectory
            fn = QFileDialog.getOpenFileName(self,
                                             "Open File",
                                             self.currentFileOpenDirectory,
                                             formats)
                    
            if not fn:
                env.history.message("Cancelled.")
                return

        if fn:
            start = begin_timing("File..Open")
            self.updateRecentFileList(fn)

            self._make_and_init_assy('$DEFAULT_MODE',
                   warn_about_abandoned_changes = warn_about_abandoned_changes )
                # resets self.assy to a new, empty Assembly object
            
            self.assy.clear_undo_stack()
                # important optimization -- the first call of clear_undo_stack
                # (for a given value of self.assy) does two initial checkpoints,
                # whereas all later calls do only one. Initial checkpoints
                # (which scan all the objects that hold undoable state which are
                # accessible from assy) are fast if done now (since assy is
                # empty), but might be quite slow later (after readmmp adds lots
                # of data to assy). So calling it now should speed up the later
                # call (near the end of this method) by making it scan all data
                # once rather than twice. The speedup from this has been
                # verified. [bruce & ericm 080225/082229]
            
            fn = str_or_unicode(fn)
            if not os.path.exists(fn):
                return
                #k Can that return ever happen? Does it need an error message?
                # Should preceding clear and modechange be moved down here??
                # (Moving modechange even farther below would be needed,
                #  if we ever let the default mode be one that cares about the
                #  model or viewpoint when it's entered.)
                # [bruce 050911 questions]
            
            _openmsg = "" # Precaution.
                ### REVIEW: it looks like this is sometimes used, and it probably
                # ought to be more informative, or be tested as a flag if
                # no message is needed in those cases. If it's never used,
                # it's not obvious why so that needs to be explained.
                # [bruce 080606 comment]
            env.history.message("Opening file...")
            
            isMMPFile = False
            gromacsCoordinateFile = None

            if fn[-4:] == ".gro":
                gromacsCoordinateFile = fn
                failedToFindMMP = True
                fn = gromacsCoordinateFile[:-3] + "mmp"
                if (os.path.exists(fn)):
                    failedToFindMMP = False
                elif gromacsCoordinateFile[-8:] == ".xyz.gro":
                    fn = gromacsCoordinateFile[:-7] + "mmp"
                    if (os.path.exists(fn)):
                        failedToFindMMP = False
                elif gromacsCoordinateFile[-12:] == ".xyz-out.gro":
                    fn = gromacsCoordinateFile[:-11] + "mmp"
                    if (os.path.exists(fn)):
                        failedToFindMMP = False
                if (failedToFindMMP):
                    env.history.message(redmsg("Could not find .mmp file associated with %s" % gromacsCoordinateFile))
                    return

            # This puts up the hourglass cursor while opening a file.
            QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
            
            ok = SUCCESS
            
            if fn[-3:] == "mmp":
                ok, listOfAtoms = readmmp(self.assy, 
                                          fn, 
                                          showProgressDialog = True, 
                                          returnListOfAtoms = True)
                    #bruce 050418 comment: we need to check for an error return
                    # and in that case don't clear or have other side effects on assy;
                    # this is not yet perfectly possible in readmmmp.
                    #mark 2008-06-05 comment: I included an error return value
                    # for readmmp (ok) checked below. The code below needs to 
                    # be cleaned up, but I need Bruce's help to do that.
                if ok == SUCCESS:
                    _openmsg = "MMP file opened: [ " + os.path.normpath(fn) + " ]"  
                elif ok == ABORTED:
                    _openmsg = orangemsg("Open cancelled: [ " + os.path.normpath(fn) + " ]")
                elif ok == READ_ERROR:
                    _openmsg = redmsg("Error reading: [ " + os.path.normpath(fn) + " ]")
                else:
                    msg = "Unrecognized readmmp return value %r" % (ok,)
                    print_compact_traceback(msg + ": ")
                    _openmsg = redmsg("Bug: " + msg) #bruce 080606 bugfix
                isMMPFile = True
                if ok == SUCCESS and (gromacsCoordinateFile):
                    #bruce 080606 added condition ok == SUCCESS (likely bugfix) 
                    newPositions = readGromacsCoordinates(gromacsCoordinateFile, listOfAtoms)
                    if (type(newPositions) == type([])):
                        move_atoms_and_normalize_bondpoints(listOfAtoms, newPositions)
                    else:
                        env.history.message(redmsg(newPositions))
            
            if ok == SUCCESS:
                dir, fil, ext = _fileparse(fn)
                # maybe: could replace some of following code with new method just now split out of saved_main_file [bruce 050907 comment]
                self.assy.name = fil
                self.assy.filename = fn
            self.assy.reset_changed() # The file and the part are now the same
            self.update_mainwindow_caption()

            if isMMPFile:
                #bruce 050418 moved this code into a new function in files_mmp.py
                # (but my guess is it should mostly be done by readmmp itself)
                fix_assy_and_glpane_views_after_readmmp( self.assy, self.glpane)
            else: ###PDB or other file format        
                self.setViewFitToWindow()
                
            self.assy.clear_undo_stack() #bruce 060126, fix bug 1398
                # note: this is not redundant with the earlier call in this
                # method -- both are needed. See comment there for details.
                # [bruce comment 080229]

            ## russ 080603: Replaced by a call on gl_update_duration in
            ## GLPane.AnimateToView(), necessary for newly-created models.
            ##self.glpane.gl_update_duration(new_part = True) #mark 060116.
            
            self.mt.mt_update()
            
            # All set. Restore the normal cursor and print a history msg.
            env.history.message(_openmsg)
            QApplication.restoreOverrideCursor() # Restore the cursor
            end_timing(start, "File..Open")

            dir, fil = os.path.split(fn)
            self.currentFileOpenDirectory = dir
            
        self.setCurrentWorkingDirectory()
        
        return

    def fileSave(self):
        """
        Slot method for 'File > Save'.
        """
        env.history.message(greenmsg("Save File:"))
        
        #Huaicai 1/6/05: by returning a boolean value to say if it is really 
        # saved or not, user may choose "Cancel" in the "File Save" dialog          
        if self.assy:
            if self.assy.filename: 
                self.saveFile(self.assy.filename)
                return True
            else: 
                return self.fileSaveAs()
        return False #bruce 050927 added this line (should be equivalent to prior implicit return None)

    def fileSaveAs(self): #bruce 050927 revised this
        """
        Slot method for 'File > Save As'.
        """
        safile = self.fileSaveAs_filename()
        # fn will be None or a Python string
        if safile:
            self.saveFile(safile)
            return True
        else:
            # user cancelled, or some other error; message already emitted.
            return False
        pass
        
    def fileExportPdb(self):
        """
        Slot method for 'File > Export > Protein Data Bank...'
        
        @return: The name of the file saved, or None if the user cancelled.
        @rtype:  string
        """
        format = "Protein Data Bank (*.pdb)"
        return self.fileExport(format)
    
    def fileExportQuteMolXPdb(self):
        """
        Slot method for 'File > Export > Protein Data Bank for QuteMolX...'
        
        @return: The name of the file saved, or None if the user cancelled.
        @rtype:  string
        """
        format = "Protein Data Bank for QuteMolX (*.qdb)"
        return self.fileExport(format)
        
    def fileExportJpg(self):
        """
        Slot method for 'File > Export > JPEG Image...'
        
        @return: The name of the file saved, or None if the user cancelled.
        @rtype:  string
        """
        format = "JPEG (*.jpg)"
        return self.fileExport(format)
    
    def fileExportPng(self):
        """
        Slot method for 'File > Export > PNG Image...'
        
        @return: The name of the file saved, or None if the user cancelled.
        @rtype:  string
        """
        format = "Portable Network Graphics (*.png)"
        return self.fileExport(format)
    
    def fileExportPov(self):
        """
        Slot method for 'File > Export > POV-Ray...'
        
        @return: The name of the file saved, or None if the user cancelled.
        @rtype:  string
        """
        format = "POV-Ray (*.pov)"
        return self.fileExport(format)

    def fileExportAmdl(self):
        """
        Slot method for 'File > Export > Animation Master Model...'
        
        @return: The name of the file saved, or None if the user cancelled.
        @rtype:  string
        
        @note: There are more popular .mdl file formats that we may need
               to support in the future. This option was needed by John
               Burch to create the nanofactory animation.
        """
        format = "Animation Master Model (*.mdl)"
        return self.fileExport(format)
    
    def fileExport(self, format):
        """
        Exports the current part into a different file format.
        
        @param format: File format filter string to appear in the "Export As..."
                       file chooser dialog.
        @type  format: string
        
        @return: The name of the file saved, or None if the user cancelled.
        @rtype:  string
        """
        
        cmd = greenmsg("Export:")
        
        currentFilename = self.getCurrentFilename()
        sfilter = QString(format)
        options = QFileDialog.DontConfirmOverwrite # this fixes bug 2380 [bruce 070619]
            # Note: we can't fix that bug by removing our own confirmation
            # (later in this function) instead, since the Qt confirmation 
            # doesn't happen if the file extension is implicit, as it is by
            # default due to the workaround for bug 225 (above) in which 
            # currentFilename doesn't contain ext.

        # debug_prefs for experimentation with dialog style [bruce 070619]
        if (sys.platform == 'darwin' and 
            debug_pref("File Save As: DontUseSheet", 
                       Choice_boolean_False, 
                       prefs_key = True)):
            options |= QFileDialog.DontUseSheet # probably faster
        if debug_pref("File Save As: DontUseNativeDialog", 
                      Choice_boolean_False, 
                      prefs_key = True):
            options |= QFileDialog.DontUseNativeDialog
            
        fn = QFileDialog.getSaveFileName(
            self, # parent
            "Export As", # caption
            currentFilename, # dialog's cwd and basename
            format, # file format options
            sfilter, # selectedFilter
            QFileDialog.DontConfirmOverwrite # options
            )
        
        if not fn:
            return None
        
        # [bruce question: when and why can this differ from fn?]
        # IIRC, fileparse() doesn't (or didn't) handle QString types. 
        # mark 2008-01-23
        fn = str(fn)
        dir, fil, ext2 = _fileparse(fn)
        del fn #bruce 050927
        ext = str(sfilter[-5:-1]) 
            # Get "ext" from the sfilter. 
            # It *can* be different from "ext2"!!! - Mark
        safile = dir + fil + ext # full path of "Save As" filename

        # ask user before overwriting an existing file
        # (other than this part's main file)
        if os.path.exists(safile):
            # Confirm overwrite of the existing file.
            ret = QMessageBox.warning( self, "Warning!",
                "The file \"" + fil + ext + "\" already exists.\n"\
                "Do you want to overwrite the existing file?",
                "&Overwrite", "&Cancel", "",
                0,      # Enter == button 0
                1 )     # Escape == button 1

            if ret == 1: # The user cancelled
                env.history.message( cmd + "Cancelled. Part not exported." )
                return None # Cancel/Escape pressed, user cancelled.

        ###e bruce comment 050927: this might be a good place to test whether we can write to that filename,
        # so if we can't, we can let the user try choosing one again, within
        # this method. But we shouldn't do this if it's the main filename, 
        # to avoid erasing that file now. (If we only do this test with each
        # function that writes into the file, then if that fails it'll more
        # likely require user to redo the entire op.)
        
        self.saveFile(safile)
        return safile
        
    def fileSaveAs_filename(self):
        #bruce 050927 split this out of fileSaveAs, added some comments, 
        # added images_ok option
        """
        Prompt user with a "Save As..." file chooser dialog to specify a
        new MMP filename. If file exists, ask them to confirm overwrite of
        that file.
        
        @return: the filename. If if user cancels, or if some error occurs,
                 emit a history message and return None.
        @rtype:  string
        """
        currentFilename = self.getCurrentFilename()
        format = "Molecular Machine Part (*.mmp)"
        sfilter = QString(format)
        options = QFileDialog.DontConfirmOverwrite 
            # this fixes bug 2380 [bruce 070619]
            # Note: we can't fix that bug by removing our own confirmation
            # (later in this function) instead, since the Qt confirmation 
            # doesn't happen if the file extension is implicit, as it is by
            # default due to the workaround for bug 225 (above) in which 
            # currentFilename doesn't contain ext.

        # debug_prefs for experimentation with dialog style [bruce 070619]
        if (sys.platform == 'darwin' 
            and debug_pref("File Save As: DontUseSheet", 
                           Choice_boolean_False, 
                           prefs_key = True)):
            options |= QFileDialog.DontUseSheet # probably faster -- try it and see
        if debug_pref("File Save As: DontUseNativeDialog", 
                      Choice_boolean_False, 
                      prefs_key = True):
            options |= QFileDialog.DontUseNativeDialog
        
        fn = QFileDialog.getSaveFileName(
            self, # parent
            "Save As", # caption
            currentFilename, # # dialog's cwd and basename
            format, # filter
            sfilter, # selectedFilter
            QFileDialog.DontConfirmOverwrite # options
            )
        
        if not fn:
            return None # User cancelled.
        
        # [bruce question: when and why can this differ from fn?]
        # IIRC, fileparse() doesn't (or didn't) handle QString types. 
        # mark 2008-01-23
        fn = str_or_unicode(fn)
        dir, fil, ext2 = _fileparse(fn)
        del fn #bruce 050927
        ext = str(sfilter[-5:-1]) 
            # Get "ext" from the sfilter. It *can* be different from "ext2"!!!
            # Note: As of 2008-01-23, only the MMP extension is supported.
            # This may change in the future. Mark 2008-01-23.
        safile = dir + fil + ext # full path of "Save As" filename

        # Ask user before overwriting an existing file 
        # (except this part's main file)
        if self.assy.filename != safile: 
            # If the current part and "Save As" filename are not the same...
            if os.path.exists(safile): 
                # ...and if the "Save As" file exists.
                # confirm overwrite of the existing file.
                ret = QMessageBox.warning( self, "Warning!",
                    "The file \"" + fil + ext + "\" already exists.\n"\
                    "Do you want to overwrite the existing file?",
                    "&Overwrite", "&Cancel", "",
                    0,      # Enter == button 0
                    1 )     # Escape == button 1

                if ret == 1: # The user cancelled
                    env.history.message( "Cancelled.  Part not saved." )
                   
                    return None # User cancelled

        ###e bruce comment 050927: this might be a good place to test whether we can write to that filename,
        # so if we can't, we can let the user try choosing one again, within this method.
        # But we shouldn't do this if it's the main filename, to avoid erasing that file now.
        # (If we only do this test with each function
        # that writes into the file, then if that fails it'll more likely require user to redo the entire op.)
        
        return safile
        
    def fileSaveSelection(self): #bruce 050927
        """
        Slot method for 'File > Save Selection'.
        """
        env.history.message(greenmsg("Save Selection:"))
            # print this before counting up what selection contains, in case that's slow or has bugs
        (part, killfunc, desc) = self.assy.part_for_save_selection()
            # part is existing part (if entire current part was selected)
            # or new homeless part with a copy of the selection (if selection is not entire part)
            # or None (if the current selection can't be saved [e.g. if nothing selected ##k]).
            # If part is not None, its contents are described in desc;
            # otherwise desc is an error message intended for the history.
        if part is None:
            env.history.message(redmsg(desc))
            return
        # now we're sure the current selection is savable
        safile = self.fileSaveAs_filename( images_ok = False)
            ##e if entire part is selected, could pass images_ok = True,
            # if we also told part_for_save_selection above never to copy it,
            # which is probably appropriate for all image-like file formats
        saved = self.savePartInSeparateFile(part, safile)
        if saved:
            desc = desc or "selection"
            env.history.message( "Saved %s in %s" % (desc, safile) )
                #e in all histmsgs like this, we should encode html chars in safile and desc!
        else:
            pass # assume savePartInSeparateFile emitted error message
        killfunc()
        return

    def saveFile(self, safile, brag = True, savePartFiles = True):
        """
        Save the current part as I{safile}.
        
        @param safile: the part filename.
        @type  safile: string
        
        @param savePartFiles: True (default) means save any part files if this
                              MMP file has a Part Files directory.
                              False means just save the MMP file and don't 
                              worry about saving the Part Files directory, too.
        """
        
        dir, fil, ext = _fileparse(safile)
            #e only ext needed in most cases here, could replace with os.path.split [bruce 050907 comment]
                    
        if ext == ".mmp" : # Write MMP file.
            self.save_mmp_file(safile, brag = brag, savePartFiles = savePartFiles)
            self.setCurrentWorkingDirectory() # Update the CWD.
                
        else:
            self.savePartInSeparateFile( self.assy.part, safile)
        return

    def savePartInSeparateFile( self, part, safile): #bruce 050927 added part arg, renamed method
        """
        Save some aspect of part (which might or might not be self.assy.part)
        in a separate file, named safile, without resetting self.assy's 
        changed flag or filename. For some filetypes, use display attributes 
        from self.glpane.
        
        For JPG and PNG, assert part is the glpane's current part, since 
        current implem only works then.
        """
        #e someday this might become a method of a "saveable object" (open file) or a "saveable subobject" (part, selection).
        linenum()
        dir, fil, ext = _fileparse(safile)
            #e only ext needed in most cases here, could replace with os.path.split [bruce 050908 comment]
        type = "this" # never used (even if caller passes in unsupported filetype) unless there are bugs in this routine
        saved = True # be optimistic (not bugsafe; fix later by having save methods which return a success code)
        glpane = self.glpane
        try:
            # all these cases modify type variable, for use only in subsequent messages.
            # kluges: glpane is used for various display options;
            # and for grabbing frame buffer for JPG and PNG formats
            # (only correct when the part being saved is the one it shows, which we try to check here).
            linenum()
            if ext == ".mmp": #bruce 050927; for now, only used by Save Selection
                type = "MMP"
                part.writemmpfile( safile) ###@@@ WRONG, stub... this writes a smaller file, unreadable before A5, with no saved view.
                #e also, that func needs to report errors; it probably doesn't now.
                ###e we need variant of writemmpfile_assy, but the viewdata will differ...
                # pass it a map from partindex to part?
                # or, another way, better if it's practical: ###@@@ DOIT
                #   make a new assy (no shelf, same pov, etc) and save that. kill it at end.
                #   might need some code cleanups. what's done to it? worry about saver code reset_changed on it...
                msg = "Save Selection: not yet fully implemented; saved MMP file lacks viewpoint and gives warnings when read."
                # in fact, it lacks chunk/group structure and display modes too, and gets hydrogenated as if for sim!
                print msg
                env.history.message( orangemsg(msg) )
            elif ext == ".pdb": #bruce 050927; for now, only used by Save Selection
                type = "PDB"
                writepdb(part, safile)
            elif ext == ".qdb": #mark 2008-03-21
                type = "QDB"
                write_qutemol_pdb_file(self.assy.part, safile,
                                   EXCLUDE_BONDPOINTS | EXCLUDE_HIDDEN_ATOMS)
            elif ext == ".pov":
                type = "POV-Ray"
                writepovfile(part, glpane, safile) #bruce 050927 revised arglist
            elif ext == ".mdl":
                linenum()
                type = "MDL"
                writemdlfile(part, glpane, safile) #bruce 050927 revised arglist
            elif ext == ".jpg":
                type = "JPEG"
                image = glpane.grabFrameBuffer()
                image.save(safile, "JPEG", 85)
                assert part is self.assy.part, "wrong image was saved" #bruce 050927
                assert self.assy.part is glpane.part, "wrong image saved since glpane not up to date" #bruce 050927
            elif ext == ".png":
                type = "PNG"
                image = glpane.grabFrameBuffer()
                image.save(safile, "PNG")
                assert part is self.assy.part, "wrong image was saved" #bruce 050927
                assert self.assy.part is glpane.part, "wrong image saved since glpane not up to date" #bruce 050927
            else: # caller passed in unsupported filetype (should never happen)
                saved = False
                env.history.message(redmsg( "File Not Saved. Unknown extension: " + ext))
        except:
            linenum()
            print_compact_traceback( "error writing file %r: " % safile )
            env.history.message(redmsg( "Problem saving %s file: " % type + safile ))
        else:
            linenum()
            if saved:
                linenum()
                env.history.message( "%s file saved: " % type + safile )
        return

    def save_mmp_file(self, safile, brag = True, savePartFiles = True):
        # bruce 050907 split this out of saveFile; maybe some of it should be moved back into caller ###@@@untested
        """
        Save the current part as a MMP file under the name <safile>.
        If we are saving a part (assy) that already exists and it has an (old) Part Files directory, 
        copy those files to the new Part Files directory (i.e. '<safile> Files').
        """
        dir, fil, extjunk = _fileparse(safile)

        from dna.updater.dna_updater_prefs import pref_mmp_save_convert_to_PAM5
        from utilities.constants import MODEL_PAM5
        # temporary, so ok to leave local for now:
        from utilities.GlobalPreferences import debug_pref_write_bonds_compactly
        from utilities.GlobalPreferences import debug_pref_read_bonds_compactly

        # determine options for writemmpfile
        options = dict()
        if pref_mmp_save_convert_to_PAM5(): # maybe WRONG, see whether calls differ in this! ##### @@@@@@ [bruce 080326]
            options.update(dict(convert_to_pam = MODEL_PAM5,
                                honor_save_as_pam = True))
            pass
        if debug_pref_write_bonds_compactly(): # bruce 080328
            # temporary warning
            env.history.message( orangemsg( "Warning: writing mmp file with experimental bond_chain records"))
            if not debug_pref_read_bonds_compactly():
                env.history.message( orangemsg( "Warning: your bond_chain reading code is presently turned off"))
            options.update(dict(write_bonds_compactly = True))
            pass
        
        tmpname = "" # in case of exceptions
        try:
            tmpname = os.path.join(dir, '~' + fil + '.m~')
            self.assy.writemmpfile(tmpname, **options)
        except:
            #bruce 050419 revised printed error message
            print_compact_traceback( "Problem writing file [%s]: " % safile )
            env.history.message(redmsg( "Problem saving file: " + safile ))
            
            # If you want to see what was wrong with the MMP file, you can comment this out so 
            # you can see what's in the temp MMP file.  Mark 050128.
            if os.path.exists(tmpname):
                os.remove (tmpname) # Delete tmp MMP file
        else:
            if os.path.exists(safile):
                os.remove (safile) # Delete original MMP file
                #bruce 050907 suspects this is never necessary, but not sure;
                # if true, it should be removed, so there is never a time with no file at that filename.
                # (#e In principle we could try just moving it first, and only if that fails, try removing and then moving.)

            os.rename( tmpname, safile) # Move tmp file to saved filename.
            
            if not savePartFiles:
                # Sometimes, we just want to save the MMP file and not worry about
                # any of the part's Part Files. For example, Open Babel just needs to
                # save a copy of the current MMP file in a temp directory for
                # translation purposes (see fileExport() and fileOpenBabelImport()). 
                # Mark 2007-06-05
                return
            
            errorcode, oldPartFilesDir = self.assy.find_or_make_part_files_directory(make = False) # Mark 060703.
            
            # If errorcode, print a history warning about it and then proceed as if the old Part Files directory is not there.
            if errorcode:
                env.history.message( orangemsg(oldPartFilesDir))
                oldPartFilesDir = None # So we don't copy it below.

            self.saved_main_file(safile, fil)

            if brag:
                env.history.message( "MMP file saved: [ " + os.path.normpath(self.assy.filename) + " ]" )
            # bruce 060704 moved this before copying part files,
            # which will now ask for permission before removing files,
            # and will start and end with a history message if it does anything.
            # wware 060802 - if successful, we may choose not to brag, e.g. during a
            # step of exporting a non-native file format

            # If it exists, copy the Part Files directory of the original part
            # (oldPartFilesDir) to the new name (i.e. "<safile> Files")
            if oldPartFilesDir: #bruce 060704 revised this code
                errorcode, errortext = self.copy_part_files_dir(oldPartFilesDir)
                    # Mark 060703. [only copies them if they exist]
                    #bruce 060704 will modify that function, e.g. to make it print
                    # a history message when it starts copying.
                if errorcode:
                    env.history.message( orangemsg("Problem copying part files: " + errortext ))
                else:
                    if debug_part_files:
                        env.history.message( _graymsg("debug: Success copying part files: " + errortext ))
            else:
                if debug_part_files:
                    env.history.message( _graymsg("debug: No part files to copy." ))
            
        return
    
    def copy_part_files_dir(self, oldPartFilesDir): # Mark 060703. NFR bug 2042. Revised by bruce 060704 for user safety, history.
        """
        Recursively copy the entire directory tree rooted at oldPartFilesDir to the assy's (new) Part Files directory.
        Return errorcode, message (message might be for error or for success, but is not needed for success except for debugging).
        Might also print history messages (and in future, maintain progress indicators) about progress.
        """
        set_waitcursor(True)
        if not oldPartFilesDir:
            set_waitcursor(False)
            return 0, "No part files directory to copy."
        
        errorcode, newPartFilesDir = self.assy.get_part_files_directory() # misnamed -- actually just gets its name
        if errorcode:
            set_waitcursor(False)
            return 1, "Problem getting part files directory name: " + newPartFilesDir
            
        if oldPartFilesDir == newPartFilesDir:
            set_waitcursor(False)
            return 0, "Nothing copied since the part files directory is the same."
        
        if os.path.exists(newPartFilesDir): 
            # Destination directory must not exist. copytree() will create it.
            # Assume the user was prompted and confirmed overwriting the MMP file, 
            # and thus its part files directory, so remove newPartFilesDir.
            
            #bruce 060704 revision -- it's far too dangerous to do this without explicit permission.
            # Best fix would be to integrate this permission with the one for overwriting the main mmp file
            # (which may or may not have been given at this point, in the current code --
            #  it might be that the newPartFilesDir exists even if the new mmp file doesn't).
            # For now, if no time for better code for A8, just get permission here. ###@@@
            if os.path.isdir(newPartFilesDir):
                if "need permission":
                    # ... confirm overwrite of the existing file. [code copied from another method above]
                    ret = QMessageBox.warning( self, "Warning!", ###k what is self.name()?
                        "The Part Files directory for the copied mmp file,\n[" + newPartFilesDir + "], already exists.\n"\
                        "Do you want to overwrite this directory, or skip copying the Part Files from the old mmp file?\n"\
                        "(If you skip copying them now, you can rename this directory and copy them using your OS;\n"\
                        "if you don't rename it, the copied mmp file will use it as its own Part Files directory.)",
                        "&Overwrite", "&Skip", "",
                        0,      # Enter == button 0
                        1 )     # Escape == button 1

                    if ret == 1: # The user wants to skip copying the part files
                        msg = "Not copying Part Files; preexisting Part Files directory at new name [%s] will be used unless renamed." % newPartFilesDir
                        env.history.message( orangemsg( msg ) )
                        return 0, "Nothing copied since user skipped overwriting existing part files directory"
                    else:
                        # even this could take a long time; and the user needs to have a record that we're doing it
                        # (in case they later realize it was a mistake).
                        msg = "Removing existing part files directory [%s]" % newPartFilesDir
                        env.history.message( orangemsg( msg ) )
                        env.history.h_update() # needed, since following op doesn't processEvents and might take a long time
                try:
                    shutil.rmtree(newPartFilesDir)
                except Exception, e:
                    set_waitcursor(False)
                    return 1, ("Problem removing an existing part files directory [%s]" % newPartFilesDir
                               + " - ".join(map(str, e.args)))
        
        # time to start copying; tell the user what's happening
        # [in future, ASAP, this needs to be abortable, and maybe have a progress indicator]
        ###e this ought to have a wait cursor; should grab code from e.g. SurfaceChunks
        msg = "Copying part files from [%s] to [%s]" % ( oldPartFilesDir, newPartFilesDir )
        env.history.message( msg )
        env.history.h_update() # needed
        
        try:
            shutil.copytree(oldPartFilesDir, newPartFilesDir)
        except Exception, e:
            eic.handle_exception() # BUG: Undefined variable eic (fyi, no handle_exception method is defined in NE1)
            set_waitcursor(False)
            return 1, ("Problem copying files to the new parts file directory " + newPartFilesDir
                       + " - ".join(map(str, e.args)))

        set_waitcursor(False)
        env.history.message( "Done.")
        return 0, 'Part files copied from "' + oldPartFilesDir + '" to "' + newPartFilesDir + '"'

    def saved_main_file(self, safile, fil): #bruce 050907 split this out of mmp and pdb saving code
        """
        Record the fact that self.assy itself is now saved into (the same or a new) main file
        (and will continue to be saved into that file, until further notice)
        (as opposed to part or all of it being saved into some separate file, with no change in status of main file).
        Do necessary changes (filename, window caption, assy.changed status) and updates, but emit no history message.
        """
        # (It's probably bad design of pdb save semantics for it to rename the assy filename -- it's more like saving pov, etc.
        #  This relates to some bug reports. [bruce 050907 comment])
        # [btw some of this should be split out into an assy method, or more precisely a savable-object method #e]
        self.assy.filename = safile
        self.assy.name = fil
        self.assy.reset_changed() # The file and the part are now the same.
        self.updateRecentFileList(safile)
            #bruce 050927 code cleanup: moved updateRecentFileList here (before, it preceded each call of this method)        
        self.update_mainwindow_caption()
        self.mt.mt_update() # since it displays self.assy.name [bruce comment 050907; a guess]
            # [note, before this routine was split out, the mt_update happened after the history message printed by our callers]
        return
        
    def prepareToCloseAndExit(self): #bruce 070618 revised/renamed #e SHOULD RENAME to not imply side effects other than file save
        """
        The user has asked NE1 to close the main window and exit; if any files are modified,
        ask the user whether to save them, discard them, or cancel the exit.
           If the user wants any files saved, save them. (In the future there might be more than one
        open file, and this would take care of them all, even though some but not all might get saved.)
           If the user still wants NE1 to exit, return True; otherwise (if user cancels exit at any
        time during this, using some dialog's Cancel button), return False.
           Perform no exit-related side effects other than possibly saving modified files.
        If such are needed, the caller should do them afterwards (see cleanUpBeforeExiting in current code)
        or before (not implemented as of 070618 in current code).
        """ 
        if not self.assy.has_changed():
            return True
        
        rc = QMessageBox.warning( self, "Warning!",
            "The part contains unsaved changes.\n"
            "Do you want to save the changes before exiting?",
            "&Save", "&Discard", "Cancel",
            0,      # Enter == button 0
            2 )     # Escape == button 2
        print "fyi: dialog choice =", ["Save", "Discard", "Cancel"][rc] # leave this in until changes fully tested [bruce 070618]
        
        if rc == 0: # Save (save file and exit)
            isFileSaved = self.fileSave()
            if isFileSaved:
                return True
            else:
                ##Huaicai 1/6/05: While in the "Save File" dialog, if user chooses
                ## "Cancel", the "Exit" action should be ignored. bug 300
                return False
        
        elif rc == 1: # Discard (discard file and exit)
            return True
        
        else: # Cancel (cancel exit, and don't save file)
            return False
        pass

    __last_closeEvent_cancel_done_time = 0.0 #bruce 070618 for bug 2444
    __exiting = False #bruce 070618 for bug 2444
    
    def closeEvent(self, ce):
        """
        Slot method for closing the main window (and exiting NE1), called via
        "File > Exit" or clicking the "Close" button on the window title.
        
        @param ce: The close event.
        @type  ce: U{B{QCloseEvent}<http://doc.trolltech.com/4/qcloseevent.html>}
        """
        # Note about bug 2444 and its fix here:
        #
        # For unknown reasons, Qt can send us two successive closeEvents.
        # This is part of the cause of bug 2444 (two successive dialogs asking
        # user whether to save changes).
        # The two events are not distinguishable in any way we [Bruce & Ninad] 
        # know of (stacktrace, value of ce.spontaneous()).
        # But there is no documented way to be sure they are the same
        # (their id is the same, but that doesn't mean much, since it's often
        # true even for different events of the same type; QCloseEvent has
        # no documented serial number or time; they are evidently different
        # PyQt objects, since a Python attribute saved in the first one (by 
        # debug code tried here) is no longer present in the second one).
        #
        # But, there is no correct bugfix except to detect whether they're
        # the same, because:
        # - if the user cancels an exit, then exits again (without doing 
        #   anything in between), they *should* get another save-changes dialog;
        # - the cause of getting two events per close is not known, so it
        #   might go away, so (in trying to handle that case) we can't just
        #   assume the next close event should be discarded.
        #
        # So all that's left is guessing whether they're the same, based on
        # intervening time. (This means comparing end time of handling one
        # event with start time of handling the next one, since getting the
        # cancel from the user can take an arbitrarily long time.)
        # (Of course if the user doesn't cancel, so we're really exiting, 
        # then we know they have to be the same.)
        #
        # But even once we detect the duplicate, we have to handle it
        # differently depending on whether we're exiting.
        # (Note: during development, a bug caused us to call neither 
        # ce.accept() nor ce.ignore() on the 2nd event, which in some cases
        # aborted the app with "Modules/gcmodule.c:231: failed assertion
        # `gc->gc.gc_refs != 0'".)

        now = time.time()
##        print "self.__exiting =", self.__exiting, ", now =", now, ", last done time =", self.__last_closeEvent_cancel_done_time
        
        if self.__exiting or (now - self.__last_closeEvent_cancel_done_time <= 0.5):
            # (I set the threshhold at 0.5 since the measured time difference was up to 0.12 during tests.)
            # Assume this is a second copy of the same event (see long comment above).
            # To fix bug 2444, don't do the same side effects for this event,
            # but accept or ignore it the same as for the first one (based on self.__exiting).
            duplicate = True
            shouldExit = self.__exiting # from prior event
            print "fyi: ignoring duplicate closeEvent (exiting = %r)" % shouldExit
                # leave this print statement in place until changes fully tested [bruce 070618]
        else:
            # normal case
            duplicate = False
            shouldExit = self.prepareToCloseAndExit() # puts up dialog if file might need saving

        if shouldExit:
            self.__exiting = True
            if not duplicate:
                print "exiting" # leave this in until changes fully tested [bruce 070618]
                self.cleanUpBeforeExiting()
            
            #Not doing the following in 'cleanupBeforeExiting? 
            #as it is not a 'clean up'. Adding it below for now --ninad 20070702
            
            #Note: saveState() is QMainWindow.saveState(). It saves the 
            #current state of this mainwindow's toolbars and dockwidgets
            #The 'objectName' property is used to identify each QToolBar 
            #and QDockWidget. 
            #QByteArray QMainWindow::saveState ( int version = 0 ) const
            toolbarState_QByteArray = self.saveState()
            
            env.prefs[toolbar_state_prefs_key] = str(toolbarState_QByteArray)
            ce.accept()
        else:
            ce.ignore()
            if not duplicate:
                env.history.message("Cancelled exit.")
            self.__last_closeEvent_cancel_done_time = time.time() # note: not the same value as the time.time() call above
##            print "done time =",self.__last_closeEvent_cancel_done_time
        return

    def fileClose(self):
        """
        Slot method for 'File > Close'.
        """
        env.history.message(greenmsg("Close File:"))
        
        isFileSaved = True
        warn_about_abandoned_changes = True # see similar code in fileOpen
        if self.assy.has_changed():
            ret = QMessageBox.warning( self, "Warning!" ,
                "The model contains unsaved changes.\n"
                "Do you want to save the changes before closing\n"\
                "this model and beginning a new (empty) model?",
                "&Save", "&Discard", "Cancel",
                0,      # Enter == button 0
                2 )     # Escape == button 2
            
            if ret == 0:
                # Save clicked or Alt+S pressed or Enter pressed
                isFileSaved = self.fileSave()
            elif ret == 1:
                # Discard
                env.history.message("Changes discarded.")
                warn_about_abandoned_changes = False
            elif ret == 2:
                # Cancel clicked or Alt+C pressed or Escape pressed
                env.history.message("Cancelled.")
                return
            else:
                assert 0 #bruce 080909
        
        if isFileSaved:
            self._make_and_init_assy('$STARTUP_MODE',
                   warn_about_abandoned_changes = warn_about_abandoned_changes )
            self.assy.reset_changed() #bruce 050429, part of fixing bug 413
            self.assy.clear_undo_stack() #bruce 060126, maybe not needed, or might fix an unreported bug related to 1398
            self.win_update()
        return

    def fileSetWorkingDirectory(self):
        """
        Slot for 'File > Set Working Directory', which prompts the user to
        select a new NE1 working directory via a directory chooser dialog.
        
        @deprecated: The 'Set Working Directory' menu item that calls this slot
        has been removed from the File menu as of Alpha 9.  Mark 2007-06-18.
        """
        env.history.message(greenmsg("Set Working Directory:"))
    
        workdir = env.prefs[workingDirectory_prefs_key]
        wdstr = "Current Working Directory - [" + workdir  + "]"
        workdir = QFileDialog.getExistingDirectory( self, wdstr, workdir )
        
        if not workdir:
            env.history.message("Cancelled.")
            return
        
        self.setCurrentWorkingDirectory(workdir)
        
    def setCurrentWorkingDirectory(self, dir = None): # Mark 060729.
        """
        Set the current working directory (CWD). 
        
        @param dir: The working directory. If I{dir} is None (the default), the
                    CWD is set to the directory of the current assy filename
                    (i.e. the directory of the current part). If there is no 
                    current assy filename, the CWD is set to the default
                    working directory.
        @type  dir: string
        
        @see: L{getDefaultWorkingDirectory()}
        """
        if not dir:
            dir, fil = os.path.split(self.assy.filename)
        
        if os.path.isdir(dir):
            self.currentWorkingDirectory = dir
            self._setWorkingDirectoryInPrefsDB(dir)
        else:
            self.currentWorkingDirectory =  getDefaultWorkingDirectory()
            
        #print "setCurrentWorkingDirectory(): dir=",dir
        
    def _setWorkingDirectoryInPrefsDB(self, workdir = None):
        """
        [private method]
        Set the working directory in the user preferences database.
        
        @param workdir: The fullpath directory to write to the user pref db.
        If I{workdir} is None (default), there is no change.
        @type  workdir: string
        """
        if not workdir:
            return
        
        workdir = str(workdir)
        if os.path.isdir(workdir):
            workdir = os.path.normpath(workdir)
            env.prefs[workingDirectory_prefs_key] = workdir # Change pref in prefs db.            
        else:
            msg = "[" + workdir + "] is not a directory. Working directory was not changed."
            env.history.message( redmsg(msg))
        return
    
    def _make_and_init_assy(self,
                            initial_mode_symbol = None,
                            warn_about_abandoned_changes = True ):
        """
        [private; as of 080812, called only from fileOpen and fileClose]

        Close current self.assy, make a new assy and reinit commandsequencer
        for it (in glpane.setAssy), tell new assy about our model tree and
        glpane (and vice versa), update mainwindow caption.

        @param initial_mode_symbol: if provided, initialize the command
                                    sequencer to that mode; otherwise,
                                    to nullMode. All current calls provide
                                    this as a "symbolic mode name".

        @param warn_about_abandoned_changes: passed to exit_all_commands method in
                                             self.assy.commandSequencer; see that
                                             method in class CommandSequencer for
                                             documentation
        @type warn_about_abandoned_changes: boolean
                                          
        @note: MWsemantics.__init__ doesn't call this, but contains similar
               code, not all in one place. It's not clear whether it could
               be made to call this.

        @note: certain things are done shortly after this call by all callers,
               and by the similar MWsemantics.__init__ code, but since various
               things intervene it's not clear whether they could be pulled
               into a single method. These include assy.clear_undo_stack.
        """
        #bruce 080812 renamed this from __clear (which is very old).
        # REVIEW: should all or part of this method be moved back into
        # class MWsemantics (which mixes it in)?
        
        if self.assy:
            cseq = self.assy.commandSequencer
            cseq.exit_all_commands( warn_about_abandoned_changes = \
                                    warn_about_abandoned_changes )            
                #bruce 080909 new features:
                # 1. exit all commands here, rather than (or in addition to)
                # when initing new assy.
                # 2. but tell that not to warn about abandoning changes
                # stored in commands, if user already said to discard changes
                # stored in assy (according to caller passing False for warn_about_abandoned_changes).
                # This should fix an old bug in which redundant warnings
                # would be given if both kinds of changes existed.
            self.assy.close_assy() # bruce 080314
        
        self.assy = self._make_a_main_assy()
        self.update_mainwindow_caption()
        self.glpane.setAssy(self.assy)
            # notes: this calls assy.set_glpane, and _reinit_modes
            # (which leaves currentCommand as nullmode)
            # (even after USE_COMMAND_STACK).
            ### TODO: move _reinit_modes out of that, do it somewhere else.
        self.assy.set_modelTree(self.mt)
        
        self.mt.mt_update() # not sure if needed

        if initial_mode_symbol:
            #bruce 080812 pulled this code in from just after both calls
            self.commandSequencer.start_using_initial_mode( initial_mode_symbol)
        
        return

    def openRecentFile(self, idx):
        """
        Slot method for the "Open Recent File" menu, 
        a submenu of the "File" menu.
        """
        text = str_or_unicode(idx.text())
        selectedFile = text[text.index("  ") + 2:] 
            # Warning: Potential bug if number of recent files >= 10
            # (i.e. LIST_CAPACITY >= 10)
        self.fileOpen(selectedFile)
        return

    pass # end of class fileSlotsMixin

# ==

## Test code -- By cleaning the recent files list of QSettings
if __name__ == '__main__':
    prefs = QSettings()
    from utilities.constants import RECENTFILES_QSETTINGS_KEY
    emptyList = QStringList()
    prefs.writeEntry(RECENTFILES_QSETTINGS_KEY, emptyList)
        # todo: make a user-accessible way to erase the recent files list.
        # [bruce 080727 suggestion]
    
    del prefs

# end

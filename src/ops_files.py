# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
'''
ops_files.py provides fileSlotsMixin for MWsemantics,
with file slot methods and related helper methods.

$Id$

Note: most other ops_*.py files provide mixin classes for Part,
not for MWsemantics like this one.

History:

bruce 050907 split this out of MWsemantics.py.
[But it still needs major cleanup and generalization.]

bruce 050913 used env.history in some places.

mark 060730 removed unsupported slot method fileNew(); refined and added missing docstrings
'''

from qt import QFileDialog, QMessageBox, QString, qApp, QSettings
from assembly import assembly
import os, shutil
import platform

from fileIO import * # this might be needed for some of the many other modules it imports; who knows? [bruce 050418 comment]
    # (and it's certainly needed for the functions it defines, e.g. writepovfile.)
from files_pdb import readpdb, insertpdb, writepdb
from files_gms import readgms, insertgms
from files_mmp import readmmp, insertmmp, fix_assy_and_glpane_views_after_readmmp
from debug import print_compact_traceback

from HistoryWidget import greenmsg, redmsg, orangemsg, _graymsg

import preferences
import env

def set_waitcursor(on_or_off):
    """For on_or_off True, set the main window waitcursor.
    For on_or_off False, revert to the prior cursor.
    [It might be necessary to always call it in matched pairs, I don't know [bruce 050401]. #k]
    """
    if on_or_off:
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
    else:
        QApplication.restoreOverrideCursor() # Restore the cursor
    return

debug_part_files = False #&&& Debug prints to history. Change to False after QA. Mark 060703 [revised by bruce 060704]

def fileparse(name): #bruce 050413 comment: see also filesplit and its comments.
    # This has known bugs (e.g. for basename containing two dots);
    # should be revised to use os.path.split and splitext. ###@@@
    """breaks name into directory, main name, and extension in a tuple.
    fileparse('~/foo/bar/gorp.xam') ==> ('~/foo/bar/', 'gorp', '.xam')
    """
    dir, x = os.path.split(name)
    fil, ext = os.path.splitext(x)
    return dir + os.path.sep, fil, ext

class fileSlotsMixin: #bruce 050907 moved these methods out of class MWsemantics
    "Mixin class to provide file-related methods for class MWsemantics. Has slot methods and their helper methods."

    def fileImport(self): # Code copied from fileInsert() slot method. Mark 060731. 
        """Slot method for 'File > Import'.
        """
        cmd = greenmsg("Import File: ")
        
        # This format list generated from the Open Babel wiki page: 
        # http://openbabel.sourceforge.net/wiki/Babel#File_Formats
        formats = \
            "All Files (*.*);;"\
            "Molecular Machine Part (*.mmp);;"\
            "Accelrys/MSI Biosym/Insight II CAR (*.car);;"\
            "Alchemy (*.alc, *.mol);;"\
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
            "YASARA.org YOB (*.yob)"
        
        fn = QFileDialog.getOpenFileName(self.currentWorkingDirectory,
                formats,
                self,
                "Import File dialog",
                "Select file to Import" )
                
        if not fn:
             env.history.message(cmd + "Cancelled")
             return
        
        if fn:
            fn = str(fn)
            if not os.path.exists(fn):
                #bruce 050415: I think this should never happen;
                # in case it does, I added a history message (to existing if/return code).
                env.history.message( redmsg( "File not found: [ " + fn+ " ]") )
                return

            # Anything that isn't an MMP file, we will import with Open Babel.
            # Its coverage of MMP files is imperfect so it makes mistakes, but
            # it would be good to use it enough to find those mistakes.

            if fn[-3:] == "mmp":
                try:
                    insertmmp(self.assy, fn)
                except:
                    print_compact_traceback( "MWsemantics.py: fileInsert(): error inserting MMP file [%s]: " % fn )
                    env.history.message( redmsg( "Internal error while inserting MMP file: [ " + fn+" ]") )
                else:
                    self.assy.changed() # The file and the part are not the same.
                    env.history.message( cmd + "MMP file inserted: [ " + os.path.normpath(fn) + " ]" ) # fix bug 453 item. ninad060721

#           elif fn[-3:] in ["pdb","PDB"]:
#               try:
#                   insertpdb(self.assy, fn)
#               except:
#                   print_compact_traceback( "MWsemantics.py: fileInsert(): error inserting PDB file [%s]: " % fn )
#                   env.history.message( redmsg( "Internal error while inserting PDB file: [ " + fn + " ]") )
#               else:
#                   self.assy.changed() # The file and the part are not the same.
#                   env.history.message( cmd + "PDB file inserted: [ " + os.path.normpath(fn) + " ]" )

            else:
                dir, fil, ext = fileparse(fn)
                tmpdir = platform.find_or_make_Nanorex_subdir('temp')
                mmpfile = os.path.join(tmpdir, fil + ".mmp")
                result = self.runBabel(fn, mmpfile)
                if result:
                    insertmmp(self.assy, mmpfile)
                    # Theoretically, we have successfully imported the file at this point.
                    # But there might be a warning from insertmmp.
                else:
                    print 'Problem:', fn, '->', mmpfile
                    env.history.message(redmsg("File translation failed."))
            self.glpane.scale = self.assy.bbox.scale()
            self.glpane.gl_update()
            self.mt.mt_update()
            
            # Update the current working directory (CWD).
            dir, fil = os.path.split(fn)
            self.setCurrentWorkingDirectory(dir)
            
    def fileExport(self): # Code copied from fileInsert() slot method. Mark 060731. 
        """Slot method for 'File > Export'.
        """
        if platform.atom_debug:
            from debug import linenum
            linenum()
            print 'start fileExport()'
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

        formats = \
            "All Files (*.*);;"\
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
            "Chemical Resource Kit diagram format (2D) (*.crk2d);;"\
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
            "Compares first molecule to others using InChI. (*.k);;"\
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
            "YASARA.org YOB format (*.yob);;"\
            "ZINDO input format (*.zin);;"

            ## Don't use OpenBabel for MDL, otherwise it would look like this

        fn = QFileDialog.getSaveFileName(self.currentWorkingDirectory,
                formats,
                self,
                "Export File dialog",
                "Select file to Export" )
        if platform.atom_debug:
            linenum()
            print 'fn', repr(str(fn))

        if not fn:
            env.history.message(cmd + "Cancelled")
            if platform.atom_debug:
                linenum()
                print 'fileExport cancelled because fn is no good'
            return
        
        fn = str(fn)
        dir, fil, ext = fileparse(fn)
        if ext == ".mmp":
            self.save_mmp_file(fn, brag=True)
        else:
            # Anything that isn't an MMP file, we will export with Open Babel.
            # Its coverage of MMP files is imperfect so it makes mistakes, but
            # it would be good to use it enough to find those mistakes.
            import time
            from qt import QStringList, QProcess
            dir, fil, ext = fileparse(fn)
            if platform.atom_debug:
                linenum()
                print 'dir, fil, ext', repr(dir), repr(fil), repr(ext)
            tmpdir = platform.find_or_make_Nanorex_subdir('temp')
            mmpfile = os.path.join(tmpdir, fil + ".mmp")
            if platform.atom_debug:
                linenum()
                print 'tmpdir, mmpfile', repr(tmpdir), repr(mmpfile)
            self.saveFile(mmpfile, brag=False)
            result = self.runBabel(mmpfile, fn)
            if result and os.path.exists(fn):
                if platform.atom_debug:
                    linenum()
                    print 'file translation OK'
                env.history.message( "File exported: [ " + fn + " ]" )
            else:
                if platform.atom_debug:
                    linenum()
                    print 'file translation failed'
                print 'Problem:', mmpfile, '->', fn
                env.history.message(redmsg("File translation failed."))

        self.glpane.scale = self.assy.bbox.scale()
        self.glpane.gl_update()
        self.mt.mt_update()

        # Update the current working directory (CWD).
        dir, fil = os.path.split(fn)
        if platform.atom_debug:
            linenum()
            print 'fileExport changing working directory to %s' % repr(dir)
        self.setCurrentWorkingDirectory(dir)
        if platform.atom_debug:
            linenum()
            print 'finish fileExport()'

    def runBabel(self, infile, outfile):
        if platform.atom_debug:
            print 'start runBabel(%s, %s)' % (repr(infile), repr(outfile))
        import time
        from qt import QStringList, QProcess
        arguments = QStringList()
        if sys.platform == 'win32':
            program = 'babel.exe'
        else:
            program = 'babel'
        i = 0
        for arg in [program, infile, outfile]:
            if platform.atom_debug:
                print 'argument', i, repr(arg)
            i += 1
            arguments.append(arg)
        proc = QProcess()
        proc.setArguments(arguments)
        text = [ None ]
        def blaberr(text=text):
            text[0] = str(proc.readStderr())
        QObject.connect(proc, SIGNAL("readyReadStderr()"), blaberr)
        proc.start()
        while 1:
            if proc.isRunning():
                if platform.atom_debug:
                    print "still running"
                    time.sleep(1)
                else:
                    time.sleep(0.1)
            else:
                break
        exitStatus = proc.exitStatus()
        stderr = text[0]
        if platform.atom_debug:
            print 'exit status', exitStatus
            print 'stderr says', repr(stderr)
            print 'finish runBabel(%s, %s)' % (repr(infile), repr(outfile))
        return exitStatus == 0 and stderr == "1 molecule converted\n"

    def fileInsert(self):
        """Slot method for 'File > Insert'.
        """
        env.history.message(greenmsg("Insert File:"))
        
        formats = \
                    "Molecular Machine Part (*.mmp);;"\
                    "Protein Data Bank (*.pdb);;"\
                    "GAMESS (*.out);;"\
                    "All Files (*.*)"
        
        fn = QFileDialog.getOpenFileName(self.currentWorkingDirectory,
                formats,
                self,
                "Insert File dialog",
                "Select file to insert" ) # This is the caption for the dialog.  Fixes bug 1125. Mark 051116.
                
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
                    insertmmp(self.assy, fn)
                except:
                    print_compact_traceback( "MWsemantics.py: fileInsert(): error inserting MMP file [%s]: " % fn )
                    env.history.message( redmsg( "Internal error while inserting MMP file: [ " + fn+" ]") )
                else:
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
            
            if fn[-3:] in ["out","OUT"]:
                try:
                    r = insertgms(self.assy, fn)
                except:
                    print_compact_traceback( "MWsemantics.py: fileInsert(): error inserting GAMESS OUT file [%s]: " % fn )
                    env.history.message( redmsg( "Internal error while inserting GAMESS OUT file: [ " + fn + " ]") )
                else:
                    if r:
                        env.history.message( redmsg("File not inserted."))
                    else:
                        self.assy.changed() # The file and the part are not the same.
                        env.history.message( "GAMESS file inserted: [ " + os.path.normpath(fn) + " ]" )
                    
                    
            self.glpane.scale = self.assy.bbox.scale()
            self.glpane.gl_update()
            self.mt.mt_update()
            
            # Update the current working directory (CWD). Mark 060729.
            dir, fil = os.path.split(fn)
            self.setCurrentWorkingDirectory(dir)


    def fileOpen(self, recentFile = None):
        """Slot method for 'File > Open'.
        By default, users open a file through 'Open File' dialog. If <recentFile> is provided, it means user
        is opening a file named <recentFile> through the 'Recent Files' menu list. The file may or may not exist.
        """
        env.history.message(greenmsg("Open File:"))
        
        mmkit_was_hidden = self.hide_MMKit_during_open_or_save_on_MacOS() # Fixes bug 1744. mark 060325
        
        if self.assy.has_changed():
            ret = QMessageBox.warning( self, self.name(),
                "The part contains unsaved changes.\n"
                "Do you want to save the changes before opening a new part?",
                "&Save", "&Discard", "Cancel",
                0,      # Enter == button 0
                2 )     # Escape == button 2
            
            if ret==0: # Save clicked or Alt+S pressed or Enter pressed.
                ##Huaicai 1/6/05: If user canceled save operation, return 
                ## without letting user open another file
                if not self.fileSave():
                    if mmkit_was_hidden: self.glpane.mode.MMKit.show() # Fixes bug 1744. mark 060325
                    return
                
            ## Huaicai 12/06/04. Don't clear it, user may cancel the file open action    
            elif ret==1: pass#self.__clear() 
            
            elif ret==2: 
                env.history.message("Cancelled.")
                if mmkit_was_hidden: self.glpane.mode.MMKit.show() # Fixes bug 1744. mark 060325
                return # Cancel clicked or Alt+C pressed or Escape pressed

        if recentFile:
            if not os.path.exists(recentFile):
              QMessageBox.warning( self, self.name(),
                "The file [ " + recentFile + " ] doesn't exist any more.", QMessageBox.Ok, QMessageBox.NoButton)
              if mmkit_was_hidden: self.glpane.mode.MMKit.show() # Fixes bug 1744. mark 060325
              return
            
            fn = recentFile
        else:
            formats = \
                    "Molecular Machine Part (*.mmp);;"\
                    "Protein Data Bank (*.pdb);;"\
                    "All Files (*.*)"
            
            fn = QFileDialog.getOpenFileName(self.currentWorkingDirectory,
                    formats,
                    self ) #fixes bug 316 ninad060724
                    
            if not fn:
                env.history.message("Cancelled.")
                if mmkit_was_hidden: self.glpane.mode.MMKit.show() # Fixes bug 1744. mark 060325
                return
        
        if fn:
            self._updateRecentFileList(fn)

            self.__clear() # leaves glpane.mode as nullmode, as of 050911
            self.glpane.start_using_mode( '$DEFAULT_MODE') #bruce 050911 [now needed here, to open files in default mode]
                
            fn = str(fn)
            if not os.path.exists(fn):
                if mmkit_was_hidden: self.glpane.mode.MMKit.show() # Fixes bug 1744. mark 060325
                return

            #k Can that return ever happen? Does it need an error message?
            # Should preceding clear and modechange be moved down here??
            # (Moving modechange even farther below would be needed,
            #  if we ever let the default mode be one that cares about the
            #  model or viewpoint when it's entered.)
            # [bruce 050911 questions]

            isMMPFile = False
            if fn[-3:] == "mmp":
                readmmp(self.assy,fn)
                    #bruce 050418 comment: we need to check for an error return
                    # and in that case don't clear or have other side effects on assy;
                    # this is not yet perfectly possible in readmmmp.
                env.history.message("MMP file opened: [ " + os.path.normpath(fn) + " ]")
                isMMPFile = True
                
            if fn[-3:] in ["pdb","PDB"]:
                readpdb(self.assy,fn)
                env.history.message("PDB file opened: [ " + os.path.normpath(fn) + " ]")

            dir, fil, ext = fileparse(fn)
            ###@@@e could replace some of following code with new method just now split out of saved_main_file [bruce 050907 comment]
            self.assy.name = fil
            self.assy.filename = fn
            self.assy.reset_changed() # The file and the part are now the same

#            self.setCaption(self.trUtf8(self.name() + " - " + "[" + self.assy.filename + "]"))
            self.update_mainwindow_caption()

            if isMMPFile:
                #bruce 050418 moved this code into a new function in files_mmp.py
                # (but my guess is it should mostly be done by readmmp itself)
                fix_assy_and_glpane_views_after_readmmp( self.assy, self.glpane)
            else: ###PDB or other file format        
                self.setViewFitToWindow()

            self.assy.clear_undo_stack() #bruce 060126, fix bug 1398

            self.glpane.gl_update_duration(new_part=True) #mark 060116.
            
            self.mt.mt_update()

        if mmkit_was_hidden: self.glpane.mode.MMKit.show() # Fixes bug 1744. mark 060325
        
        self.setCurrentWorkingDirectory()
        
        return

    def fileSave(self):
        """Slot method for 'File > Save'.
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
        """Slot method for 'File > Save As'.
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

    def fileSaveAs_filename(self, images_ok = True):
        #bruce 050927 split this out of fileSaveAs, added some comments, added images_ok option
        """Ask user to choose a save-as filename (and file type) based on the current main filename.
        If file exists, ask them if they want to overwrite that file.
        If user cancels either dialog, or if some error occurs,
        emit a history message and return None.
        Otherwise return the file name to save to, as a Python string.
           If images_ok is false, don't offer the image formats as possible choices for filetype.
        This is needed due to limits in how callers save these image formats
        (and that also determines the set of image formats excluded by this option).
        """
        # figure out sdir, sfilter from existing filename
        if self.assy:
            if self.assy.filename:
                # Below, sdir is the filename minus the extension. This way only the basename is displayed
                # in the QFileDialog. This is a workaround for bug 225. 
                # Normally, we'd like to include the extension so that it is included in the filename field of
                # the QFileDialog, but when the user changes the filter (i.e. *.mmp to *.pdb), the extension
                # in the filename field does not get updated to match the selected filter. Mark 060730.
                sdir, ext = os.path.splitext(self.assy.filename)
                #sdir = self.assy.filename # Keeping this here in case there is strong disagreement. Mark 060730.
            else: 
                # Marked for removal since <dir> and <fil> are not used. Mark 060730.
                #&&& dir, fil = "./", self.assy.name
                ext = ".mmp"
                sdir = self.currentWorkingDirectory # Make sure the file chooser dialog opens to the CWD. Mark 060730.
        else:
            env.history.message( "Save Ignored: Part is currently empty." )
            return None

        if ext == ".pdb": 
            sfilter = QString("Protein Data Bank (*.pdb)")
        else: 
            sfilter = QString("Molecular Machine Part (*.mmp)")

        # ask user for new filename (and file type); they might cancel; fn will be a QString
        # The Animation Master MDL format was removed in version 1.47 to fix bug 1508. I am
        # putting it back after email discussion with Mark.  - wware 060804
        formats = \
                    "Molecular Machine Part (*.mmp);;"\
                    "Protein Data Bank (*.pdb);;"\
                    "POV-Ray (*.pov);;"\
                    "Animation Master Model (*.mdl);;"
                    
        if images_ok:
            formats += \
                    "JPEG (*.jpg);;"\
                    "Portable Network Graphics (*.png)"

        mmkit_was_hidden = self.hide_MMKit_during_open_or_save_on_MacOS() # Fixes bug 1744. mark 060325
        
        fn = QFileDialog.getSaveFileName(sdir, 
                    formats,
                    self, 
                    None,
                    "Save As",
                    sfilter)

        if fn:
            fn = str(fn)
            # figure out name of new file, safile [bruce question: when and why can this differ from fn?]
            dir, fil, ext2 = fileparse(fn)
            del fn #bruce 050927
            ext =str(sfilter[-5:-1]) # Get "ext" from the sfilter. It *can* be different from "ext2"!!! - Mark
            safile = dir + fil + ext # full path of "Save As" filename

            # ask user before overwriting an existing file (other than this part's main file)
            if self.assy.filename != safile: # If the current part name and "Save As" filename are not the same...
                if os.path.exists(safile): # ...and if the "Save As" file exists...

                    # ... confirm overwrite of the existing file.
                    ret = QMessageBox.warning( self, self.name(),
                        "The file \"" + fil + ext + "\" already exists.\n"\
                        "Do you want to overwrite the existing file or cancel?",
                        "&Overwrite", "&Cancel", None,
                        0,      # Enter == button 0
                        1 )     # Escape == button 1

                    if ret==1: # The user cancelled
                        env.history.message( "Cancelled.  Part not saved." )
                        if mmkit_was_hidden: self.glpane.mode.MMKit.show() # Fixes bug 1744. mark 060325
                        return None # Cancel clicked or Alt+C pressed or Escape pressed

            ###e bruce comment 050927: this might be a good place to test whether we can write to that filename,
            # so if we can't, we can let the user try choosing one again, within this method.
            # But we shouldn't do this if it's the main filename, to avoid erasing that file now.
            # (If we only do this test with each function
            # that writes into the file, then if that fails it'll more likely require user to redo the entire op.)
            
            if mmkit_was_hidden: self.glpane.mode.MMKit.show() # Fixes bug 1744. mark 060325
                        
            return safile
            
        else:
            if mmkit_was_hidden: self.glpane.mode.MMKit.show() # Fixes bug 1744. mark 060325
            
            return None ## User canceled.

    def fileSaveSelection(self): #bruce 050927
        """Slot method for 'File > Save Selection'.
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

    def saveFile(self, safile, brag=True):
        """Save the current model. <safile> is the filename to save the part under.
        """
        
        dir, fil, ext = fileparse(safile)
            #e only ext needed in most cases here, could replace with os.path.split [bruce 050907 comment]
                    
        if ext == ".mmp" : # Write MMP file.
            self.save_mmp_file(safile, brag=brag)
            self.setCurrentWorkingDirectory() # Update the CWD.

        elif ext == ".pdb": # Write PDB file.
            try:
                writepdb(self.assy.part, safile) #bruce 050927 revised arglist
            except:
                print_compact_traceback( "MWsemantics.py: saveFile(): error writing file %r: " % safile )
                env.history.message(redmsg( "Problem saving PDB file: [ " + safile + " ]" ))
            else:
                self.saved_main_file(safile, fil)
                    #bruce 050907 split out this common code, though it's probably bad design for PDB files (as i commented elsewhere)
                env.history.message( "PDB file saved: [ " + os.path.normpath( self.assy.filename) +" ]" )
                    #bruce 050907 moved this after mt_update (which is now in saved_main_file)
                self.setCurrentWorkingDirectory() # Update the CWD.
        else:
            self.savePartInSeparateFile( self.assy.part, safile)
        return

    def savePartInSeparateFile( self, part, safile): #bruce 050927 added part arg, renamed method
        """Save some aspect of part (which might or might not be self.assy.part) in a separate file, named safile,
        without resetting self.assy's changed flag or filename. For some filetypes, use display attributes from self.glpane.
        For JPG and PNG, assert part is the glpane's current part, since current implem only works then.
        """
        #e someday this might become a method of a "saveable object" (open file) or a "saveable subobject" (part, selection).
        from debug import linenum
        linenum()
        dir, fil, ext = fileparse(safile)
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
                ###e we need variant of writemmpfile_assy, but the viewdata will differ... pass it a map from partindex to part?
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

    def save_mmp_file(self, safile, brag=True):
        # bruce 050907 split this out of saveFile; maybe some of it should be moved back into caller ###@@@untested
        """Save the current part as a MMP file under the name <safile>.
        If we are saving a part (assy) that already exists and it has an (old) Part Files directory, 
        copy those files to the new Part Files directory (i.e. '<safile> Files').
        """
        dir, fil, extjunk = fileparse(safile)
        try:
            tmpname = os.path.join(dir, '~' + fil + '.m~')
            self.assy.writemmpfile(tmpname)
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
            
            errorcode, oldPartFilesDir = self.assy.find_or_make_part_files_directory(make = False) # Mark 060703.
            
            # If errorcode, print a history warning about it and then proceed as if the old Part Files directory is not there.
            if errorcode:
                env.history.message( orangemsg(oldPartFilesDir))
                oldPartFilesDir = None # So we don't copy it below.

            self.saved_main_file(safile, fil)

            if brag: env.history.message( "MMP file saved: [ " + os.path.normpath(self.assy.filename) + " ]" )
            # bruce 060704 moved this before copying part files,
            # which will now ask for permission before removing files,
            # and will start and end with a history message if it does anything.
            # wware 060802 - if successful, we may choose not to brag, e.g. during a
            # step of exporting a non-native file format

            # If it exists, copy the Part Files directory of the original part (oldPartFilesDir) to the new name (i.e. "<safile> Files")
            if oldPartFilesDir: #bruce 060704 revised this code
                errorcode, errortext = self.copy_part_files_dir(oldPartFilesDir) # Mark 060703. [only copies them if they exist]
                    #bruce 060704 will modify that function, e.g. to make it print a history message when it starts copying.
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
        """Recursively copy the entire directory tree rooted at oldPartFilesDir to the assy's (new) Part Files directory.
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
                    ret = QMessageBox.warning( self, self.name(), ###k what is self.name()?
                        "The Part Files directory for the copied mmp file,\n[" + newPartFilesDir + "], already exists.\n"\
                        "Do you want to overwrite this directory, or skip copying the Part Files from the old mmp file?\n"\
                        "(If you skip copying them now, you can rename this directory and copy them using your OS;\n"\
                        "if you don't rename it, the copied mmp file will use it as its own Part Files directory.)",
                        "&Overwrite", "&Skip", None,
                        0,      # Enter == button 0
                        1 )     # Escape == button 1

                    if ret==1: # The user wants to skip copying the part files
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
            eic.handle_exception()
            set_waitcursor(False)
            return 1, ("Problem copying files to the new parts file directory " + newPartFilesDir
                       + " - ".join(map(str, e.args)))

        set_waitcursor(False)
        env.history.message( "Done.")
        return 0, 'Part files copied from "' + oldPartFilesDir + '" to "' + newPartFilesDir + '"'

    def saved_main_file(self, safile, fil): #bruce 050907 split this out of mmp and pdb saving code
        """Record the fact that self.assy itself is now saved into (the same or a new) main file
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
#                self.setCaption(self.trUtf8(self.name() + " - " + "[" + self.assy.filename + "]"))
        self._updateRecentFileList(safile)
            #bruce 050927 code cleanup: moved _updateRecentFileList here (before, it preceded each call of this method)        
        self.update_mainwindow_caption()
        self.mt.mt_update() # since it displays self.assy.name [bruce comment 050907; a guess]
            # [note, before this routine was split out, the mt_update happened after the history message printed by our callers]
        return
        
    def prepareToClose(self): #bruce 050907 split this out of MWsemantics.closeEvent method, added docstring
        """Prepare to close the main window and exit (e.g. ask user whether to save file if necessary).
        If user cancels, or anything else means we should not actually close and exit,
        return False; otherwise return True.
        """
        # wware 060406 bug 1263 - signal the simulator that we are exiting
        from runSim import SimRunner
        if not self.assy.has_changed():
            SimRunner.PREPARE_TO_CLOSE = True
            return True
        else:
            rc = QMessageBox.warning( self, self.name(),
                "The part contains unsaved changes.\n"
                "Do you want to save the changes before exiting?",
                "&Save", "&Discard", "Cancel",
                0,      # Enter == button 0
                2 )     # Escape == button 2

            if rc == 0:
                # Save
                isFileSaved = self.fileSave() # Save clicked or Alt+S pressed or Enter pressed.
                ##Huaicai 1/6/05: While in the "Save File" dialog, if user chooses
                ## "Cancel", the "Exit" action should be ignored. bug 300
                if isFileSaved:
                    SimRunner.PREPARE_TO_CLOSE = True
                    return True
                else:
                    return False
            elif rc == 1: # Discard
                SimRunner.PREPARE_TO_CLOSE = True
                return True
            else: # Cancel
                return False
        pass
            
    def closeEvent(self,ce): #bruce 050907 split this into two methods, revised docstring
        """slot method, called via File > Exit or clicking X titlebar button"""
        #bruce 090507 comment: this slot method should be moved back to MWsemantics.py.
        shouldEventBeAccepted = self.prepareToClose()
        if shouldEventBeAccepted:
            self.cleanUpBeforeExiting() #bruce 060127 added this re bug 1412 (defined in MWsemantics)
            ce.accept()
            ##self.periodicTable.close()
        else:
            ce.ignore()
            env.history.message("Cancelled exit.") # bruce 050907 added this message
        return

    def fileClose(self):
        """Slot method for 'File > Close'.
        """
        
        env.history.message(greenmsg("Close File:"))
        
        isFileSaved = True
        if self.assy.has_changed():
            ret = QMessageBox.warning( self, self.name(),
                "The part contains unsaved changes.\n"
                "Do you want to save the changes before closing this part?",
                "&Save", "&Discard", "Cancel",
                0,      # Enter == button 0
                2 )     # Escape == button 2
            
            if ret==0: isFileSaved = self.fileSave() # Save clicked or Alt+S pressed or Enter pressed.
            elif ret==1:
                env.history.message("Changes discarded.")
            elif ret==2: 
                env.history.message("Cancelled.")
                return # Cancel clicked or Alt+C pressed or Escape pressed
        
        if isFileSaved: 
                self.__clear() # leaves glpane.mode as nullmode, as of 050911
                self.glpane.start_using_mode( '$STARTUP_MODE') #bruce 050911: File->Clear sets same mode as app startup does
                self.assy.reset_changed() #bruce 050429, part of fixing bug 413
                self.assy.clear_undo_stack() #bruce 060126, maybe not needed, or might fix an unreported bug related to 1398
                self.win_update()
        return
    
    def setCurrentWorkingDirectory(self, dir=None): # Mark 060729.
        """Sets the current working directory (CWD) to <dir>. If <dir> is None, the CWD is set
        to the directory of the current assy filename (i.e. the directory of the current part). 
        If <dir> is None and there is no current assy filename, set the CWD to the default working directory.
        """
        if not dir:
            dir, fil = os.path.split(self.assy.filename)
        
        if os.path.isdir(dir):
            self.currentWorkingDirectory = dir
        else:
            self.currentWorkingDirectory =  getDefaultWorkingDirectory()
            
        #print "setCurrentWorkingDirectory(): dir=",dir

    def fileSetWorkDir(self):
        """Slot for 'File > Set Working Directory', which sets the working directory preference.
        If there is no open part, the CWD will be changed to the directory chosen by the user.
        """

        env.history.message(greenmsg("Set Working Directory:"))
        
        wd = env.prefs[workingDirectory_prefs_key]
        wdstr = "Current Working Directory - [" + wd  + "]"
        wd = QFileDialog.getExistingDirectory( wd, self, "get existing directory", wdstr, 1 )
        
        if not wd:
            env.history.message("Cancelled.")
            return
        
        wd = str(wd)
        if os.path.isdir(wd):
            wd = os.path.normpath(wd)
            env.prefs[workingDirectory_prefs_key] = wd # Change pref in prefs db.
            
            # Set the CWD to the Working Directory. Mark 060730.
            self.setCurrentWorkingDirectory(wd)
            
            env.history.message( "Working Directory set to " + wd )
        else:
            msg = "[" + dir + "] is not a directory. Working directory was not changed."
            env.history.message( redmsg(msg))
        return
                
    def __clear(self): #bruce 050911 revised this: leaves glpane.mode as nullmode
        #bruce 050907 comment: this is only called from two file ops in this mixin, so I moved it here from MWsemantics
        # even though its name-mangled name was thereby changed. It should really be given a normal name.
        # Some comments in other files still call it MWsemantics.__clear. [See also the 060127 kluge below.]
        
        self.assy = assembly(self, "Untitled", own_window_UI = True) # own_window_UI is required for this assy to support Undo
            #bruce 060127 added own_window_UI flag to help fix bug 1403
        self.update_mainwindow_caption()
        self.glpane.setAssy(self.assy) # leaves glpane.mode as nullmode, as of 050911
        self.assy.mt = self.mt
        
        ### Hack by Huaicai 2/1 to fix bug 369
        self.mt.resetAssy_and_clear() 
        
        self.deleteMMKit() #mark 051215.  Fixes bug 1222 (was bug 961, item #4).
        return

    _MWsemantics__clear = __clear #bruce 060127 kluge so it can be called as __clear from inside class MWsemantics itself.
    
    def _updateRecentFileList(self, fileName):
        '''Add the <fileName> into the recent file list '''
        LIST_CAPACITY = 4 #This could be set by user preference, not added yet
        from MWsemantics import recentfiles_use_QSettings #bruce 050919 debug code #####@@@@@
            
        if recentfiles_use_QSettings:
            prefsSetting = QSettings()
            fileList = prefsSetting.readListEntry('/Nanorex/nE-1/recentFiles')[0]
        else:
            fileName = str(fileName)
            prefsSetting = preferences.prefs_context()
            fileList = prefsSetting.get('/Nanorex/nE-1/recentFiles', [])
        
        if len(fileList) > 0:
           if fileName == fileList[0]:
               return
           else:
               for ii in range(len(fileList)):
                   if fileList[ii] == fileName: ## Put this one at the top
                       del fileList[ii]
                       break
        
        if recentfiles_use_QSettings:
            fileList.prepend(fileName) 
        else:
            fileList.insert(0, fileName)
            
        fileList = fileList[:LIST_CAPACITY]
        
        if recentfiles_use_QSettings:
            prefsSetting.writeEntry('/Nanorex/nE-1/recentFiles', fileList)
        else:
            prefsSetting['/Nanorex/nE-1/recentFiles'] = fileList 
        
        del prefsSetting
        
        self._createRecentFilesList()
        return

    def _openRecentFile(self, idx):
        '''Slot method when user choose from the recently opened files submenu. '''
        from MWsemantics import recentfiles_use_QSettings #bruce 050919 debug code #####@@@@@
        if recentfiles_use_QSettings:
            prefsSetting = QSettings()
            fileList = prefsSetting.readListEntry('/Nanorex/nE-1/recentFiles')[0]
        else:
            prefsSetting = preferences.prefs_context()
            fileList = prefsSetting.get('/Nanorex/nE-1/recentFiles', [])
        
        assert idx <= len(fileList)
        
        selectedFile = str(fileList[idx])
        self.fileOpen(selectedFile)
        return
        
    def _createRecentFilesList(self):
        '''Dynamically construct the list of recently opened files submenus '''
        from MWsemantics import recentfiles_use_QSettings #bruce 050919 debug code #####@@@@@
        
        if recentfiles_use_QSettings:
            prefsSetting = QSettings()
            fileList = prefsSetting.readListEntry('/Nanorex/nE-1/recentFiles')[0]
        else:
            prefsSetting = preferences.prefs_context()
            fileList = prefsSetting.get('/Nanorex/nE-1/recentFiles', [])
        
        self.recentFilePopupMenu = QPopupMenu(self)
        for ii in range(len(fileList)):
            recentFilename = os.path.normpath(str(fileList[ii])) # Fixes bug 2193. Mark 060808.
            self.recentFilePopupMenu.insertItem(qApp.translate("Main Window",  "&" + str(ii+1) + "  " + recentFilename, None), ii)
        
        menuIndex = self.RECENT_FILES_MENU_INDEX
        self.fileMenu.removeItemAt(menuIndex)
        self.fileMenu.insertItem(qApp.translate("Main Window", "Open Recent Files", None), self.recentFilePopupMenu, menuIndex, menuIndex)
            # WARNING: this is added in two places, in MWsemantics.__init__ and in _createRecentFilesList in ops_files.py.
            # Some of the other code here is duplicated as well, but not quite identically. [bruce 060808 comment]
        
        self.connect(self.recentFilePopupMenu, SIGNAL('activated (int)'), self._openRecentFile)
        return

    pass # end of class fileSlotsMixin

# end


## Test code--By cleaning the recent files list of QSettings###
if __name__ == '__main__':
    prefs = QSettings()
    from qt import QStringList
    emptyList = QStringList()
    prefs.writeEntry('/Nanorex/nE-1/recentFiles', emptyList)
    
    
    del prefs
    

# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
files_gms.py -- reading and writing GAMESS files

@author: Mark
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

History:

GAMESS file IO was part of GamessJob.py until I moved it here 
to make it more modular and consistent.
"""

import os, re, time
from model.chunk import Chunk
from model.chem import Atom
from string import capitalize
from model.elements import PeriodicTable
from platform_dependent.PlatformDependent import get_gms_name
from utilities.Log import redmsg, orangemsg
from geometry.VQT import A
import foundation.env as env

failpat = re.compile("ABNORMALLY")
errorPat = re.compile("Fatal error")
noconvpat = re.compile("GEOMETRY SEARCH IS NOT CONVERGED")
irecpat = re.compile(" (\w+) +\d+\.\d* +([\d\.E+-]+) +([\d\.E+-]+) +([\d\.E+-]+)")

def _readgms(assy, filename, isInsert=False):
    """
    Read the atoms from a GAMESS DAT file into a single new chunk, which is returned,
    unless there are no atoms in the file, in which case a warning is printed
    and None is returned. (The new chunk (if returned) is in assy, but is not
    yet added into any Group or Part in assy -- caller must do that.)
    """
    fi = open(filename,"rU")
    lines = fi.readlines()
    fi.close()
    
    dir, nodename = os.path.split(filename)
    ndix = {}
    mol = Chunk(assy, nodename)
    countdown = 0
    equilibruim_found = False
    atoms_found = False
    
    for card in lines:

        if failpat.search(card): # GAMESS Aborted.  No atom data will be found.
            print card
            break
        
        # If this card is found:
        # "1     ***** EQUILIBRIUM GEOMETRY LOCATED *****\n"
        # we know we have a successfully optimized structure/set of atoms.
        # If this card is not found, the optimization failed for some reason.
        # Atom positions begin soon after this card.
        if card == "1     ***** EQUILIBRIUM GEOMETRY LOCATED *****\n":
            equilibruim_found = True
            continue
            
        # The atom positions we want ALWAYS begin 2 lines after this card:
        # " COORDINATES OF ALL ATOMS ARE (ANGS)\n"
        # which follows the previous card.
        # This is one way to fix the problem mentioned above.
        # I've commented the code below out since it needs further work to do what
        # we need, and there is a chance we will not need this if GAMESS-US has
        # the same number of lines (6) after the "EQUILIBRIUM" card above.
        #
        # P.S. The reason we do not just look for this card by itself is that there
        # can be many of them.  There is only one "EQUILIBRIUM" card, and the
        # good atoms follow that card.
        # 050624 Mark
        
        if equilibruim_found:
            if card == " COORDINATES OF ALL ATOMS ARE (ANGS)\n":
                atoms_found = True
                reading_atoms = True
                countdown = 2
                continue
        
        if not equilibruim_found or not atoms_found:
            continue
            
        if countdown:
            countdown -= 1
#            print countdown, card # for debugging only.
            continue

        # The current card contains atom type and position. 
        
        n = 0
        
        if reading_atoms:
            if len(card)<10: 
                reading_atoms = False # Finished reading atoms.
                break
            m=irecpat.match(card)
            sym = capitalize(m.group(1))
            try:
                PeriodicTable.getElement(sym)
            except:
                env.history.message( redmsg( "Warning: GAMESS DAT file: unknown element %s in: %s" % (sym,card) ))
            else:
                xyz = map(float, (m.group(2),m.group(3), m.group(4)))
                a = Atom(sym, A(xyz), mol)
                ndix[n] = a
                n += 1
            
    # Don't return an empty chunk.
    if not mol.atoms:
        msg = "Warning: GAMESS file contains no equilibrium geometry.  No atoms read into part."
        env.history.message( redmsg(msg))
        return None
    
    # Need to compute and add bonds for this chunk.  I'll ask Bruce how to best accomplish this.
    # In the meantime, let's warn the user that no bonds have been formed since it
    # is impossible to see this in vdW display mode.  
    # Mark 050623.
    msg = "Warning: Equilibrium geometry found.  Atoms read into part, but there are no bonds."
    env.history.message( orangemsg(msg))
    return mol
    
# Read a GAMESS DAT file into a single chunk
def readgms(assy,filename):
    """
    Reads a GAMESS DAT file.
    Returns: 0 = Success
                   1 = Failed
    """
    mol  = _readgms(assy, filename, isInsert = False)
    if mol is not None:
        assy.addmol(mol)
        return 0
    else:
        return 1
    
# Insert a GAMESS DAT file into a single chunk.
def insertgms(assy,filename):
    """
    Reads a GAMESS DAT file and inserts it into the existing model.
    Returns: 0 = Success
                   1 = Failed
    """
    mol  = _readgms(assy, filename, isInsert = True)
    if mol is not None:
        assy.addmol(mol)
        return 0
    else:
        return 1
        

# Insert a GAMESS DAT file into a single chunk.
def insertgms_new(assy,filename):
    """
    Reads a GAMESS DAT file and inserts it into the existing model.
    Returns: 0 = Success
                   1 = Failed
    """

    gmsAtomList  = _get_atomlist_from_gms_outfile(assy, filename)
    
    if not gmsAtomList: 
        return 1 # No atoms read.
    
    dir, nodename = os.path.split(filename)
    mol = Chunk(assy, nodename)
    ndix = {}
    
    n = 0
    
    for a in gmsAtomList:
        print a
        pos = a.posn()
        fpos = (float(pos[0]), float(pos[1]), float(pos[2]))
        na = Atom(a.element.symbol, fpos, mol)
        ndix[n] = na
        n += 1
    
    if mol is not None:
        assy.addmol(mol)
        return 0
    else:
        return 1


# This was copied from _readgms and is mainly the same.  This will live, _readgms will
# be deleted eventually, after I ask Bruce how to get an alist from the mol (dict) in the same order
# as it was read from the file.   Since Python stores dict items in any order it chooses,
# I created a list with the same order that the atoms are read from the GAMESS OUT file.
# Mark 050712.
def _get_atomlist_from_gms_outfile(assy, filename):
    """
    Read the atoms from a GAMESS OUT file into an atom list, which is returned,
    unless there are no atoms in the file, in which case a warning is printed
    and None is returned.
    """
    fi = open(filename,"rU")
    lines = fi.readlines()
    fi.close()
    
    dir, nodename = os.path.split(filename)
    mol = Chunk(assy, nodename)
    
    newAtomList = [] 
    countdown = 0
    equilibruim_found = False
    atoms_found = False
    
    for card in lines:

        if failpat.search(card): # GAMESS Aborted.  No atom data will be found.
            print card
            env.history.message( redmsg( card ))
            break
            
        if noconvpat.search(card): # Geometry search is not converged.
            print card
            env.history.message( redmsg( card ))
            break
        
        # If this card is found:
        # "1     ***** EQUILIBRIUM GEOMETRY LOCATED *****\n"
        # we know we have a successfully optimized structure/set of atoms.
        # If this card is not found, the optimization failed for some reason.
        # Atom positions begin soon after this card.
        if card == "1     ***** EQUILIBRIUM GEOMETRY LOCATED *****\n":
            equilibruim_found = True
            continue
            
        # The atom positions we want ALWAYS begin 2 lines after this card:
        # " COORDINATES OF ALL ATOMS ARE (ANGS)\n"
        # which follows the previous card.
        # This is one way to fix the problem mentioned above.
        # I've commented the code below out since it needs further work to do what
        # we need, and there is a chance we will not need this if GAMESS-US has
        # the same number of lines (6) after the "EQUILIBRIUM" card above.
        #
        # P.S. The reason we do not just look for this card by itself is that there
        # can be many of them.  There is only one "EQUILIBRIUM" card, and the
        # good atoms follow that card.
        # 050624 Mark
        
        if equilibruim_found:
            if card == " COORDINATES OF ALL ATOMS ARE (ANGS)\n":
                atoms_found = True
                reading_atoms = True
                countdown = 2
                continue
        
        if not equilibruim_found or not atoms_found:
            continue
            
        if countdown:
            countdown -= 1
#            print countdown, card # for debugging only.
            continue

        # The current card contains atom type and position. 
        
        n = 0
        
        if reading_atoms:
#            print "_get_atomlist_from_gms_outfile:", card
            if len(card)<10: 
                reading_atoms = False # Finished reading atoms.
                break
            m=irecpat.match(card)
            sym = capitalize(m.group(1))
            try:
                PeriodicTable.getElement(sym)
            except:
                env.history.message( redmsg( "Warning: GAMESS OUT file: unknown element %s in: %s" % (sym,card) ))
            else:
                xyz = map(float, (m.group(2),m.group(3), m.group(4)))
                a = Atom(sym, A(xyz), mol)
                newAtomList += [a]
            
# Let caller handle history msgs.  Mark 050712
#    if not newAtomList:
#        msg = "Warning: GAMESS file contains no equilibrium geometry.  No atoms read into part."
#        env.history.message( redmsg(msg))
#        return None
    
    return newAtomList
    
        
# Read a GAMESS OUT file into a single chunk
def get_atompos_from_gms_outfile(assy, filename, atomList):
    """
    Reads a GAMESS DAT file and returns the xyz positions of the atoms.
    """
    gmsAtomList  = _get_atomlist_from_gms_outfile(assy, filename)
    
    if not gmsAtomList:
        msg = "No atoms read from file " + filename
        print msg
        return msg
    
    newAtomsPos = [] 
    atomIndex = 0
    
    for a in gmsAtomList:

#        print atomIndex + 1, a.element.symbol, atomList[atomIndex].element.symbol
        
        if a.element.symbol != atomList[atomIndex].element.symbol:
            msg = "The atom type (%s) of atom # %d from %s is not matching with the Gamess jig (%s)." % \
            (a.element.symbol, atomIndex + 1, filename, atomList[atomIndex].element.symbol)
            print msg
            return msg
        
        pos = a.posn()
        newAtomsPos += [map(float, pos)]
        
        atomIndex += 1
            
    if (len(newAtomsPos) != len(atomList)):
        msg = "The number of atoms from %s (%d) is not matching with the Gamess jig (%d)." % \
            (filename, len(newAtomsPos), len(atomList))
        print msg
        return msg
    
    return newAtomsPos
    
# File Writing Methods.
        
def writegms_inpfile(filename, gamessJig):
    """
    Writes a GAMESS INP file from a GAMESS Jig.
    """
    pset = gamessJig.pset
        
    f = open(filename,'w') # Open GAMESS input file.
        
    # Write header
    f.write ('!\n! INP file created by NanoEngineer-1 on ')
    timestr = "%s\n!\n" % time.strftime("%Y-%m-%d at %H:%M:%S")
    f.write(timestr)
    gmstr = "! " + get_gms_name() + " parameter summary: " + gamessJig.gms_parms_info() + "\n!\n"
    f.write(gmstr)
        
    # This method should be moved to the GAMESS Jig.
    pset.prin1(f) # Write GAMESS Jig parameters.
        
    # $DATA Section keyword
    f.write(" $DATA\n")
        
    # Comment (Description) line from UI
    f.write(pset.ui.comment + "\n")
        
    # Schoenflies symbol
    f.write("C1\n")
    
    for a in gamessJig.atoms:
        pos = a.posn()
        fpos = (float(pos[0]), float(pos[1]), float(pos[2]))
        f.write("%2s" % a.element.symbol)
        f.write("%8.1f" % a.element.eltnum)
        ##Huaicai 8/15/05: to fix bug 892
        #f.write("%8.3f%8.3f%8.3f\n" % fpos)
        f.write(" %.3f %.3f %.3f\n" % fpos)

    #  $END
    f.write(' $END\n')     


def writegms_batfile(filename, gamessJob):
    """
    Write PC GAMESS BAT file
    """ 
    f = open(filename,'w') # Open new BAT file.
    
    # Get the script comment character(s) for this platform.
    rem = gamessJob.get_comment_character()
    
    # Write Header
    f.write (rem + '\n' + rem + 'File created by NanoEngineer-1 on ')
    timestr = "%s\n" % time.strftime("%Y-%m-%d at %H:%M:%S")
    f.write(timestr)
    f.write (rem + '\n')
        
    gamessJob.write_parms(f) # write_parms is a method in superclass (SimJob)
        
    if gamessJob.server.engine == 'PC GAMESS': # Windows
        f.write(gamessJob.server.program + ' -i ' + gamessJob.job_inputfile + ' -o ' + gamessJob.job_outputfile + '\n')
    else: # GAMESS on Linux/Mac OS
        f.write(gamessJob.server.program + '  "' + gamessJob.job_inputfile + '" >& > "' + gamessJob.job_outputfile + '"\n')
            
    f.close() # Close BAT file.

def get_energy_from_gms_outfile(filename):
    """
    Returns a string containing the final energy value from a GAMESS OUT file.
    Works for both PC GAMESS and GAMESS-US.
    """
    # Method: Process the output file line by line backwards.  Since there are multiple 
    # "FINAL ENERGY IS" lines in the output file of an Optimization run (one for each iteration), 
    # it is the last line that contains the final energy value we need. This fixes an undocumented 
    # bug I discovered on 060112.  Mark.
    
    if not os.path.exists(filename):
        return 2, None
            
    elist = []
                    
    lines = open(filename,"rU").readlines()
    
    gamessEnergyStr = re.compile(r'\bFINAL R.+ ENERGY IS')
    
    for line in lines[::-1]: # Read file backwards.
        
        if failpat.search(line): # GAMESS Aborted.  Final energy will not be found.
            return 1, line
            break
        
        elif errorPat.search(line):
            return 1, line
            break
            
        elif line.find('FINAL ENERGY IS') >= 0:
            elist = line.split()
#            print elist
            return 0, elist[3] # Return final energy value as a string.
        
        elif gamessEnergyStr.search(line):# line.find('FINAL R-AM1 ENERGY IS') >= 0: 
            elist = line.split()
#            print elist
            return 0, elist[4] # Return final energy value as a string.
        
        else: continue
            
    return 1, None

# end

# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
files_gms.py -- reading and writing GAMESS files

$Id$

History: GAMESS file IO was part of GamessJob.py until I moved it here 
to make it more modular and consistent.
"""

__author__ = "Mark"

import os, re, time
from chunk import molecule
from chem import atom, bond_atoms
from string import capitalize
from elements import PeriodicTable, Singlet
from platform import fix_plurals
from HistoryWidget import redmsg, orangemsg
from VQT import A

failpat = re.compile("-ABNORMALLY-")
irecpat = re.compile(" (\w+) +\d+\.\d* +([\d\.E+-]+) +([\d\.E+-]+) +([\d\.E+-]+)")

def _readgms(assy, filename, isInsert = False):
    """Read the atoms from a GAMESS DAT file into a single new chunk, which is returned,
    unless there are no atoms in the file, in which case a warning is printed
    and None is returned. (The new chunk (if returned) is in assy, but is not
    yet added into any Group or Part in assy -- caller must do that.)
    Unless isInsert = True, set assy.filename to match the file we read,
    even if we return None.
    """
    fi = open(filename,"rU")
    lines = fi.readlines()
    fi.close()
    
    dir, nodename = os.path.split(filename)
    if not isInsert:
        assy.filename = filename
    ndix = {}
    mol = molecule(assy, nodename)
    countdown = 0
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
        # For PC GAMESS (WindowsXP) it is 6 lines after this card.
        # For GAMESS-US (Linux) it seems to be 3 lines after this card.
        #!!! This needs to be confirmed and addressed for Linux/GAMESS-US.
        # 050624 Mark
        if card == "1     ***** EQUILIBRIUM GEOMETRY LOCATED *****\n":
            atoms_found = True
            reading_atoms = True
            countdown = 6 # 6 lines if PC GAMESS, 3 lines if GAMESS-US.
            continue
            
        # The atom positions we want ALWAYS begin 2 lines after this card:
        # " COORDINATES OF ALL ATOMS ARE (ANGS)\n"
        # which follows the previous card by 4 cards in PC GAMESS.
        # This is one way to fix the problem mentioned above.
        # I've commented the code below out since it needs further work to do what
        # we need, and there is a chance we will not need this if GAMESS-US has
        # the same number of lines (6) after the "EQUILIBRIUM" card above.
        #
        # P.S. The reason we do not just look for this card by itself is that there
        # can be many of them.  There is only one "EQUILIBRIUM" card, and the
        # good atoms follow that card.
        # 050624 Mark
                
#        if card == " COORDINATES OF ALL ATOMS ARE (ANGS)\n":
#            atoms_found = True
#            reading_atoms = True
#            countdown = 2
#            continue
        
        if not atoms_found:
            continue
            
        if countdown:
            countdown -= 1
#            print countdown, card # for debugging only.
            continue

        n = 0
        
        if reading_atoms:
            if len(card)<10: 
                reading_atoms = False # Finished reading atoms.
                continue
            m=irecpat.match(card)
            sym = capitalize(m.group(1))
            try:
                PeriodicTable.getElement(sym)
            except:
                assy.w.history.message( redmsg( "Warning: GAMESS DAT file: unknown element %s in: %s" % (sym,card) ))
            else:
                xyz = map(float, (m.group(2),m.group(3), m.group(4)))
                a = atom(sym, A(xyz), mol)
                ndix[n] = a
                n += 1
            
    # Don't return an empty chunk.
    if not mol.atoms:
        msg = "Warning: GAMESS file contains no equilibrium geometry.  No atoms read into part."
        assy.w.history.message( redmsg(msg))
        return None
    
    # Need to compute and add bonds for this chunk.  I'll ask Bruce how to best accomplish this.
    # In the meantime, let's warn the user that no bonds have been formed since it
    # is impossible to see this in vdW display mode.  
    # Mark 050623.
    msg = "Warning: Equilibrium geometry found.  Atoms read into part, but there are no bonds."
    assy.w.history.message( orangemsg(msg))
    return mol
    
# Read a GAMESS DAT file into a single molecule (chunk)
def readgms(assy,filename):
    '''Reads a GAMESS DAT file.'''
    mol  = _readgms(assy, filename, isInsert = False)
    if mol is not None:
        assy.addmol(mol)
    return
    
# Insert a GAMESS DAT file into a single molecule (chunk).
def insertgms(assy,filename):
    '''Reads a GAMESS DAT file and inserts it into the existing model.'''
    mol  = _readgms(assy, filename, isInsert = True)
    if mol is not None:
        assy.addmol(mol)
    return

# File Writing Methods.
        
def writegms_inpfile(filename, gamessJig):
    '''Writes a GAMESS INP file from a GAMESS Jig.'''

    #!!! Should change psets[] list to a single pset attribute everywhere.
    # Mark 050623 (on the airplane going home).
    pset = gamessJig.psets[0] 
        
    f = open(filename,'w') # Open GAMESS input file.
        
    # Write header
    f.write ('!\n! INP file created by nanoENGINEER-1 on ')
    timestr = "%s\n!\n" % time.strftime("%Y-%m-%d at %H:%M:%S")
    f.write(timestr)
    gmstr = "! GAMESS parameter summary: " + gamessJig.gms_parms_info() + "\n!\n"
    f.write(gmstr)
        
    # This method should be moved to the GAMESS Jig.
    pset.prin1(f) # Write GAMESS Jig parameters.
        
    # $DATA Section keyword
    f.write(" $DATA\n")
        
    # Comment (Description) line from UI
    f.write(pset.ui.comment + "\n")
        
    # Schoenflies symbol
    f.write("C1\n")
        
#    from jigs import povpoint
    for a in gamessJig.atoms:
        pos = a.posn()
        fpos = (float(pos[0]), float(pos[1]), float(pos[2]))
        f.write("%2s" % a.element.symbol)
        f.write("%8.1f" % a.element.eltnum)
        f.write("%8.3f%8.3f%8.3f\n" % fpos)

    #  $END
    f.write(' $END\n')     


def writegms_batfile(filename, gamessJob):
    'Write PC GAMESS BAT file'
        
    f = open(filename,'w') # Open new BAT file.
    
    # Get the script comment character(s) for this platform.
    rem = gamessJob.get_comment_character()
    
    # Write Header
    f.write (rem + '\n' + rem + 'File created by nanoENGINEER-1 on ')
    timestr = "%s\n" % time.strftime("%Y-%m-%d at %H:%M:%S")
    f.write(timestr)
    f.write (rem + '\n')
        
    gamessJob.write_parms(f) # write_parms is located in superclass (SimJob)
        
    if gamessJob.server.engine == 'PC GAMESS': # Windows
        f.write(gamessJob.server.program + ' -i "' + gamessJob.job_inputfile + '" -o "' + gamessJob.job_outputfile + '"\n')
    else: # GAMESS on Linux/Mac OS
        f.write(gamessJob.server.program + '  "' + gamessJob.job_inputfile + '" >& > "' + gamessJob.job_outputfile + '"\n')
            
    f.close() # Close BAT file.

def get_energy_from_pcgms_outfile(filename):
    '''Returns the final energy value from the PC GAMESS DAT file.
    GAMESS is not yet supported, as the line containing the energy
    value may be different from PC GAMESS.
    '''
    
    #!!! This routine can serve for both PC GAMESS and GAMESS if we know the version.
    # When Huaicai or I start working on Linux, we'll pass the version as an argument.
    # Something like this:
    # if gms_version == 'PC GAMESS':
    #     findstr = 'FINAL ENERGY IS'
    # else:
    #     findstr = 'WHATEVER GAMESS FINAL ENERGY IS'
    # Mark 050624
        
    if not os.path.exists(filename):
        return None
            
    elist = []
                    
    lines = open(filename,"rU").readlines()
        
    for line in lines:
        if line.find('FINAL ENERGY IS') >= 0:
            elist = line.split()
#            print elist
            return float(elist[3]) # Return the final energy value.
        else: continue
            
    return None

# end
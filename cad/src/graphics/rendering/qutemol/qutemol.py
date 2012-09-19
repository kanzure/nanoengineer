# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
qutemol.py - provides routines to support QuteMolX as a plug-in.

@author: Mark
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

History:

mark 2007-06-02
- Created file. Much of the plug-in checking code was copied from
povray.py, written by Bruce.

Module classification: [bruce 071215, 080103]

Looks like operations and io code. Similar to "simulation" code
but is not about simulation -- maybe that category is misconceived
and what we want instead is an "external process" category of code.
For now, call this "graphics_io" but file it into graphics/rendering/QuteMolX.
"""

import foundation.env as env
import os
import sys
from PyQt4.Qt import QString, QStringList, QProcess

from utilities.prefs_constants import qutemol_enabled_prefs_key, qutemol_path_prefs_key
from utilities.debug import print_compact_traceback
from utilities.debug_prefs import debug_pref, Choice_boolean_True
from utilities.constants import properDisplayNames, TubeRadius, diBALL_SigmaBondRadius
from files.pdb.files_pdb import writePDB_Header, writepdb, EXCLUDE_HIDDEN_ATOMS
from model.elements import PeriodicTable

from utilities.prefs_constants import cpkScaleFactor_prefs_key
from utilities.prefs_constants import diBALL_AtomRadius_prefs_key
from utilities.prefs_constants import backgroundGradient_prefs_key
from utilities.prefs_constants import backgroundColor_prefs_key
from utilities.prefs_constants import diBALL_BondCylinderRadius_prefs_key

from processes.Plugins import checkPluginPreferences

from processes.Process import Process
from commands.GroupProperties.GroupProp import Statistics
from platform_dependent.PlatformDependent import find_or_make_Nanorex_subdir

def launch_qutemol(pdb_file):
    """
    Launch and load QuteMolX with the PDB file I{pdb_file}.

    @param pdb_file: the PDB filename to load
    @type  pdb_file: string

    @return: (errorcode, errortext)
             where errorcode is one of the following: ###k
                 0 = successful
                 8 = QuteMolX failed for an unknown reason.
    @rtype:  int, text
    """

    plugin_name = "QuteMolX"
    plugin_prefs_keys = (qutemol_enabled_prefs_key, qutemol_path_prefs_key)

    errorcode, errortext_or_path = \
             checkPluginPreferences(plugin_name, plugin_prefs_keys,
                                    insure_executable = True)
    if errorcode:
        return errorcode, errortext_or_path

    program_path = errortext_or_path

    workdir, junk_exe = os.path.split(program_path)

    # This provides a way to tell NE1 which version of QuteMolX is installed.
    if debug_pref("QuteMol 0.4.1 or later",
                  Choice_boolean_True,
                  prefs_key = True):
        version = "0.4.1"
    else:
        version = "0.4.0"

    # Start QuteMolX.
    try:
        args = [pdb_file]
        if env.debug():
            print "Debug: Launching", plugin_name, \
                  "\n  working directory=", workdir, \
                  "\n  program_path=", program_path,  \
                  "\n  args are %r" % (args,)

        arguments = QStringList()
        for arg in args:
            if arg != "":
                arguments.append(arg)

        p = Process()

        # QuteMolX must run from the directory its executable lives. Otherwise,
        # it has serious problems (but still runs). Mark 2007-06-02.
        p.setWorkingDirectory(QString(workdir))

        # Tried p.startDetached() so that QuteMolX would be its own process and
        # continue to live even if NE1 exits. Unfortunately,
        # setWorkingDirectory() doesn't work. Seems like a Qt bug to me.
        # Mark 2007-06-02
        p.start(program_path, arguments)

    except:
        print_compact_traceback( "exception in launch_qutemol(): " )
        return 8, "%s failed for an unknown reason." % plugin_name

    # set an appropriate exitcode and msg
    if p.exitStatus() == QProcess.NormalExit:
        exitcode = p.exitStatus()
        if not exitcode:
            msg = plugin_name + " launched."
        else:
            msg = plugin_name + " had exitcode %r" % exitcode
    else:
        exitcode = p.exitStatus()
        exitcode = -1
        msg = "Abnormal exit (or failure to launch)"

    if exitcode:
        return 8, "Error: " + msg
        # this breaks the convention of the other error returns

    return 0, plugin_name + " launched." # from launch_qutemol


def write_art_data(fileHandle):
    """
    Writes the Atom Rendering Table (ART) data, which contains all
    the atom rendering properties needed by QuteMolX, to the file with the
    given fileHandle.
    Each atom is on a separate line.
    Lines starting with '#' are comment lines.
    """
    fileHandle.write("""\
REMARK   8
REMARK   8 ;NanoEngineer-1 Atom Rendering Table (format version 0.1.0)
REMARK   8 ;This table specifies the scene rendering scheme as employed by
REMARK   8 ;NanoEngineer-1 (NE1) at the time this file was created.
REMARK   8
REMARK   8 ;Note: All CPK radii were calculated using a CPK scaling factor that
REMARK   8 ;can be modified by the user from "Preferences... | Atoms".\n""")
    fileHandle.write("REMARK   8 ;This table's CPK Scaling Factor: %2.3f"
                     % env.prefs[cpkScaleFactor_prefs_key])
    fileHandle.write("""
REMARK   8 ;To compute the original van der Waals radii, use the formula:
REMARK   8 ;  vdW Radius = CPK Radius / CPK Scaling Factor
REMARK   8
REMARK   8 ;Atom Name  NE1 Atom  CPK Radius  Ball and Stick  Color (RGB)
REMARK   8 ;           Number                Radius\n""")

    elementTable = PeriodicTable.getAllElements()
    for elementNumber, element in elementTable.items():
        color = element.color
        r = int(color[0] * 255 + 0.5)
        g = int(color[1] * 255 + 0.5)
        b = int(color[2] * 255 + 0.5)

        # The following was distilled from chem.py: Atom.howdraw()
        #
        # "Render Radius"
        cpkRadius = \
            element.rvdw * env.prefs[cpkScaleFactor_prefs_key]

        # "Covalent Radius"
        ballAndStickRadius = \
            element.rvdw * 0.25 * env.prefs[diBALL_AtomRadius_prefs_key]

        #if element.symbol == 'Ax3':
        #    ballAndStickRadius = 0.1

        fileHandle.write \
            ("REMARK   8  %-3s        %-3d       %3.3f       %3.3f           %3d  %3d  %3d\n"
             % (element.symbol, elementNumber, cpkRadius, ballAndStickRadius,
                r, g, b))

    fileHandle.close()
    return

def write_qutemol_pdb_file(part, filename, excludeFlags):
    """
    Writes an NE1-QuteMolX PDB file of I{part} to I{filename}.

    @param part: the NE1 part.
    @type  part: L{assembly}

    @param filename: the PDB filename to write
    @type  filename: string

    @param excludeFlags: used to exclude certain atoms from being written
        to the QuteMolX PDB file.
    @type  excludeFlags: int

    @see L{writepdb()} for more information about I{excludeFlags}.
    """

    f = open(filename, "w")

    skyBlue = env.prefs[ backgroundGradient_prefs_key ]

    bgcolor = env.prefs[ backgroundColor_prefs_key ]
    r = int (bgcolor[0] * 255 + 0.5)
    g = int (bgcolor[1] * 255 + 0.5)
    b = int (bgcolor[2] * 255 + 0.5)

    TubBond1Radius = TubeRadius
    BASBond1Radius = \
                   diBALL_SigmaBondRadius * \
                   env.prefs[diBALL_BondCylinderRadius_prefs_key]

    writePDB_Header(f) # Writes our generic PDB header

    # Write the QuteMolX REMARKS "header".
    # See the following wiki page for more information about
    # the format of all NE1-QuteMolX REMARK records:
    # http://www.nanoengineer-1.net/mediawiki/index.php?title=NE1_PDB_REMARK_Records_Display_Data_Format
    #
    f.write("""\
REMARK   6 - The ";" character is used to denote non-data (explanatory) records
REMARK   6   in the REMARK 7 and REMARK 8 blocks.
REMARK   6
REMARK   7
REMARK   7 ;Display Data (format version 0.1.0) nanoengineer-1.com/PDB_REMARK_7
REMARK   7\n""")

    f.write("REMARK   7 ORIENTATION: %1.6f %1.6f %1.6f %1.6f\n"
            % (part.o.quat.w, part.o.quat.x, part.o.quat.y, part.o.quat.z))
    f.write("REMARK   7 SCALE: %4.6f\n"
            % part.o.scale)
    f.write("REMARK   7 POINT_OF_VIEW: %6.6f %6.6f %6.6f\n"
            % (part.o.pov[0], part.o.pov[1], part.o.pov[2]))
    f.write("REMARK   7 ZOOM=%6.6f\n"
            % part.o.zoomFactor)
    if skyBlue:
        f.write("REMARK   7 BACKGROUND_COLOR: SkyBlue\n")
    else:
        f.write("REMARK   7 BACKGROUND_COLOR: %3d %3d %3d\n"
            % (r, g, b))
    f.write("REMARK   7 DISPLAY_STYLE: %s\n"
            % properDisplayNames[part.o.displayMode])
    f.write("REMARK   7 TUBES_BOND_RADIUS: %1.3f\n"
            % TubBond1Radius)
    f.write("REMARK   7 BALL_AND_STICK_BOND_RADIUS: %1.3f\n"
            % BASBond1Radius)

    # Now write the REMARK records for each chunk (chain) in the part.
    molNum = 1
    for mol in part.molecules:
        if mol.hidden:
            # Skip hidden chunks. See docstring in writepdb() for details.
            # Mark 2008-02-13.
            continue
        f.write("REMARK   7 CHAIN: %s " % (molNum))
        f.write("  DISPLAY_STYLE: %s " % properDisplayNames[mol.display])
        if mol.color:
            r = int (mol.color[0] * 255 + 0.5)
            g = int (mol.color[1] * 255 + 0.5)
            b = int (mol.color[2] * 255 + 0.5)
            f.write("  COLOR: %3d %3d %3d " % (r, g, b))
        f.write("  NAME: \"%s\"\n" % mol.name)

        molNum+=1

    f.write("REMARK   7\n")

    write_art_data(f)

    f.close()

    # Write the "body" of PDB file (appending it to what we just wrote).
    writepdb(part, filename, mode = 'a', excludeFlags = excludeFlags)

def write_qutemol_files(part, excludeFlags = EXCLUDE_HIDDEN_ATOMS):
    """
    Writes a PDB of the current I{part} to the Nanorex temp directory.

    @param part: the NE1 part.
    @type  part: L{assembly}

    @param excludeFlags: used to exclude certain atoms from being written
        to the QuteMolX PDB file, where:
        WRITE_ALL_ATOMS = 0 (even writes hidden and invisble atoms)
        EXCLUDE_BONDPOINTS = 1 (excludes bondpoints)
        EXCLUDE_HIDDEN_ATOMS = 2 (excludes both hidden and invisible atoms)
        EXCLUDE_DNA_ATOMS = 4 (excludes PAM3 and PAM5 pseudo atoms)
        EXCLUDE_DNA_AXIS_ATOMS = 8 (excludes PAM3 axis atoms)
        EXCLUDE_DNA_AXIS_BONDS = 16 (suppresses PAM3 axis bonds)
    @type  excludeFlags: int

    @return: the name of the temp PDB file, or None if no atoms are in I{part}.
    @rtype:  str
    """

    # Is there a better way to get the number of atoms in <part>.?
    # Mark 2007-06-02
    stats = Statistics(part.tree)

    if 0:
        stats.num_atoms = stats.natoms - stats.nsinglets
        print "write_qutemol_files(): natoms =", stats.natoms, \
              "nsinglets =", stats.nsinglets, \
              "num_atoms =", stats.num_atoms

    if not stats.natoms:
        # There are no atoms in the current part.
        # writepdb() will create an empty file, which causes
        # QuteMolX to crash at launch.
        # Mark 2007-06-02
        return None

    pdb_basename = "QuteMolX.pdb"

    # Make full pathnames for the PDB file (in ~/Nanorex/temp/)
    tmpdir = find_or_make_Nanorex_subdir('temp')
    qutemol_pdb_file = os.path.join(tmpdir, pdb_basename)

    # Write the PDB file.
    write_qutemol_pdb_file(part, qutemol_pdb_file, excludeFlags)

    return qutemol_pdb_file

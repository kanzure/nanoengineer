# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
whatsThis_for_MinimizeEnergyDialog.py

This file provides functions for setting the "What's This" and tooltip text
for widgets in the NE1 Minimize Energy dialog only.

Edit WhatsThisText_for_MainWindow.py to set "What's This" and tooltip text
for widgets in the Main Window.

@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

"""

def whatsThis_MinimizeEnergyDialog(minimizeEnergyDialog):
    """
    Assigning the I{What's This} text for the Minimize Energy dialog.
    """

    _med = minimizeEnergyDialog

    _med.update_every_rbtn.setWhatsThis(
        """<b>Update every <i>n units.</u></b>
        <p>
        Specify how often to update the model during the adjustment.
        This allows the user to monitor results during adjustments.
        </p>""")
    _med.update_asap_rbtn.setWhatsThis(
        """<b>Update as fast as possible</b>
        <p>
        Update every 2 seconds, or faster (up to 20x/sec) if it doesn't
        slow adjustments by more than 20%
        </p>""")
    _text = \
        """<b>EndRMS</b>
        <p>
        Continue until this RMS force is reached.
        </p>"""
    _med.endrms_lbl.setWhatsThis(_text)
    _med.endRmsDoubleSpinBox.setWhatsThis(_text)
    _text = \
        """<b>EndMax</b>
        <p>
        Continue until no interaction exceeds this force.
        </p>"""
    _med.endmax_lbl.setWhatsThis(_text)
    _med.endMaxDoubleSpinBox.setWhatsThis(_text)

    _text = \
        """<b>CutoverMax</b>
        <p>Use steepest descent until no interaction exceeds this force.
        </p>"""
    _med.cutovermax_lbl.setWhatsThis(_text)
    _med.cutoverMaxDoubleSpinBox.setWhatsThis(_text)

    _text = \
        """<b>CutoverRMS</b>
        <p>
        Use steepest descent until this RMS force is reached.
        </p>"""
    _med.cutoverRmsDoubleSpinBox.setWhatsThis(_text)
    _med.cutoverrms_lbl.setWhatsThis(_text)

    _med.minimize_all_rbtn.setWhatsThis(
        """<b>Minimize All</b>
        <p>Perform energy minimization on all the atoms in the workspace.
        </p>""")
    _med.minimize_sel_rbtn.setWhatsThis(
        """<b>Minimize Selection</b>
        <p>
        Perform energy minimization on the atoms that are currently selected.
        </p>""")
    _med.watch_motion_groupbox.setWhatsThis(
        """<b>Watch Motion In Real Time</b>
        <p>
        Enables real time graphical updates during minimization runs.
        """)
    _med.update_asap_rbtn.setWhatsThis(
        """<b>Update as fast as possible</b>
        <p>
        Update every 2 seconds, or faster (up to 20x/sec) if it doesn't slow
        minimization by more than 20%.
        </p>""")
    _med.update_every_rbtn.setWhatsThis(
        """<b>Update every <i>n units.</u></b>
        <p>
        Specify how often to update the model during the minimization.
        This allows the user to monitor minimization results while the
        minimization is running.
        </p>""")
    _med.update_number_spinbox.setWhatsThis(
        """<b>Update every <i>n units.</u></b>
        <p>
        Specify how often to update the model during the minimization.
        This allows the user to monitor minimization results while the
        minimization is running.
        </p>""")
    _med.update_units_combobox.setWhatsThis(
        """<b>Update every <i>n units.</u></b>
        <p>
        Specify how often to update the model during the minimization.
        This allows the user to monitor minimization results while the
        minimization is running.</p>""")
    _med.cancel_btn.setWhatsThis(
        """<b>Cancel</b>
        <p>
        Dismiss this dialog without taking any action.
        </p>""")
    _med.ok_btn.setWhatsThis(
        """<b>Minimize Energy</b>
        <p>
        Using the parameters specified above perform energy minimization on
        some or all of the atoms.
        </p>""")
    _med.setWhatsThis("""<u><b>Minimize Energy</b></u>
        <p>
        The potential energy of a chemical structure is a function of the
        relative positions of its atoms. To obtain this energy with complete
        accuracy involves a lot of computer time spent on quantum mechanical
        calculations, which cannot be practically done on a desktop computer.
        To get an approximate potential energy without all that, we represent
        the energy as a series of terms involving geometric properties
        of the structure: lengths of chemical bonds, angles between pairs and
        triples of chemical bonds, etc. </p>
        <p>
        As is generally the case with physical systems, the gradient of the
        potential energy represents the forces acting on various particles. The
        atoms want to move in the direction that most reduces the potential
        energy. Energy minimization is a process of adjusting the atom
        positions to try to find a global minimum of the potential energy.
        Each atom contributes three variables (its x, y, and z  coordinates)
        so the search space is multi-dimensional. The global minimum is the
        configuration that the atoms will settle into if lowered to zero Kelvin.
        </p>""")

    return

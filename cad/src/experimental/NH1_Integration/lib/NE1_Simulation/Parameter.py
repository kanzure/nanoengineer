
# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
Encapsulates the information necessary for viewing and editing single parameters
via some GUI.

The following is the object model of the Parameter module:
IMAGE_2
"""


class Parameter:
    """
    A GUI editable key/value pair. When newly constructed, the value is
    officially un-set (see the L{getValue} method.)

    This is an abstract/interface class and should not be instantiated.
    """


    def __init__(self, key):
        """
        Constructs a Parameter object with the given key - should only be called
        by L{ParameterFactory}.
        """
        hasValue = 0;


    def getKey(self):
        """
        Returns the dotted descriptor of what this parameter is.
        """
        pass


    def getValue(self):
        """
        Returns whether this Parameter has a set value, and what that value is.
        @return: (0=no value set, 1=value set), (value)
        """
        pass
    def setValue(self, value):
        """
        Sets the value of this Parameter.
        """
        pass
    def unSetValue(self):
        """
        Un-sets this Parameter's value.
        """
        hasValue = 0;



class ParameterFactory:
    """
    Creates fully configured Parameter subclass objects.

    Key names are dot-separated based on the L{SimSpecification} object model.
    Here is the list of reserved key names:

    B{simSpec.timestep} [float seconds] - The amount of time
    between the calculations of a system's state. Widget: lineedit,
    min=0.05e-15, max=5.00e-15, default=0.1e-15, suffix=s

    B{simSpec.startStep} [integer] - The number of the first step -
    usually zero, but may be non-zero when a simulation is continuing on
    fromwhere a previous simulation stopped. Widget: lineedit,
    min=0, max=-1, default=0

    and etc. etc. for

    B{simSpec.}maxSteps, stepsPerFrame,
    environmentTemperature, environmentPressure, workingDirectory

    B{simSpec.input.}type, file

    B{simSpec.motionPath.interval.}start, end

    B{simSpec.motionPath.interval.velocity.}fixed, xyzComponents, etc.

    B{simSpec.operation.}action

    B{simSpec.operation.}engine, atomSet, method,
    basisSet, functional, multiplicity, integrator, energyAccuracy,
    maxConvergenceAttempts, unscripted, applyFrom, applyTo

    B{simSpec.operation.constraint.}motion, atomSet

    B{simSpec.operation.measurement.}measure, atomSet

    B{simSpec.preSimChecks.}all, detectUnMinimized, checkJigSanity,
    detectUnusedJigs, detectReactionPoints, checkSpinMultiplicity
    """


    def createParameter(self, key):
        """Returns a fully configured Parameter subclass for the given key."""
        pass


class ParameterSet:
    """A set of Parameters."""


    def getGroupName(self):
        """Returns this ParameterSet's group name for GUI use."""
        return self.groupName


    def getParameter(self, key):
        """
        Returns whether or not the Parameter with the given key is in this set,
        and the Parameter itself if it is.
        @return: (0=the Parameter for the given key is not in this set, 1=the
                  Parameter is present), (the Parameter)
        """
        pass
    def getParameterArray(self):
        """
        Returns this object's Parameters in an array in the correct order. The
        correct order is determined by each Parameter's "order" attribute.
        """
        pass
    def setParameter(self, Parameter):
        """
        Sets the given parameter. Any existing Parameter with the same key will
        be clobbered.
        """
        # Insert the Parameter such that the array remains sorted by
        # Parameter.order
        pass










#  <table>
#    <tr><td><b>Keyword<br>[Type Units]</b></td>
#        <td align="center"><b>Meaning</b></td></tr>
#    <tr><td>name<br>[string]</td>
#        <td valign="top">The simulation name.</td></tr>
#    <tr><td>description<br>[string]</td>
#        <td valign="top">A description of the simulation.</td></tr>
#    <tr><td nowrap >timestep<br>[float seconds]</td>
#        <td valign="top">The amount of time between the calculations of a system's state.</td></tr>
#    <tr><td>startStep<br>[integer]</td>
#        <td valign="top">The number of the first step - usually zero, but may be non-zero when a simulation is continuing on from where a previous simulation stopped.</td></tr>
#    <tr><td>maxSteps<br>[integer]</td>
#        <td valign="top">The maximum number of steps to simulate.</td></tr>
#    <tr><td>stepsPerFrame<br>[integer]</td>
#        <td valign="top">The number of steps to aggregate into a single frame of data.</td>
#    <tr><td>environmentTemperature<br>[float Kelvin]</td>
#        <td valign="top">The simulation environment temperature.</td>
#    <tr><td>environmentPressure<br>[float Pascals]</td>
#        <td valign="top">The simulation environment pressure.</td>
#    <tr><td>workflow</td>
#        <td valign="top">Specific configuration about the simulation workflow or process.
#            <table>
#              <tr><td>inputFiles<br>[string]</td>
#                  <td valign="top">A list of input files.
#                      <table>
#                        <tr><td>filePath<br>[string]</td>
#                            <td valign="top">The input file path.</td></tr>
#                        <tr><td>fileType<br>[string]</td>
#                            <td valign="top">The input file type: MMP, PDB, etc.</td></tr>
#                      </table>
#                  </td></tr>
#              <tr><td>outputFile<br>[string]</td>
#                  <td valign="top">An output file path.</td></tr>
#            </table>
#        </td></tr>
#  </table>

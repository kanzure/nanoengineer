# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

"""
SimulatorParameters.py

Read the sim-params.txt file, and extract information needed on the
NE1 side.  This currently consists of parameters controlling the
Yukawa non-bonded potential function for PAM3 and PAM5 DNA models.
NE1 generates the tables which define a user-defined potential
function for GROMACS.

@author: Eric M
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

import os
import foundation.env as env
from platform_dependent.PlatformDependent import find_plugin_dir

from utilities.debug import print_compact_traceback

class SimulatorParameters(object):
    def __init__(self):
        ok, nd1_plugin_path = find_plugin_dir("NanoDynamics-1")
        if (not ok):
            env.history.redmsg("Error: can't find " + nd1_plugin_path)
            nd1_plugin_path = "."
        fileName = os.path.join(nd1_plugin_path, "sim-params.txt")

        self._parameterValues = {}
        try:
            print "sim parameters used by NE1 read from: [%s]" % fileName
            parametersFile = open(fileName)
            for line in parametersFile:
                s = line.split()
                if (len(s) > 0 and s[0] == "ne1"):
                    if (len(s) > 1):
                        key = s[1]
                        if (len(s) > 2):
                            value = " ".join(s[2:])
                        else:
                            value = True
                        self._parameterValues[key] = value
        except IOError:
            msg = "Error reading [%s]" % fileName
            print_compact_traceback(msg + ": ")
            env.history.redmsg(msg)
            self._parameterValues = {}

    def _getFloatParameter(self, parameterName, defaultValue = 0.0):
        if (self._parameterValues.has_key(parameterName)):
            try:
                value = float(self._parameterValues[parameterName])
                return value
            except:
                print_compact_traceback()
                env.history.redmsg("malformed float parameter %s in sim-params.txt" % parameterName)
        return defaultValue

    def _getBooleanParameter(self, parameterName, defaultValue = False):
        if (self._parameterValues.has_key(parameterName)):
            if (self._parameterValues[parameterName]):
                return True
            return False
        return defaultValue

    def getYukawaRSwitch(self):
        return self._getFloatParameter("YukawaRSwitch", 2.0)
    
    def getYukawaRCutoff(self):
        return self._getFloatParameter("YukawaRCutoff", 3.0)

    def getYukawaShift(self):
        return self._getBooleanParameter("YukawaShift", True)

    def getYukawaCounterionCharge(self):
        return self._getFloatParameter("YukawaCounterionCharge", 2.0)

    def getYukawaCounterionMolarity(self):
        return self._getFloatParameter("YukawaCounterionMolarity", 0.02)

    def getYukawaTemperatureKelvin(self):
        return self._getFloatParameter("YukawaTemperatureKelvin", 298.0)

    def getYukawaDielectric(self):
        return self._getFloatParameter("YukawaDielectric", 78.5)

    def getYukawaConstantMultiple(self):
        return self._getFloatParameter("YukawaConstantMultiple", 1.0)

    
        

# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
# 10/3 currently being owned by Josh

"""Classes for objects in the model
$Id$
"""

from VQT import Q
from chem import molecule

class Group:
        """This class is used to organize different molecules into a group"""
        
        def __init__(self, name, list = None):
                self.name = name
                self.members = list
                
                 
        def __str__(self):
                rec = "group (" + self.name +") "
                for m in self.members:
                        if isinstance(m, molecule):
                                rec += "(" + m.name + ") "
                        else:
                                rec += "(<" + m.name + ">) "
                                
                return rec                
                
class Csys:
        """ Information for coordinate system"""
        
        def __init__(self, name, zoom, w, x = None, y = None, z = None):
                self.name = name
                self.zoom = zoom
                
                if not x and not y and not z:
                        self.quat = Q(w)
                else:
                        self.quat = Q(x, y, z, w)
                              
        def __str__(self):
                
                rStr = "csys (" + self.name + ") (" 
                rStr += str(self.quat.w) + ", " + str(self.quat.x) + ", " + str(self.quat.y) + ", " + str(self.quat.z) 
                rStr += ") (" + str(self.zoom) + ")"
                
                return rStr
                
class Waals:
        """ Van del Waals """
        
        def __init__(self, list):
                self. atomsList = list
                
        def __str__(self, ndix = None):
                if ndix:
                        nums = map((lambda a: ndix[a.key]), self.atomsList)
                else:
                        nums = map((lambda a: a.key), self.atomsList)
                return "waals " + " ".join(map(str,nums))
      

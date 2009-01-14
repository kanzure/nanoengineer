# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
CrystalShape.py -- handle freehand curves for crystal-cutting (?)

@author: Huaicai, maybe others
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 071215 split class CrystalShape out of shape.py into its own module.

Module classification:

Contains graphics_behavior and operations and perhaps internal transient
model code, all to help the graphics_mode (and command?) for Build Crystal
(presently an unsplit_mode, BuildCrystal_Command). So the overall classification
is not clear -- for now say "command" since nothing less does all the above.
But it'll end up in a package for Build Crystal, so this might be ok.
[bruce 071215]
"""

from Numeric import dot, floor

from geometry.VQT import vlen, V
from OpenGL.GL import glNewList, glEndList, glCallList
from OpenGL.GL import GL_COMPILE_AND_EXECUTE

from graphics.drawing.drawers import drawCircle
from graphics.drawing.drawers import genDiam
from graphics.drawing.CS_draw_primitives import drawcylinder
from graphics.drawing.CS_draw_primitives import drawsphere
from graphics.drawing.CS_draw_primitives import drawline
from graphics.drawing.ColorSorter import ColorSorter
from graphics.drawing.ColorSorter import ColorSortedDisplayList

from utilities.constants import SUBTRACT_FROM_SELECTION
from utilities.constants import OUTSIDE_SUBTRACT_FROM_SELECTION
from utilities.constants import ADD_TO_SELECTION
from utilities.constants import START_NEW_SELECTION
from utilities.constants import white

from utilities.debug import print_compact_traceback

from geometry.BoundingBox import BBox

from graphics.behaviors.shape import simple_shape_2d
from graphics.behaviors.shape import get_selCurve_color
from graphics.behaviors.shape import shape

from model.bonds import bond_atoms

# ==

class _Circle(simple_shape_2d):
    """
    Represents the area of a circle ortho projection intersecting with a slab.
    """
    def __init__(self, shp, ptlist, origin, selSense, **opts):
        """
        <Param> ptlist: the circle center and a point on the perimeter
        """
        simple_shape_2d.__init__( self, shp, ptlist, origin, selSense, opts)

    def draw(self):
        """
        the profile circle draw
        """
        color =  get_selCurve_color(self.selSense)
        drawCircle(color, self.ptlist[0], self.rad, self.slab.normal)

    def isin(self, pt):
        """
        Test if a point is in the area
        """
        if self.slab and not self.slab.isin(pt):
            return False

        p2d = self.project_2d(pt)
        dist = vlen(p2d - self.cirCenter)
        if dist <= self.rad :
            return True
        else:
            return False

    def _computeBBox(self):
        """
        Construct the 3D bounding box for this volume.
        """
        self.rad = vlen(self.ptlist[1] - self.ptlist[0])
        self.cirCenter = self.project_2d(self.ptlist[0])

        bbhi = self.cirCenter + V(self.rad, self.rad)
        bblo = self.cirCenter - V(self.rad, self.rad)

        x, y = self.right, self.up
        self.bbox = BBox(V(bblo, bbhi), V(x, y), self.slab)

    pass

# ==

class CrystalShape(shape):
    """
    This class is used to create cookies. It supports multiple parallel layers,
    each curve sits on a particular layer.
    """
    def __init__(self, right, up, normal, mode, latticeType):
        shape.__init__(self, right, up, normal)
        # Each element is a dictionary object storing "carbon" info for a layer
        self.carbonPosDict = {} 
        self.hedroPosDict = {}
        self.markedAtoms = {}
        # Each element is a dictionary for the bonds info for a layer
        self.bondLayers = {} 

        self.displist = ColorSortedDisplayList()
        self.havelist = 0
        self.dispMode = mode
        self.latticeType = latticeType
        self.layerThickness = {}
        self.layeredCurves = {} # A list of (merged bb, curves) for each layer

    def pushdown(self, lastLayer):
        """
        Put down one layer from last layer
        """
        th, n = self.layerThickness[lastLayer]
        #print "th, n", th, n
        return th * n

    def _saveMaxThickness(self, layer, thickness, normal):
        if layer not in self.layerThickness:
            self.layerThickness[layer] = (thickness, normal)
        elif thickness > self.layerThickness[layer][0]:
            self.layerThickness[layer] = (thickness, normal)

    def isin(self, pt, curves = None):
        """
        returns 1 if <pt> is properly enclosed by the curves.
        """
        #& To do: docstring needs to be updated.  mark 060211.
        # bruce 041214 comment: this might be a good place to exclude points
        # which are too close to the screen to be drawn. Not sure if this
        # place would be sufficient (other methods call c.isin too).
        # Not done yet. ###e
        val = 0
        if not curves: curves = self.curves
        for c in curves:
            if c.selSense == START_NEW_SELECTION or c.selSense == ADD_TO_SELECTION: 
                val = val or c.isin(pt)
            elif c.selSense == OUTSIDE_SUBTRACT_FROM_SELECTION:
                val = val and c.isin(pt)
            elif c.selSense == SUBTRACT_FROM_SELECTION:
                val = val and not c.isin(pt)
        return val

    def pickCircle(self, ptlist, origin, selSense, layer, slabC):
        """
        Add a new circle to the shape.
        """
        c = _Circle(self, ptlist, origin, selSense, slab = slabC)
        self._saveMaxThickness(layer, slabC.thickness, slabC.normal)
        self._cutCookie(layer, c)
        self._addCurve(layer, c)

    def pickline(self, ptlist, origin, selSense, layer, slabC):
        """
        Add a new curve to the shape.
        Args define the curve (see curve) and the selSense operator
        for the curve telling whether it adds or removes material.
        """
        # Review: does "(see curve)" in this docstring
        # refer to class curve in shape.py,
        # which is not used in this module which was split from shape.py?
        # If not, what does it mean?
        # [bruce 071215 question]
        c = shape.pickline(self, ptlist, origin, selSense, slab = slabC)
        self._saveMaxThickness(layer, slabC.thickness, slabC.normal)
        self._cutCookie(layer, c)
        self._addCurve(layer, c)

    def pickrect(self, pt1, pt2, org, selSense, layer, slabC):
        """
        Add a new rectangle to the shape.
        Args define the rectangle and the selSense operator
        for the curve telling whether it adds or removes material.
        """
        c = shape.pickrect(self, pt1, pt2, org, selSense, slab = slabC)
        self._saveMaxThickness(layer, slabC.thickness, slabC.normal)
        self._cutCookie(layer, c)
        self._addCurve(layer, c)

    def _updateBBox(self, curveList):
        """
        Recompute the bounding box for the list of curves
        """
        bbox = BBox()
        for c in curveList[1:]:
            bbox.merge(c.bbox)
        curveList[0] = bbox


    def undo(self, currentLayer):
        """
        This would work for shapes, if anyone called it.
        """
        if self.layeredCurves.has_key(currentLayer):
            curves = self.layeredCurves[currentLayer]
            if len(curves) > 1: 
                curves = curves[:-1]
            self._updateBBox(curves)
            self.layeredCurves[currentLayer] = curves

            ##Kludge to make the undo work.
            self.carbonPosDict[currentLayer] = {} 
            self.hedroPosDict[currentLayer] = {}
            self.bondLayers[currentLayer] = {}
            for c in curves[1:]:
                self._cutCookie(currentLayer, c)

            self.havelist = 0

    def clear(self, currentLayer):
        """
        This would work for shapes, if anyone called it.
        """
        curves = self.layeredCurves[currentLayer]
        curves = []
        self.layeredCurves[currentLayer] = curves
        self.havelist = 0

    def anyCurvesLeft(self):
        """
        Return True if there are curve(s) left, otherwise, False. 
        This can be used by user to decide if the shape object
        can be deleted.
        """
        for cbs in self.layeredCurves.values():
            if len(cbs) > 1:
                return True
        return False

    def combineLayers(self):
        """
        """
        # Experimental code to add all curves and bbox together
        # to make the molmake working. It may be removed later.
        for cbs in self.layeredCurves.values():
            if cbs:
                self.bbox.merge(cbs[0])
                self.curves += cbs[1:]

    def _hashAtomPos(self, pos):
        return int(dot(V(1000000, 1000, 1), floor(pos * 1.2)))

    def _addCurve(self, layer, c):
        """
        Add curve into its own layer, update the bbox
        """
        self.havelist = 0

        if not layer in self.layeredCurves:
            bbox = BBox()
            self.layeredCurves[layer] = [bbox, c]
        else:
            self.layeredCurves[layer] += [c]
        self.layeredCurves[layer][0].merge(c.bbox)

    def _cellDraw(self, color, p0, p1):
        hasSinglet = False
        if type(p1) == type((1,)): 
            v1 = p1[0]
            hasSinglet = True
        else:
            v1 = p1
        if self.dispMode == 'Tubes':
            drawcylinder(color, p0, v1, 0.2)
        else:
            drawsphere(color, p0, 0.5, 1)
            if hasSinglet:
                drawsphere(color, v1, 0.2, 1)
            else:    
                drawsphere(color, v1, 0.5, 1)
            drawline(white, p0, v1)

    def _anotherDraw(self, layerColor):
        """
        The original way of selecting cookies, but do it layer by layer, 
        so we can control how to display each layer.
        """
        if self.havelist:
            glCallList(self.displist.dl)
            return
        glNewList(self.displist.dl, GL_COMPILE_AND_EXECUTE)
        for layer in self.layeredCurves.keys():
            bbox = self.layeredCurves[layer][0]
            curves = self.layeredCurves[layer][1:]
            if not curves:
                continue
            color = layerColor[layer]
            for c in curves:
                c.draw()
            try:
                bblo, bbhi = bbox.data[1], bbox.data[0]
                allCells = genDiam(bblo - 1.6, bbhi + 1.6, self.latticeType)
                for cell in allCells:
                    for pp in cell:
                        p1 = p2 = None
                        if self.isin(pp[0], curves):
                            if self.isin(pp[1], curves):
                                p1 = pp[0]; p2 = pp[1]
                            else: 
                                p1 = pp[0]; p2 = ((pp[1]+pp[0])/2, )
                        elif self.isin(pp[1], curves):
                            p1 = pp[1]; p2 = ((pp[1]+pp[0])/2, )
                        if p1 and p2:
                            self._cellDraw(color, p1, p2) 
            except:
                # bruce 041028 -- protect against exceptions while making display
                # list, or OpenGL will be left in an unusable state (due to the lack
                # of a matching glEndList) in which any subsequent glNewList is an
                # invalid operation. (Also done in chem.py; see more comments there.)
                print_compact_traceback( "bug: exception in shape.draw's displist; ignored: ")
        glEndList()
        self.havelist = 1 #
        return

    def _cutCookie(self, layer, c):
        """
        For each user defined curve, cut the crystal for it, store carbon postion into a
        global dictionary, store the bond information into each layer.
        """
        self.havelist = 0

        bblo, bbhi = c.bbox.data[1], c.bbox.data[0]
        #Without +(-) 1.6, crystal for lonsdaileite may not be right
        allCells = genDiam(bblo - 1.6, bbhi + 1.6, self.latticeType)
        if self.carbonPosDict.has_key(layer):
            carbons = self.carbonPosDict[layer]
        else:
            carbons = {}

        if self.hedroPosDict.has_key(layer):
            hedrons = self.hedroPosDict[layer]
        else:
            hedrons = {}

        if c.selSense == SUBTRACT_FROM_SELECTION:
            markedAtoms = self.markedAtoms
            if not self.bondLayers or not self.bondLayers.has_key(layer):
                return
            else:
                bonds = self.bondLayers[layer]
                for cell in allCells:
                    for pp in cell:
                        ppInside = [False, False]
                        for ii in range(2):
                            if c.isin(pp[ii]): 
                                ppInside[ii] = True
                        if ppInside[0] or ppInside[1]:
                            self._logic0Bond(carbons, bonds, markedAtoms, hedrons, ppInside, pp)
                self. _removeMarkedAtoms(bonds, markedAtoms, carbons, hedrons)

        elif c.selSense == OUTSIDE_SUBTRACT_FROM_SELECTION:
            #& This differs from the standard selection scheme for Shift + Drag. mark 060211.
            #& This is marked for removal.  mark 060320.
            if not self.bondLayers or not self.bondLayers.has_key(layer): 
                return
            bonds = self.bondLayers[layer]
            newBonds = {}; newCarbons = {}; newHedrons = {}; 
            insideAtoms = {}
            newStorage = (newBonds, newCarbons, newHedrons)
            for cell in allCells:
                for pp in cell:
                    pph = [None, None]
                    for ii in range(2):
                        if c.isin(pp[ii]): 
                            pph[ii] = self._hashAtomPos(pp[ii])
                            if bonds.has_key(pph[ii]):
                                insideAtoms[pph[ii]] = pp[ii]

                    if (not pph[0]) and pph[1] and carbons.has_key(pph[1]):
                        pph[0] = self._hashAtomPos(pp[0])
                        if bonds.has_key(pph[0]):
                            newCarbons[pph[1]] = pp[1]
                            newHedrons[pph[0]] = pp[0]
                            if not newBonds.has_key(pph[0]):
                                newBonds[pph[0]] = [(pph[1], 1)]
                            else:
                                newBonds[pph[0]] += [(pph[1], 1)]
            if insideAtoms:
                self._logic2Bond(carbons, bonds, hedrons, insideAtoms, newStorage)
            bonds, carbons, hedrons = newStorage

        elif c.selSense == ADD_TO_SELECTION:
            if self.bondLayers.has_key(layer):
                bonds = self.bondLayers[layer]
            else:
                bonds = {}
            for cell in allCells:
                for pp in cell:
                    pph=[None, None]
                    ppInside = [False, False]
                    for ii in range(2):
                        pph[ii] = self._hashAtomPos(pp[ii]) 
                        if c.isin(pp[ii]):
                            ppInside[ii] = True
                    if ppInside[0] or ppInside[1]:
                        self._logic1Bond(carbons, hedrons, bonds, pp, pph, ppInside)

        elif c.selSense == START_NEW_SELECTION: 
            # Added to make crystal cutter selection behavior 
            # consistent when no modkeys pressed. mark 060320.
            carbons = {}
            bonds = {}
            hedrons = {}

            for cell in allCells:
                for pp in cell:
                    pph = [None, None]
                    ppInside = [False, False]
                    for ii in range(2):
                        pph[ii] = self._hashAtomPos(pp[ii]) 
                        if c.isin(pp[ii]):
                            ppInside[ii] = True
                    if ppInside[0] or ppInside[1]:
                        self._logic1Bond(carbons, hedrons, bonds, pp, pph, ppInside)     

        self.bondLayers[layer] = bonds
        self.carbonPosDict[layer] = carbons
        self.hedroPosDict[layer] = hedrons

        #print "bonds", bonds   
        self.havelist = 1
        return

    def _logic0Bond(self, carbons, bonds, markedAtoms, hedrons, ppInside, pp):
        """
        For each pair of points<pp[0], pp[1]>, if both points are inside the
        curve and are existed carbons, delete the bond, and mark the 
        'should be' removed atoms. Otherwise, delete half bond or 
        change full to half bond accoringly.
        """

        def _deleteHalfBond(which_in):
            """
            Internal function: when the value-- carbon atom is removed 
            from an half bond, delete the half bond.
            """
            markedAtoms[pph[which_in]] = pp[which_in]    
            try:
                values = bonds[pph[0]]
                values.remove((pph[1], which_in))
                bonds[pph[0]] = values
                if len(values) == 0:
                    del bonds[pph[0]]
                #print "Delete half bond: ", pph[0], (pph[1], which_in)
            except:
                print "No such half bond: ", pph[0], (pph[1], which_in)

        def _changeFull2Half(del_id, which_in):
            """
            internal function: If there is a full bond and when the value
            (2nd in a bond pair) carbon atom is removed, change it to half bond
            """
            if not hedrons.has_key(pph[del_id]):
                hedrons[pph[del_id]] = pp[del_id]
            markedAtoms[pph[del_id]] = pp[del_id]
            if bonds.has_key(pph[0]):
                values = bonds[pph[0]]
                idex = values.index(pph[1])
                values[idex] = (pph[1], which_in)
                bonds[pph[0]] = values
                ## print "Change full to half bond: ", pph[0], (pph[1], which_in)

        pph = []
        pph += [self._hashAtomPos(pp[0])]
        pph += [self._hashAtomPos(pp[1])]
        if ppInside[0] and ppInside[1]:
            # Delete full bond
            if carbons.has_key(pph[0]) and carbons.has_key(pph[1]):
                markedAtoms[pph[0]] = pp[0]
                markedAtoms[pph[1]] = pp[1]
                values = bonds[pph[0]]
                values.remove(pph[1])
                bonds[pph[0]] = values
                if len(values) == 0:
                    del bonds[pph[0]]
            # Delete half bond                              
            elif carbons.has_key(pph[0]):
                #markedAtoms[pph[0]] = pp[0]
                _deleteHalfBond(0)
            # Delete half bond
            elif carbons.has_key(pph[1]):
                _deleteHalfBond(1)
        elif ppInside[0]:
            # Full bond becomes half bond, carbon becomes hedron
            if carbons.has_key(pph[0]) and carbons.has_key(pph[1]):
                markedAtoms[pph[0]] = pp[0]
                #_changeFull2Half(0, 1)
            # Delete half bond    
            elif carbons.has_key(pph[0]):
                #markedAtoms[pph[0]] = pp[0]
                _deleteHalfBond(0)
        elif ppInside[1]:
            # Full bond becomes half bond, carbon becomes hedron
            if carbons.has_key(pph[1]) and carbons.has_key(pph[0]):
                _changeFull2Half(1, 0)
            # Delete half bond    
            elif carbons.has_key(pph[1]):
                _deleteHalfBond(1)


    def _logic1Bond(self, carbons, hedrons, bonds, pp, pph, ppInside):
        """
        For each pair of points <pp[0], pp[1]>, create a full bond if 
        necessary and if both points are inside the curve ; otherwise, 
        if one point is in while the other is not, create a half bond if 
        necessary.
        """
        if ppInside[0] and ppInside[1]:
            if (not pph[0] in carbons) and (not pph[1] in carbons):
                if pph[0] in hedrons:
                    del hedrons[pph[0]]
                if pph[1] in hedrons:
                    del hedrons[pph[1]]
                carbons[pph[0]] = pp[0]
                carbons[pph[1]] = pp[1]
                # create a new full bond
                self._createBond(bonds, pph[0], pph[1], -1, True) 
            elif not pph[0] in carbons:
                if pph[0] in hedrons:
                    del hedrons[pph[0]]
                carbons[pph[0]] = pp[0]
                # update half bond to full bond
                self._changeHf2FullBond(bonds, pph[0], pph[1], 1) 
            elif not pph[1] in carbons:
                if pph[1] in hedrons:
                    del hedrons[pph[1]]
                carbons[pph[1]] = pp[1]
                # update half bond to full bond
                self._changeHf2FullBond(bonds, pph[0], pph[1], 0) 
            # create full bond
            else:
                self._createBond(bonds, pph[0], pph[1])

        elif ppInside[0]:
            if (not pph[0] in carbons) and (not pph[1] in carbons):
                if pph[0] in hedrons:
                    del hedrons[pph[0]]
                carbons[pph[0]] = pp[0]
                if not pph[1] in hedrons:
                    hedrons[pph[1]] = pp[1]
                # create new half bond
                self._createBond(bonds, pph[0], pph[1], 0, True) 
            elif not pph[0] in carbons:
                if pph[0] in hedrons:
                    del hedrons[pph[0]]
                carbons[pph[0]] = pp[0]
                #update half bond to full bond
                self._changeHf2FullBond(bonds, pph[0], pph[1], 1) 
            elif not pph[1] in carbons:
                if not pph[1] in hedrons:
                    hedrons[pph[1]] = pp[1]
                # create half bond, with 0 in, 1 out
                self._createBond(bonds, pph[0], pph[1], 0) 
            # create full bond
            else:
                self._createBond(bonds, pph[0], pph[1])

        elif ppInside[1]:
            if (not pph[0] in carbons) and (not pph[1] in carbons):
                if pph[1] in hedrons:
                    del hedrons[pph[1]]
                carbons[pph[1]] = pp[1]
                if not pph[0] in hedrons:
                    hedrons[pph[0]] = pp[0]
                # create new half bond, with 1 in, 0 out
                self._createBond(bonds, pph[0], pph[1], 1, True) 
            elif not pph[0] in carbons:
                if not pph[0] in hedrons:
                    hedrons[pph[0]] = pp[0]
                # create half bond, with 1 in, 0 out
                self._createBond(bonds, pph[0], pph[1], 1) 
            elif not pph[1] in carbons:
                if pph[1] in hedrons:
                    del hedrons[pph[1]]
                carbons[pph[1]] = pp[1]
                # update half bond to full bond
                self._changeHf2FullBond(bonds, pph[0], pph[1], 0) 
            # create full bond
            else:
                self._createBond(bonds, pph[0], pph[1])      
        return

    def _logic2Bond(self, carbons, bonds, hedrons, insideAtoms, newStorage):
        """
        Processing all bonds having key inside the current selection curve.
        For a bond with the key outside, the value inside the selection 
        curve, we deal with it when we scan the edges of each cell. To 
        make sure no such bonds are lost, we need to enlarge the 
        bounding box at least 1 lattice cell.
        """
        newBonds, newCarbons, newHedrons = newStorage

        for a in insideAtoms.keys():
            values = bonds[a]
            newValues = []
            # The key <a> is carbon:
            if carbons.has_key(a):
                if not newCarbons.has_key(a):
                    newCarbons[a] = insideAtoms[a]
                for b in values:
                    if type(b) == type(1): #Full bond
                        # If the carbon inside, keep the bond
                        if insideAtoms.has_key(b):
                            if not newCarbons.has_key(b):
                                newCarbons[b] = insideAtoms[b]
                            newValues += [b]
                        else: # outside carbon, change it to h-bond
                            if not newHedrons.has_key(b):
                                newHedrons[b] = carbons[b]
                            newValues += [(b, 0)]
                    else: # Half bond, keep it
                        if insideAtoms.has_key(b[0]):
                            p = insideAtoms[b[0]]
                        elif hedrons.has_key(b[0]):
                            p = hedrons[b[0]]
                        else: 
                            raise ValueError, (a, b[0])
                        if not newHedrons.has_key(b[0]):
                            newHedrons[b[0]] = p
                        newValues += [b]
            else: # The key <a> is not a carbon
                if not newHedrons.has_key(a):
                    newHedrons[a] = insideAtoms[a]
                for b in values:
                    # Inside h-bond, keep it
                    if insideAtoms.has_key(b[0]):
                        if not newHedrons.has_key(b[0]): 
                            newHedrons[b[0]] = insideAtoms[b[0]]
                        newValues += [b]
            if newValues: newBonds[a] = newValues        

    def _removeMarkedAtoms(self, bonds, markedAtoms, carbons, hedrons):
        """
        Remove all carbons that should have been removed because of 
        the new selection curve. Update bonds that have the carbon as 
        key. For a bond who has the carbon as its value, we'll leave them 
        as they are, untill the draw() call. When it finds a value of a bond 
        can't find its carbon position, either remove the bond if it was a 
        half bond or change it to half bond if it was full bond, and find its 
        carbon position in markedAtoms{}
        """
        for ph in markedAtoms.keys(): 
            if carbons.has_key(ph):
                ## print "Remove carbon: ", ph    
                if bonds.has_key(ph):
                    values = bonds[ph]
                    for b in values[:]:
                        if type(b) == type(1):
                            idex = values.index(b)
                            values[idex]  = (b, 1)
                            ## print "Post processing: Change full to half bond: ", ph, values[idex]
                        else:
                            values.remove(b)
                            ## print "Erase half bond:", ph, b # commented out.  Mark 060205.
                    bonds[ph] = values        
                    if len(values) == 0:
                        del bonds[ph]
                    else:
                        hedrons[ph] = carbons[ph]
                del carbons[ph]


    def _changeHf2FullBond(self, bonds, key, value, which_in):
        """
        If there is a half bond, change it to full bond. Otherwise, create
        a new full bond. 
        <which_in>: the atom which exists before.
        """
        foundHalfBond = False

        if bonds.has_key(key):
            values = bonds[key]
            for ii in range(len(values)):
                if type(values[ii]) == type((1, 1)) and values[ii][0] == value:
                    values[ii] = value
                    foundHalfBond = True                
                    break
            if not foundHalfBond:
                values += [value]
            ## bonds[key] = values
        elif not bonds.has_key(key):
            bonds[key] = [value]


    def _createBond(self, dict, key, value, half_in = -1, new_bond = False):
        """
        Create a new bond if <new_bond> is True. Otherwise, search if
        there is such a full/half bond, change it appropriately if found. 
        Otherwise, create a new bond.
        If <half_in> == -1, it's a full bond; otherwise, it means a half 
        bond with the atom of <half_in> is inside.
        """
        if not key in dict:
            if half_in < 0:
                dict[key] = [value]
            else:
                dict[key] = [(value, half_in)]
        else:
            values = dict[key]
            if half_in < 0:
                if new_bond:
                    values += [value]
                else:
                    found = False
                    for ii in range(len(values)):
                        if type(values[ii]) == type(1):
                            if value == values[ii]:
                                found = True
                                break
                        elif value == values[ii][0]:
                            values[ii] = value
                            found = True
                            break
                    if not found:
                        values += [value]     
            else:
                if new_bond:
                    values +=[(value, half_in)]
                else:
                    try:
                        idex = values.index((value, half_in))
                    except:
                        values += [(value, half_in)]
            dict[key] = values


    def changeDisplayMode(self, mode):
        self.dispMode = mode
        self.havelist = 0

    def _bondDraw(self, color, p0, p1, carbonAt):
        if self.dispMode == 'Tubes':
            drawcylinder(color, p0, p1, 0.2)
        else:
            if carbonAt < 0:
                drawsphere(color, p0, 0.5, 1)
                drawsphere(color, p1, 0.5, 1)
            elif carbonAt == 0:
                drawsphere(color, p0, 0.5, 1)
                drawsphere(color, p1, 0.2, 1)
            elif carbonAt == 1:
                drawsphere(color, p0, 0.2, 1)
                drawsphere(color, p1, 0.5, 1)

            drawline(white, p0, p1)  


    def draw(self, win, layerColor):
        """
        Draw the shape. win, not used, is for consistency among
        drawing functions (and may be used if drawing logic gets
        more sophisticated.

        Find  the bounding box for the curve and check the position of each
        carbon atom in a lattice would occupy for being 'in'
        the shape. A tube representation of the atoms thus selected is
        saved as a GL call list for fast drawing.

        This method is only for crystal-cutter mode. --Huaicai
        """
        if 0: 
            self._anotherDraw(layerColor)
            return

        markedAtoms = self.markedAtoms

        if self.havelist:
            glCallList(self.displist.dl)
            return
        #russ 080225: Moved glNewList into ColorSorter.start for displist re-org.
        #russ 080225: displist side effect allocates a ColorSortedDisplayList.
        ColorSorter.start(self.displist) # grantham 20051205
        try:
            for layer, bonds in self.bondLayers.items():
                color = layerColor[layer]
                self.layeredCurves[layer][-1].draw()
                bonds = self.bondLayers[layer]
                carbons = self.carbonPosDict[layer]
                hedrons = self.hedroPosDict[layer]

                for cK, bList in bonds.items():
                    if carbons.has_key(cK):  p0 = carbons[cK]
                    for b in bList[:]:
                        carbonAt = -1
                        if type(b) == type(1): #Full bond
                            if carbons.has_key(b):
                                p1 = carbons[b]
                            else: 
                                #which means the carbon was removed
                                p1 = markedAtoms[b]
                                #print "Carbon was removed: ", b, p1
                                idex = bList.index(b)
                                bList[idex] = (b, 0)
                                hedrons[b] = p1
                                p1 = (p0 + p1) / 2.0
                                carbonAt = 0
                        else: #Half bond
                            carbonAt = b[1]
                            if b[1]: 
                                if carbons.has_key(b[0]): # otherwise, means the carbon has been removed.
                                    p1 = carbons[b[0]]
                                    if hedrons.has_key(cK):
                                        p0 = hedrons[cK]
                                        p0 = (p0 + p1) / 2.0
                                    else: 
                                        #half bond becomes full bond because of new selection
                                        p0 = carbons[cK]
                                        idex = bList.index(b)
                                        bList[idex] = b[0]
                                else: # remove the half bond
                                    bList.remove(b)
                                    #print "delete half bond: (%d: " %cK, b
                                    if len(bList) == 0: 
                                        del bonds[cK]
                                        break
                                    continue
                            else:
                                if hedrons.has_key(b[0]):
                                    p1 = hedrons[b[0]]
                                    p1 = (p0 + p1) / 2.0
                                else: 
                                    # Which means half bond becomes full bond because of new selection
                                    p1 = carbons[b[0]]
                                    idex = bList.index(b)
                                    bList[idex] = b[0]

                        self._bondDraw(color, p0, p1, carbonAt)    
                    bonds[cK] = bList
        except:
            # bruce 041028 -- protect against exceptions while making display
            # list, or OpenGL will be left in an unusable state (due to the lack
            # of a matching glEndList) in which any subsequent glNewList is an
            # invalid operation. (Also done in chem.py; see more comments there.)
            print "cK: ", cK
            print_compact_traceback( "bug: exception in shape.draw's displist; ignored: ")
        self.markedAtoms = {}

        ColorSorter.finish() # grantham 20051205
        #russ 080225: Moved glEndList into ColorSorter.finish for displist re-org.

        self.havelist = 1 # always set this flag, even if exception happened.

    def buildChunk(self, assy):
        """
        Build Chunk for the cookies. First, combine bonds from
        all layers together, which may fuse some half bonds to full bonds.
        """
        from model.chunk import Chunk
        from model.chem import Atom
        from utilities.constants import gensym

        numLayers = len(self.bondLayers)
        if numLayers:
            allBonds = {}
            allCarbons = {}

            #Copy the bonds, carbons and hedron from the first layer
            for ii in range(numLayers):
                if self.bondLayers.has_key(ii):
                    for bKey, bValue in self.bondLayers[ii].items():
                        allBonds[bKey] = bValue

                    del self.bondLayers[ii]
                    break

            for carbons in self.carbonPosDict.values():
                for cKey, cValue in carbons.items():
                    allCarbons[cKey] = cValue

            for hedrons in self.hedroPosDict.values():        
                for hKey, hValue in hedrons.items():
                    allCarbons[hKey] = hValue

            for bonds in self.bondLayers.values():
                for bKey, bValues in bonds.items():
                    if bKey in allBonds:
                        existValues = allBonds[bKey]
                        for bValue in bValues:
                            if type(bValue) == type((1, 1)):
                                if bValue[1]: 
                                    ctValue = (bValue[0], 0)
                                else: 
                                    ctValue = (bValue[0], 1)
                                if ctValue in existValues:
                                    idex = existValues.index(ctValue)
                                    existValues[idex] = bValue[0]
                                else:
                                    existValues += [bValue]
                            else: 
                                existValues += [bValue]
                        allBonds[bKey] = existValues
                    else: allBonds[bKey] = bValues

            #print "allbonds: ", allBonds
            #print "allCarbons: ", allCarbons

            carbonAtoms = {}
            mol = Chunk(assy, gensym("Crystal", assy))
            for bKey, bBonds in allBonds.items():
                keyHedron = True
                if len(bBonds):
                    for bond in bBonds:
                        if keyHedron:
                            if type(bBonds[0]) == type(1) or (not bBonds[0][1]):
                                if not bKey in carbonAtoms:
                                    keyAtom = Atom("C", allCarbons[bKey], mol) 
                                    carbonAtoms[bKey] = keyAtom
                                else:
                                    keyAtom = carbonAtoms[bKey]
                                keyHedron = False

                        if keyHedron:    
                            if type(bond) != type((1, 1)):
                                raise ValueError, (bKey, bond, bBonds)
                            else:
                                xp = (allCarbons[bKey] + allCarbons[bond[0]])/2.0
                                keyAtom = Atom("X", xp, mol)         

                        if type(bond) == type(1) or bond[1]:
                            if type(bond) == type(1):
                                bvKey = bond
                            else: 
                                bvKey = bond[0]
                            if not bvKey in carbonAtoms:
                                bondAtom = Atom("C", allCarbons[bvKey], mol) 
                                carbonAtoms[bvKey] = bondAtom
                            else: 
                                bondAtom = carbonAtoms[bvKey]
                        else:
                            xp = (allCarbons[bKey] + allCarbons[bond[0]])/2.0
                            bondAtom = Atom("X", xp, mol)     

                        bond_atoms(keyAtom, bondAtom)

            if len(mol.atoms) > 0:
                #bruce 050222 comment: much of this is not needed, since mol.pick() does it.
                # Note: this method is similar to one in BuildCrystal_Command.py.
                assy.addmol(mol)
                assy.unpickall_in_GLPane() 
                    # was unpickparts; not sure _in_GLPane is best (or that
                    # this is needed at all) [bruce 060721]
                mol.pick()
                assy.mt.mt_update()

        return # from buildChunk

    pass # end of class CrystalShape

# end

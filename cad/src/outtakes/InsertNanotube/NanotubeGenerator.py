# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
NanotubeGenerator.py

@author: Will
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

@see http://www.nanoengineer-1.net/mediawiki/index.php?title=Nanotube_generator_dialog
for notes about what's going on here.
"""

from math import atan2, sin, cos, pi, asin
from Numeric import dot

from geometry.VQT import vlen, cross, norm, V
import foundation.env as env
from utilities import debug_flags
from utilities.debug import Stopwatch

from model.chem import Atom

from model.chunk import Chunk

from model.elements import PeriodicTable

from model.bonds import bond_atoms
from geometry.NeighborhoodGenerator import NeighborhoodGenerator

from model.bond_constants import V_GRAPHITE, V_SINGLE
##from bonds_from_atoms import make_bonds
##from buckyball import BuckyBall
from model.bond_constants import atoms_are_bonded

from commands.InsertNanotube.NanotubeGeneratorPropertyManager import NanotubeGeneratorPropertyManager
from command_support.GeneratorBaseClass import GeneratorBaseClass
from utilities.Log import orangemsg, greenmsg ##, redmsg


sqrt3 = 3 ** 0.5

class Chirality:

    def __init__(self, n, m, bond_length):
        self.bond_length = bond_length
        self.maxlen = maxlen = 1.2 * bond_length
        self.maxlensq = maxlen**2
        self.n, self.m = n, m
        x = (n + 0.5 * m) * sqrt3
        y = 1.5 * m
        angle = atan2(y, x)
        twoPiRoverA = (x**2 + y**2) ** .5
        AoverR = (2 * pi) / twoPiRoverA
        self.__cos = cos(angle)
        self.__sin = sin(angle)
        # time to get the constants
        s, t = self.x1y1(0,0)
        u, v = self.x1y1(1./3, 1./3)
        w, x = self.x1y1(0,1)
        F = (t - v)**2
        G = 2 * (1 - cos(AoverR * (s - u)))
        H = (v - x)**2
        J = 2 * (1 - cos(AoverR * (u - w)))
        denom = F * J - G * H
        self.R = (bond_length**2 * (F - H) / denom) ** .5
        self.B = (bond_length**2 * (J - G) / denom) ** .5
        self.A = self.R * AoverR

    def x1y1(self, n, m):
        c, s = self.__cos, self.__sin
        x = (n + .5*m) * sqrt3
        y = 1.5 * m
        x1 = x * c + y * s
        y1 = -x * s + y * c
        return (x1, y1)

    def mlimits(self, z3min, z3max, n):
        if z3max < z3min:
            z3min, z3max = z3max, z3min
        B, c, s = self.B, self.__cos, self.__sin
        P = sqrt3 * B * s
        Q = 1.5 * B * (c - s / sqrt3)
        m1, m2 = (z3min + P * n) / Q, (z3max + P * n) / Q
        return int(m1-1.5), int(m2+1.5) # REVIEW: should this use intRound?

    def xyz(self, n, m):
        x1, y1 = self.x1y1(n, m)
        x2, y2 = self.A * x1, self.B * y1
        R = self.R
        x3 = R * sin(x2/R)
        y3 = R * cos(x2/R)
        z3 = y2
        return (x3, y3, z3)

    def populate(self, mol, length, bn_members = False):

        def add(element, x, y, z, atomtype='sp2'):
            atm = Atom(element, V(x, y, z), mol)
            atm.set_atomtype_but_dont_revise_singlets(atomtype)
            return atm

        evenAtomDict = { }
        oddAtomDict = { }
        bondDict = { }
        mfirst = [ ]
        mlast = [ ]

        for n in range(self.n):
            mmin, mmax = self.mlimits(-.5 * length, .5 * length, n)
            mfirst.append(mmin)
            mlast.append(mmax)
            for m in range(mmin, mmax+1):
                x, y, z = self.xyz(n, m)
                if bn_members:
                    atm = add("B", x, y, z)
                else:
                    atm = add("C", x, y, z)
                evenAtomDict[(n,m)] = atm
                bondDict[atm] = [(n,m)]
                x, y, z = self.xyz(n+1./3, m+1./3)
                if bn_members:
                    atm = add("N", x, y, z, 'sp3')
                else:
                    atm = add("C", x, y, z)
                oddAtomDict[(n,m)] = atm
                bondDict[atm] = [(n+1, m), (n, m+1)]

        # m goes axially along the nanotube, n spirals around the tube
        # like a barber pole, with slope depending on chirality. If we
        # stopped making bonds now, there'd be a spiral strip of
        # missing bonds between the n=self.n-1 row and the n=0 row.
        # So we need to connect those. We don't know how the m values
        # will line up, so the first time, we need to just hunt for the
        # m offset. But then we can apply that constant m offset to the
        # remaining atoms along the strip.
        n = self.n - 1
        mmid = (mfirst[n] + mlast[n]) / 2
        atm = oddAtomDict[(n, mmid)]
        class FoundMOffset(Exception): pass
        try:
            for m2 in range(mfirst[0], mlast[0] + 1):
                atm2 = evenAtomDict[(0, m2)]
                diff = atm.posn() - atm2.posn()
                if dot(diff, diff) < self.maxlensq:
                    moffset = m2 - mmid
                    # Given the offset, zipping up the rows is easy.
                    for m in range(mfirst[n], mlast[n]+1):
                        atm = oddAtomDict[(n, m)]
                        bondDict[atm].append((0, m + moffset))
                    raise FoundMOffset()
            # If we get to this point, we never found m offset.
            # If this ever happens, it indicates a bug.
            raise Exception, "can't find m offset"
        except FoundMOffset:
            pass

        # Use the bond information to bond the atoms
        for (dict1, dict2) in [(evenAtomDict, oddAtomDict),
                               (oddAtomDict, evenAtomDict)]:
            for n, m in dict1.keys():
                atm = dict1[(n, m)]
                for n2, m2 in bondDict[atm]:
                    try:
                        atm2 = dict2[(n2, m2)]
                        if not atoms_are_bonded(atm, atm2):
                            if bn_members:
                                bond_atoms(atm, atm2, V_SINGLE)
                            else:
                                bond_atoms(atm, atm2, V_GRAPHITE)
                    except KeyError:
                        pass

####################################################################
# Endcaps

def addEndcap(mol, length, radius, bondlength):
    sphere_center = V(0, length / 2, 0)
    def walk_great_circle(P, Q, D, R=radius):
        """Given two points P and Q on or near the surface of the
        sphere, use P and Q to define a great circle. Then walk along
        that great circle starting at P and going in the direction of
        Q, and traveling far enough the chord is of length D. P and Q
        are not required to lie exactly on the sphere's surface.
        """
        dP, dQ = P - sphere_center, Q - sphere_center
        dPs = cross(cross(dP, dQ), dP)
        cpart, spart = norm(dP), norm(dPs)
        theta = 2 * asin(0.5 * D / R)
        return sphere_center + R * (cpart * cos(theta) + spart * sin(theta))
    def projectOntoSphere(v, R=radius):
        dv = v - sphere_center
        dvlen = vlen(dv)
        return sphere_center + (R / dvlen) * dv
    def cleanupSinglets(atm):
        for s in atm.singNeighbors():
            s.kill()
        atm.make_enough_bondpoints()
    def addCarbons(chopSpace, R=radius):
        # a buckyball has no more than about 6*r**2 atoms, r in angstroms
        # each cap is ideally a half-buckyball
        for i in range(int(3.0 * R**2)):
            regional_singlets = filter(lambda atm: chopSpace(atm) and atm.is_singlet(),
                                       mol.atoms.values())
            for s in regional_singlets:
                s.setposn(projectOntoSphere(s.posn()))
            if len(regional_singlets) < 3:
                # there won't be anything to bond to anyway, let the user
                # manually adjust the geometry
                return
            singlet_pair = None
            try:
                for s1 in regional_singlets:
                    s1p = s1.posn()
                    for s2 in regional_singlets:
                        if s2.key > s1.key and \
                           vlen(s2.posn() - s1p) < bondlength:
                            singlet_pair = (s1, s2)
                            # break out of both for-loops
                            raise Exception
            except:
                pass
            if singlet_pair is not None:
                # if there is an existing pair of singlets that's close than one bond
                # length, use those to make the newguy, so he'll have one open bond left
                sing1, sing2 = singlet_pair
                owner1, owner2 = sing1.realNeighbors()[0], sing2.realNeighbors()[0]
                newpos1 = walk_great_circle(owner1.posn(), sing1.posn(), bondlength)
                newpos2 = walk_great_circle(owner2.posn(), sing2.posn(), bondlength)
                newpos = 0.5 * (newpos1 + newpos2)
                regional_singlets.remove(sing1)
                regional_singlets.remove(sing2)
            else:
                # otherwise choose any pre-existing bond and stick the newguy on him
                # prefer a bond whose real atom already has two real neighbors
                preferred = filter(lambda atm: len(atm.realNeighbors()[0].realNeighbors()) == 2,
                                   regional_singlets)
                if preferred:
                    sing = preferred[0]
                else:
                    sing = regional_singlets[0]
                owner = sing.realNeighbors()[0]
                newpos = walk_great_circle(owner.posn(), sing.posn(), bondlength)
                regional_singlets.remove(sing)
            ngen = NeighborhoodGenerator(mol.atoms.values(), 1.1 * bondlength)
            # do not include new guy in neighborhood, add him afterwards
            newguy = Atom('C', newpos, mol)
            newguy.set_atomtype('sp2')
            # if the new atom is close to an older atom, merge them: kill the newer
            # atom, give the older one its neighbors, nudge the older one to the midpoint
            for oldguy in ngen.region(newpos):
                if vlen(oldguy.posn() - newpos) < 0.4:
                    newpos = 0.5 * (newguy.posn() + oldguy.posn())
                    newguy.setposn(newpos)
                    ngen.remove(oldguy)
                    oldguy.kill()
                    break
            # Bond with anybody close enough. The newer make_bonds
            # code doesn't seem to handle this usage very well.
            for oldguy in ngen.region(newpos):
                r = oldguy.posn() - newpos
                rlen = vlen(r)
                if (len(newguy.realNeighbors()) < 3 and rlen < 1.1 * bondlength):
                    if rlen < 0.7 * bondlength:
                        # nudge them apart
                        nudge = ((0.7 * bondlength - rlen) / rlen) * r
                        oldguy.setposn(oldguy.posn() + 0.5 * r)
                        newguy.setposn(newguy.posn() - 0.5 * r)
                    bond_atoms(newguy, oldguy, V_GRAPHITE)
                    cleanupSinglets(newguy)
                    cleanupSinglets(oldguy)
            if len(newguy.realNeighbors()) > 3:
                print 'warning: too many bonds on newguy'
            # Try moving the new guy around to make his bonds closer to bondlength but
            # keep him on or near the surface of the sphere. Use Newton's method in
            # three dimensions.
            def error(posn):
                e = (vlen(posn - sphere_center) - radius) ** 2
                for atm in newguy.realNeighbors():
                    e += (vlen(atm.posn() - posn) - bondlength)**2
                return e
            p = newguy.posn()
            for i in range(2):
                h = 1.0e-4
                e0 = error(p)
                gradient = V((error(p + V(h, 0, 0)) - e0) / h,
                             (error(p + V(0, h, 0)) - e0) / h,
                             (error(p + V(0, 0, h)) - e0) / h)
                p = p - (e0 / vlen(gradient)**2) * gradient
            newguy.setposn(p)
            # we may need to reposition singlets
            for atm in ngen.region(newguy.posn()):
                cleanupSinglets(atm)
            cleanupSinglets(newguy)

    def is_north(atm):
        return atm.posn()[1] > length / 2 - 3.0
    def is_south(atm):
        return atm.posn()[1] < -length / 2 + 3.0
    # great circles now computed for the north end
    sphere_center = V(0, length / 2, 0)
    addCarbons(is_north)
    # great circles now computed for the south end
    sphere_center = V(0, -length / 2, 0)
    addCarbons(is_south)
    env.history.message(orangemsg('Nanotube endcap generation is an inexact science. ' +
                                  'Manual touch-up will be required.'))

#################################################################

class NanotubeGenerator(NanotubeGeneratorPropertyManager, GeneratorBaseClass):
    """
    The Nanotube Generator class for the "Build > Nanotube" command.
    """

    cmd = greenmsg("Build Nanotube: ")
    prefix = 'Nanotube'   # used for gensym
    # Generators for DNA, nanotubes and graphene have their MT name generated
    # (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix = True
    # We now support multiple keywords in a list or tuple
    # sponsor_keyword = ('Nanotubes', 'Carbon')
    sponsor_keyword = 'Nanotubes'

    # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        NanotubeGeneratorPropertyManager.__init__(self)
        GeneratorBaseClass.__init__(self, win)

    ###################################################
    # How to build this kind of structure, along with
    # any necessary helper functions

    def gather_parameters(self):
        """
        Return all the parameters from the Property Manager dialog.
        """

        n = self.chiralityNSpinBox.value()
        m = self.chiralityMSpinBox.value()

        self.length = length = self.lengthField.value()
        self.bond_length = bond_length = self.bondLengthField.value()
        self.zdist = zdist = self.zDistortionField.value()
        self.xydist = xydist = self.xyDistortionField.value()
        self.spacing = spacing = self.mwntSpacingField.value()

        twist = pi * self.twistSpinBox.value() / 180.0
        bend = pi * self.bendSpinBox.value() / 180.0
        members = self.typeComboBox.currentIndex()
        endings = self.endingsComboBox.currentText()
        if endings == "Capped" and not debug_flags.atom_debug:
            raise Exception('Nanotube endcaps not implemented yet.')
        numwalls = self.mwntCountSpinBox.value()

        return (length, n, m, bond_length, zdist, xydist,
                twist, bend, members, endings, numwalls, spacing)

    def build_struct(self, name, params, position, mol=None, createPrinted=False):
        """
        Build a nanotube from the parameters in the Property Manger dialog.
        """

        length, n, m, bond_length, zdist, xydist, \
                twist, bend, members, endings, numwalls, spacing = params
        # This can take a few seconds. Inform the user.
        # 100 is a guess on my part. Mark 051103.
        if not createPrinted:
            # If it's a multi-wall tube, only print the "Creating" message once.
            if length > 100.0:
                env.history.message(self.cmd + "This may take a moment...")
        self.chirality = Chirality(n, m, bond_length)
        PROFILE = False
        if PROFILE:
            sw = Stopwatch()
            sw.start()
        xyz = self.chirality.xyz
        if mol == None:
            mol = Chunk(self.win.assy, name)
        atoms = mol.atoms
        mlimits = self.chirality.mlimits
        # populate the tube with some extra carbons on the ends
        # so that we can trim them later
        self.chirality.populate(mol, length + 4 * self.chirality.maxlen, members != 0)

        # Apply twist and distortions. Bends probably would come
        # after this point because they change the direction for the
        # length. I'm worried about Z distortion because it will work
        # OK for stretching, but with compression it can fail. BTW,
        # "Z distortion" is a misnomer, we're stretching in the Y
        # direction.
        for atm in atoms.values():
            # twist
            x, y, z = atm.posn()
            twistRadians = twist * z
            c, s = cos(twistRadians), sin(twistRadians)
            x, y = x * c + y * s, -x * s + y * c
            atm.setposn(V(x, y, z))
        for atm in atoms.values():
            # z distortion
            x, y, z = atm.posn()
            z *= (zdist + length) / length
            atm.setposn(V(x, y, z))
        length += zdist
        for atm in atoms.values():
            # xy distortion
            x, y, z = atm.posn()
            radius = self.chirality.R
            x *= (radius + 0.5 * xydist) / radius
            y *= (radius - 0.5 * xydist) / radius
            atm.setposn(V(x, y, z))

        # Judgement call: because we're discarding carbons with funky
        # valences, we will necessarily get slightly more ragged edges
        # on nanotubes. This is a parameter we can fiddle with to
        # adjust the length. My thought is that users would prefer a
        # little extra length, because it's fairly easy to trim the
        # ends, but much harder to add new atoms on the end.
        LENGTH_TWEAK = bond_length

        # trim all the carbons that fall outside our desired length
        # by doing this, we are introducing new singlets
        for atm in atoms.values():
            x, y, z = atm.posn()
            if (z > .5 * (length + LENGTH_TWEAK) or
                z < -.5 * (length + LENGTH_TWEAK)):
                atm.kill()

        # Apply bend. Equations are anomalous for zero bend.
        if abs(bend) > pi / 360:
            R = length / bend
            for atm in atoms.values():
                x, y, z = atm.posn()
                theta = z / R
                x, z = R - (R - x) * cos(theta), (R - x) * sin(theta)
                atm.setposn(V(x, y, z))

        def trimCarbons():
            # trim all the carbons that only have one carbon neighbor
            for i in range(2):
                for atm in atoms.values():
                    if not atm.is_singlet() and len(atm.realNeighbors()) == 1:
                        atm.kill()

        trimCarbons()
        # if we're not picky about endings, we don't need to trim carbons
        if endings == "Capped":
            # buckyball endcaps
            addEndcap(mol, length, self.chirality.R)
        if endings == "Hydrogen":
            # hydrogen terminations
            for atm in atoms.values():
                atm.Hydrogenate()
        elif endings == "Nitrogen":
            # nitrogen terminations
            dstElem = PeriodicTable.getElement('N')
            atomtype = dstElem.find_atomtype('sp2')
            for atm in atoms.values():
                if len(atm.realNeighbors()) == 2:
                    atm.Transmute(dstElem, force=True, atomtype=atomtype)

        # Translate structure to desired position
        for atm in atoms.values():
            v = atm.posn()
            atm.setposn(v + position)

        if PROFILE:
            t = sw.now()
            env.history.message(greenmsg("%g seconds to build %d atoms" %
                                         (t, len(atoms.values()))))

        if numwalls > 1:
            n += int(spacing * 3 + 0.5)  # empirical tinkering
            params = (length, n, m, bond_length, zdist, xydist,
                      twist, bend, members, endings, numwalls-1, spacing)
            self.build_struct(name, params, position, mol=mol, createPrinted=True)

        return mol
    pass

# end


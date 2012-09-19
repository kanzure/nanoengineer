# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
CrossoverSite_Marker.py

CrossoverSite_Marker object wraps the functionality of identifying
the potential crossoversites between the given DNA segments. It also
creates Handles at these crossover sites. The user can then click on
a hanle to create that crossover. As of 2008-06-01, instance of this class
is being used by MakeCrossovers_GraphicsMode.

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
2008-05-29 - 2008-06-01 : Created
Created to support MakeCrossovers command for v1.1.0

TODO 2008-06-01:
- This is just an initial implmentation and is subjected to heavy revision.
It is created mainly to support the make crossovers command
(a 'nice to have' feature for v1.1.0 implemented just a few days before the
release).
- The search algorithm is slow and needs to be revised.
- Works only for PAM3 model
- Works reliable only for straight dna segments  (curved Dna segments
unsupported for now)
- Add DOCUMENTATION
- Still need to discuss whether this object be better created in GraphicsMode
or the Command part - GM looks more appropriate since most of the
things are related to displaying things in the GM (But the 'identifying
crossover sites' is a general part)
"""

import foundation.env as env
import time
from utilities.constants import black, banana
from dna.commands.MakeCrossovers.MakeCrossovers_Handle import MakeCrossovers_Handle

from geometry.VQT import orthodist, norm, vlen, angleBetween
from Numeric import dot
from model.bonds import bond_direction


from graphics.display_styles.DnaCylinderChunks import get_all_available_dna_base_orientation_indicators
from exprs.instance_helpers import get_glpane_InstanceHolder
from exprs.Arrow           import Arrow
from exprs.Highlightable    import Highlightable

from utilities.prefs_constants import makeCrossoversCommand_crossoverSearch_bet_given_segments_only_prefs_key


MAX_DISTANCE_BETWEEN_CROSSOVER_SITES = 17
#Following is used by the algoritm that searches for neighboring dna segments
#(to a given dnaSegment) to mark crossover sites (atom pairs that will be
#involved in a crossover)
MAX_PERPENDICULAR_DISTANCE_BET_SEGMENT_AXES = 34

MAX_ANGLE_BET_PLANE_NORMAL_AND_AVG_CENTER_VECTOR_OF_CROSSOVER_PAIRS = 32


class CrossoverSite_Marker:
    """
    CrossoverSite_Marker object wraps the functionality of identifying
    the potential crossoversites between the given DNA segments. It also
    creates Handles at these crossover sites. The user can then click on
    a hanle to create that crossover. As of 2008-06-01, instance of this class
    is being used by MakeCrossovers_GraphicsMode.
    @see: MakeCrossovers_GraphicsMode
    """

    def __init__(self, graphicsMode):
        self.graphicsMode = graphicsMode
        self.command = self.graphicsMode.command
        self.win = self.graphicsMode.win
        self.glpane = self.graphicsMode.glpane

        self._allDnaSegmentDict = {}
        self._base_orientation_indicator_dict = {}
        self._DEBUG_plane_normals_ends_for_drawing = []
        self._DEBUG_avg_center_pairs_of_potential_crossovers = []
        self.final_crossover_pairs_dict = {}
        self._final_avg_center_pairs_for_crossovers_dict = {}
        self._raw_crossover_atoms_dict = {}
        self.handleDict = {}

        #This dict contains all ids of all the potential cross over atoms, whose
        #also have their neighbor atoms in the self._raw_crossover_atoms_dict
        self._raw_crossover_atoms_with_neighbors_dict = {}
        self._final_crossover_atoms_dict = {}

    def update(self):
        """
        Does a full update (including exprs handle creation
        @see: self.partialUpdate()
        """
        self.clearDictionaries()
        self._updateAllDnaSegmentDict()
        ##print "***updating crossover sites", time.clock()
        self._updateCrossoverSites()
        ##print "**crossover sites updated", time.clock()
        ##print "***creating handles", time.clock()
        self._createExprsHandles()
        ##print "***%d handles created, new time = %s"%(len(self.handleDict), time.clock())
        self.glpane.gl_update()

    def partialUpdate(self):
        """
        Updates everything but the self.handleDict i.e. updates the crossover sites
        but doesn't create/ update handles.
        #DOC and revise
        @see: MakeCrossovers_GraphicsMode.leftUp()
        @see: MakeCrossovers_GraphicsMode.leftDrag()
        @see: self.update()
        """
        self._allDnaSegmentDict = {}
        self._base_orientation_indicator_dict = {}
        self._DEBUG_plane_normals_ends_for_drawing = []
        self._DEBUG_avg_center_pairs_of_potential_crossovers = []
        self.final_crossover_pairs_dict = {}
        self._final_avg_center_pairs_for_crossovers_dict = {}
        self._raw_crossover_atoms_dict = {}
        #This dict contains all ids of all the potential cross over atoms, whose
        #also have their neighbor atoms in the self._raw_crossover_atoms_dict
        self._raw_crossover_atoms_with_neighbors_dict = {}
        self._final_crossover_atoms_dict = {}
        self._updateAllDnaSegmentDict()
        self._updateCrossoverSites()

    def updateHandles(self):
        """
        Only update handles, don't recompute crossover sites. (This method
        assumes that the crossover sites are up to date.
        """
        self._createExprsHandles()


    def updateExprsHandleDict(self):
        self.clearDictionaries()
        self.update()

    def update_after_crossover_creation(self, crossoverPairs):
        crossoverPairs_id = self._create_crossoverPairs_id(crossoverPairs)

        for d in (self.final_crossover_pairs_dict,
                  self._final_avg_center_pairs_for_crossovers_dict):
            if d.has_key(crossoverPairs_id):
                for atm in d[crossoverPairs_id]:
                    if self._final_crossover_atoms_dict.has_key(id(atm)):
                        del self._final_crossover_atoms_dict[id(atm)]
                del d[crossoverPairs_id]


    def clearDictionaries(self):
        self._allDnaSegmentDict = {}
        self._base_orientation_indicator_dict = {}
        self._DEBUG_plane_normals_ends_for_drawing = []
        self._DEBUG_avg_center_pairs_of_potential_crossovers = []
        self.final_crossover_pairs_dict = {}
        self._final_avg_center_pairs_for_crossovers_dict = {}
        self._raw_crossover_atoms_dict = {}
        self.handleDict = {}

        #This dict contains all ids of all the potential cross over atoms, whose
        #also have their neighbor atoms in the self._raw_crossover_atoms_dict
        self._raw_crossover_atoms_with_neighbors_dict = {}
        self._final_crossover_atoms_dict = {}

    def getAllDnaStrandChunks(self):
        allDnaStrandChunkList = []

        def func(node):
            if node.isStrandChunk():
                return True

            return False
        allDnaStrandChunkList = filter(lambda m:
                                       func(m),
                                       self.win.assy.molecules)

        return allDnaStrandChunkList


    def getAllDnaSegments(self):
        allDnaSegmentList = []

        def func(node):
            if isinstance(node, self.win.assy.DnaSegment):
                allDnaSegmentList.append(node)

        self.win.assy.part.topnode.apply2all(func)
        return allDnaSegmentList

    def getAllDnaSegmentsDict(self):
        """
        """
        return self._allDnaSegmentDict


    def _updateAllDnaSegmentDict(self):
        self._allDnaSegmentDict.clear()
        #If this preferece value is True, the search algotithm will search for
        #the potential crossover sites only *between* the segments in the
        #segment list widget (thus ignoring other segments not in that list)
        if env.prefs[makeCrossoversCommand_crossoverSearch_bet_given_segments_only_prefs_key]:
            allDnaSegments = self.command.getSegmentList()
        else:
            allDnaSegments = self.getAllDnaSegments()

        for segment in allDnaSegments:
            if not self._allDnaSegmentDict.has_key(segment):
                self._allDnaSegmentDict[id(segment)] = segment

    def _updateCrossoverSites(self):
        allSegments = self._allDnaSegmentDict.values()
        #dict segments_searched_for_neighbors is a dictionary object that
        #maintains all the dna segments that have been gone trorugh a
        #'neighbor search' . This is used for speedups.
        segments_searched_for_neighbors = {}

        segments_to_be_searched = self.command.getSegmentList()

        for dnaSegment in segments_to_be_searched:
            self._mark_crossoverSites_bet_segment_and_its_neighbors(
                dnaSegment,
                segments_searched_for_neighbors,
                allSegments )

    def _mark_crossoverSites_bet_segment_and_its_neighbors(self,
                                                           dnaSegment,
                                                           segments_searched_for_neighbors,
                                                           allSegments):
        """
        Identify the crossover sites (crossover atom pairs) between the given
        dnaSegment and all its neighbors (which are also DnaSegments) that fall
        within the specified 'crossover range'.
        @param dnaSegment: The DnaSegment which will be used to search for
        its neighboring segments and then the atoms of these will be scanned
        for potential crossover sites.
        @type  dnaSegment: B{DnaSegment}
        @param segments_searched_for_neighbors: A dictinary object that maintains
        a dictionary of all segments being previously searched for their
        neighbors.  See a comment below that explains its use.
        @type segments_searched_for_neighbors: dict
        """
        #First mark the current dna segment in the dictionary
        #segments_searched_for_neighbors for the following purpose:
        #Suppose there are 4 dna segments A, B , C and D in
        #'allDnasegment' list.
        #Let the current dnaSegment be 'A'. We add it to dict
        #'segments_searched_for_neighbors'.
        #Now we search for its neighbor segments. Now we proceed in the 'for
        #loop' and now the current dnaSegment, whose neighbors need to be
        #searched is segment  'B'. Suppose segment 'B' has 'A' and 'C' as
        #its neighbors.  But we have already searched 'A' to find its
        #neighbors and it should have found out 'B' as its neighbor.
        #So we will skip this instance in the 'sub-for-loop' that loops
        #through allSegmentList to find neighbors of 'B', thereby acheiving
        #speedup. (the 'sub-for loops is: 'for neighbor in allSegments'...)
        segments_searched_for_neighbors[id(dnaSegment)] = dnaSegment
        end1, end2 = dnaSegment.getAxisEndPoints()
        axisVector = norm(end2 - end1)

        #search through allSegments (list) to find neighbors of 'dnaSegment'
        #Also, skip the 'neighbor' that has already been searched for 'its'
        #neighbors in the toplevel 'for loop' (see explanation in the
        #comment above)
        #strandChunksOfdnaSegment is computed only once,while searching the
        #eligible neighbor list. 'strandChunksOfdnaSegment' gives a list
        #of all content strand chunks of the 'dnaSegment' currently being
        #searched for the eligible neighbors.
        strandChunksOfdnaSegment = []

        for neighbor in allSegments:
            if not neighbor is dnaSegment and \
               not segments_searched_for_neighbors.has_key(id(neighbor)):

                ok_to_search, orthogonal_vector = \
                            self._neighborSegment_ok_for_crossover_search(neighbor,
                                                                          end1,
                                                                          axisVector)

                if ok_to_search:
                    #Optimization: strandChunksOfdnaSegment for the
                    #current 'dnaSegment' is computed only once ,while
                    #searching through its eligible neighbors. The
                    #initial value for this list is set to [] before
                    #the sub-for loop that iterates over the allSegments
                    #to find neighborof 'dnaSegment'
                    if not strandChunksOfdnaSegment:
                        strandChunksOfdnaSegment = dnaSegment.get_content_strand_chunks()

                    _raw_crossover_atoms_1 = self._find_raw_crossover_atoms(strandChunksOfdnaSegment, orthogonal_vector)
                    _raw_crossover_atoms_2 = self._find_raw_crossover_atoms(neighbor.get_content_strand_chunks(),
                                                                            orthogonal_vector)

                    self._find_crossover_atompairs_between_atom_dicts(
                        _raw_crossover_atoms_1,
                        _raw_crossover_atoms_2,
                        orthogonal_vector)


    def _neighborSegment_ok_for_crossover_search(
        self,
        neighborSegment,
        reference_segment_end1,
        reference_segment_axisVector):

        ok_for_search = False
        orthogonal_vector = None

        neighbor_end1 , neighbor_end2 = neighborSegment.getAxisEndPoints()
        #Use end1 of neighbor segment and find out the perpendicular
        #distance (and the vector) between this atom and the
        #axis vector of dnaSegment (whose neighbors are being
        #searched). If this distance is less than a specified amount
        #then 'neighbor' is an approved neighbor of 'dnaSegment'
        if neighbor_end1 is not None:
            p1 = reference_segment_end1
            v1 = reference_segment_axisVector
            p2 = neighbor_end1
            dist, orthogonal_dist = orthodist(p1, v1, p2)

            #Check if the orthogonal distance is withing the
            #specified limit.
            if orthogonal_dist <= MAX_PERPENDICULAR_DISTANCE_BET_SEGMENT_AXES:
                ok_for_search = True
                vec = p1 + dist*v1 - p2
                orthogonal_vector = orthogonal_dist*norm(vec)

                if self.graphicsMode.DEBUG_DRAW_PLANE_NORMALS:
                        self._DEBUG_plane_normals_ends_for_drawing.append(
                            (p2, (p2 + orthogonal_vector)) )

        return ok_for_search, orthogonal_vector


    def _find_raw_crossover_atoms(self, chunkList, orthogonal_vector):
        available_raw_crossover_atoms_dict = {}
        for chunk in chunkList:
            indicator_atoms_dict  = \
                                  get_all_available_dna_base_orientation_indicators(
                                      chunk,
                                      orthogonal_vector,
                                      reference_indicator_dict = self._raw_crossover_atoms_dict,
                                      skip_isStrandChunk_check = True)
            available_raw_crossover_atoms_dict.update(indicator_atoms_dict)

        return available_raw_crossover_atoms_dict

    def _find_crossover_atompairs_between_atom_dicts(self,
                                                     atom_dict_1,
                                                     atom_dict_2,
                                                     orthogonal_vector
                                                     ):
        """
        @see: self._filter_neighbor_atompairs()
        """
        crossoverPairs = ()
        #First filter dictionaries so as to include only those atoms whose
        #neighbor atoms are also present in that atom_dict
        new_atom_dict_1, atomPairsList_1 = self._filter_neighbor_atompairs(
            atom_dict_1)
        new_atom_dict_2, atomPairsList_2 = self._filter_neighbor_atompairs(
            atom_dict_2)

        if self.graphicsMode.DEBUG_DRAW_ALL_POTENTIAL_CROSSOVER_SITES:
            self._base_orientation_indicator_dict.update(new_atom_dict_1)
            self._base_orientation_indicator_dict.update(new_atom_dict_2)

        for atompair in atomPairsList_1:
            crossoverPairs =  self._filter_crossover_atompairs(atompair,
                                                               atomPairsList_2,
                                                               orthogonal_vector)


    def _filter_neighbor_atompairs(self, atom_dict):
        """
        @see: self._find_crossover_atompairs_between_atom_dicts()
        """
        new_atom_dict = {}
        atomPairsList = []
        for atm in atom_dict.values():
            for neighbor in atm.neighbors():
                if atom_dict.has_key(id(neighbor)):
                    if self._final_crossover_atoms_dict.has_key(id(atm)) and \
                       self._final_crossover_atoms_dict.has_key(id(neighbor)):
                        continue #skip this iteration

                    if self.graphicsMode.DEBUG_DRAW_ALL_POTENTIAL_CROSSOVER_SITES:
                        if not new_atom_dict.has_key(id(neighbor)):
                            new_atom_dict[id(neighbor)] = neighbor
                        if not new_atom_dict.has_key(id(atm)):
                            new_atom_dict[id(atm)] = atm

                    #@@BUG: What if both neighbors of atm are in atom_dict_1??
                    #In that case, this code creates two separate tuples with
                    #'atm' as a common atom in each.
                    #MAKE SURE TO append atoms in the same order as
                    #their bond_direction. Example, if the bond is atm --> neighbor
                    #append them as (atm, neighbor) . If bond is from
                    #neighbor > atm, append them as (neighbor, atm).
                    #Possible BUG: This method DOES NOT handle case with
                    #bond_direction = 0 (simply assumes a random order)
                    if bond_direction(atm, neighbor) == - 1:
                        atomPairsList.append((neighbor, atm))
                    else:
                        atomPairsList.append((atm, neighbor))

        return new_atom_dict, atomPairsList


    def _filter_crossover_atompairs(self, atomPair,
                                    otherAtomPairList,
                                    orthogonal_vector):
        """
        TODO: REVISE THIS
        """

        for other_pair in otherAtomPairList:
            mate_found, distance, pairs = self._are_crossover_atompairs(atomPair,
                                                                        other_pair,
                                                                        orthogonal_vector)

        return None

    def _are_crossover_atompairs(self,
                                 atomPair1,
                                 atomPair2,
                                 orthogonal_vector):
        """
        """
        atm1, neighbor1 = atomPair1
        center_1 = (atm1.posn() + neighbor1.posn())/2.0
        atm2, neighbor2 = atomPair2
        center_2 = (atm2.posn() + neighbor2.posn())/2.0

        distance = vlen(center_1 - center_2)
        if  distance > MAX_DISTANCE_BETWEEN_CROSSOVER_SITES:
            return False, distance, ()

        #@NOTE: In self._filter_neighbor_atompairs() where we create the
        #atompairlists, we make sure that the atoms are ordered in +ve bond_direction
        #Below, we just check the relative direction of atoms.

        #@@@@@METHOD TO BE WRITTEN FURTHER

        centerVec = center_1 - center_2

        if self.graphicsMode.DEBUG_DRAW_AVERAGE_CENTER_PAIRS_OF_POTENTIAL_CROSSOVERS:
            self._DEBUG_avg_center_pairs_of_potential_crossovers.append((center_1, center_2))

        theta = angleBetween(orthogonal_vector, centerVec)

        if dot(centerVec, orthogonal_vector) < 1:
            theta = 180.0 - theta

        if abs(theta) > MAX_ANGLE_BET_PLANE_NORMAL_AND_AVG_CENTER_VECTOR_OF_CROSSOVER_PAIRS:
            return False, distance, ()

        crossoverPairs = (atm1, neighbor1, atm2, neighbor2)

        for a in crossoverPairs:
            if not self._final_crossover_atoms_dict.has_key(id(a)):
                self._final_crossover_atoms_dict[id(a)] = a

        #important to sort this to create a unique id. Makes sure that same
        #crossover pairs are not added to the self.final_crossover_pairs_dict
        crossoverPairs_id = self._create_crossoverPairs_id(crossoverPairs)

        if not self.final_crossover_pairs_dict.has_key(crossoverPairs_id):
            self._final_avg_center_pairs_for_crossovers_dict[crossoverPairs_id] = (center_1, center_2)
            self.final_crossover_pairs_dict[crossoverPairs_id] = crossoverPairs

        return True, distance, crossoverPairs

    def _create_crossoverPairs_id(self, crossoverPairs):
        #important to sort this to create a unique id. Makes sure that same
        #crossover pairs are not added to the self.final_crossover_pairs_dict
        crossoverPairs_list = list(crossoverPairs)
        crossoverPairs_list.sort()
        crossoverPairs_id = tuple(crossoverPairs_list)
        return crossoverPairs_id

    def _createExprsHandles(self):
        self.handleDict = {}
        for crossoverPair_id in self._final_avg_center_pairs_for_crossovers_dict.keys():
            handle = self._expr_instance_for_vector(
                self._final_avg_center_pairs_for_crossovers_dict[crossoverPair_id],
                self.final_crossover_pairs_dict[crossoverPair_id])

            if not self.handleDict.has_key(id(handle)):
                self.handleDict[id(handle)] = handle

    def removeHandle(self, handle):
        if self.handleDict.has_key(id(handle)):
            del self.handleDict[id(handle)]
            self.glpane.set_selobj(None)
            self.glpane.gl_update()


    def _expr_instance_for_vector(self, pointPair, crossoverPairs):
        ih = get_glpane_InstanceHolder(self.glpane)
        expr = self._expr_for_vector(pointPair, crossoverPairs)
        expr_instance = ih.Instance( expr,
                                     skip_expr_compare = True)
        return expr_instance


    def _expr_for_vector(self, pointPair, crossoverPairs):
        handle = MakeCrossovers_Handle(pointPair[0],
                                       pointPair[1],
                                       self.glpane.scale,
                                       crossoverSite_marker = self,
                                       command = self.command,
                                       crossoverPairs = crossoverPairs )
        return handle


    def _expr_for_vector_ORIG(self, pointPair):
        # WARNING: this is not optimized -- it recomputes and discards this expr on every access!
        # (But it looks like its caller, _expr_instance_for_imagename, caches the expr instances,
        #  so only the uninstantiated expr itself is recomputed each time, so it's probably ok.
        #  [bruce 080323 comment])
        arrow = Highlightable(Arrow(
            color = black,
            arrowBasePoint = pointPair[0],
            tailPoint = pointPair[1],
            tailRadius = 0.8,
            scale = self.glpane.scale),

            Arrow(
                color = banana,
                arrowBasePoint = pointPair[0],
                tailPoint = pointPair[1],
                tailRadius = 0.8,
                scale = self.glpane.scale)
            )

        return arrow

    def get_plane_normals_ends_for_drawing(self):
        return self._DEBUG_plane_normals_ends_for_drawing

    def get_avg_center_pairs_of_potential_crossovers(self):
        return self._DEBUG_avg_center_pairs_of_potential_crossovers

    def get_base_orientation_indicator_dict(self):
        return self._base_orientation_indicator_dict

    def get_final_crossover_atoms_dict(self):
        return self._final_crossover_atoms_dict

    def get_final_crossover_pairs(self):
        return self.final_crossover_pairs_dict.values()
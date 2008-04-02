$Id$


[a.posn() for a in baseatoms]

get 3 positions


routine:

get the 3 transformed positions (either way)

get the coordsystems for thinking about the Pls

turn Pl relative info <-> Pl position

to get a Pl: do that on both sides, then average

from a Pl: look from both sides, do that to get relative info (need coords then too)




how do we transform Pl? just look at its rel pos in a base frame, store that.

(get right origin, then matrix multiply. a quat can do that, right? not sure how to make one that does it...
 oh maybe a constructor does that.)

    Q(x, y, z), where x, y, and z are three orthonormal vectors describing a
    right-handed coordinate frame, is the quaternion that rotates the standard
    axes into that reference frame (the frame has to be right handed, or there's
    no quaternion that can do it!)

so if i have a "base frame" in model space,
then using the Q from it, I can turn rel coords into abs ones with rot,
and the reverse using unrot.

and i can do this for a lot of vectors at once.
just like mols do.

but that is not very useful now, the baseframe is used for only 2 Pls.

the baseframe data is an origin and rel_to_abs_quat.





    ss2 = Ss2.posn() # S_u, in PAM5 form
    ss1 = Ss1.posn() # S_d, in PAM5 form
    gv = Gv.posn()


    origin, rel_to_abs_quat, y_m = baseframe_from_pam5_data(ss1, gv, ss2)
    
    # now go on to get pam3 atom positions:

        # [for y_m from pam3 data variant, see my mail to ericd]

    x_aprime = X_APRIME
    
    ax_sdframe = V(x_aprime, y_m, 0) # Ax position, relative to baseframe_d

    Sprime_d_sdframe = SPRIME_D_SDFRAME # Ss3-1 pos, rel to baseframe_d






def baseframe_from_pam3_data():
    
    ss2 = Ss2.posn() # S_u, in PAM3 form
    ss1 = Ss1.posn() # S_d, in PAM3 form
    ax = Ax.posn()

##    origin = ss1 # WRONG



    origin, rel_to_abs_quat, y_m = baseframe_from_pam3_data(ss1, ax, ss2)

    # now use baseframe to get pam5 atom positions

    # we just need the Gv pos, restored from data on the sugars

    # (get two and average them; store each as rel vector, convert to abs)

    
class DnaLadder_PAM_converter(object):
    """
    Given a DnaLadder for a duplex, implement PAM conversion operations
    (in versions which modify the model, or which can be used transiently
     during mmp writing) and construct context menu entries to offer them.
    
    @note: for Duplex ladders only (not for single strand domains)
    """
    def __init__(self, ladder):
        self.ladder = ladder
    pass




class PAM_converter_duplex_PAM5(PAM_converter_DnaLadder):
    def _compute_baseframes(self):
        for rail in self.ladder.all_rails(): #k want them in order
            baseatoms = rail.baseatoms
            posns = [a.posn() for a in baseatoms]

        
    def convert_to_PAM3_in_place(self):
        """
        @note: also used by dna updater when reading PAM5
               that should be displayed as PAM3
        """
        # always on: store_plus5_data = True
        ladder = self.ladder
        # note: the dna updater enforces "same pam model" on the
        # atoms in any one DnaLadder [###VERIFY].


        # BUG: needs to detect errors before actually changing things.
        # So first, scan bases and get baseframes, detecting math errors 
        for i in range(len(ladder)):
            ssd, gv, ssu = ladder.get_basepair_atoms(i) # ssu might be None, but same for all basepairs if so # IMPLEM
            # for now assume all three atoms exist
            assert ssu is not None # can fail if i forget to check this earlier, for single strands
            assert gv is not None # ditto
            assert ssd is not None # should never fail
            
            # let's say we're in a pam5 duplex

            self.convert_basepair_to_PAM3_in_place(i, ssd, gv, ssu)
                # transmute and move atoms, store +5 data, and store (or return? so no pass i?) info for later use on Pls

            continue

        # now kill the Pl atoms and rebond their neighbors
        # (one or both of which are in self -- what if other one not converted?? ######)

        # (might have to do this later, if multiple ladders??)

        # natural order of operations:
        # - scan basepairs to determine errors, compute and save frames
        # - rule out errors -- for an op on selection, you might do this for entire sel before changing anything
        
        pass

    def convert_basepair_to_PAM3_in_place(self, i, ssd, gv, ssu):
        """
        #doc:
        transmute and move atoms, store +5 data,
        and store (or return? so no pass i?) info for later use on Pls
        """
        if ssd is not None:
            ssd.mvElement(Ss3)
        if ssu is not None:
            ssu.mvElement(Ss3)
        if gv is not None:
            gv.mvElement(Ax3)

    def convert_to_PAM5_in_place(self):
        """
        """




        # now create actual Pl atoms, position them, and rebond them.
        # (use common code with writemmp, which uses virtual Pl atoms.)

        



# TODO: did i ever compare pam models when merging ladders, and reject merge if different?
# note, i also need to reject merge if the desired pams differ, for edit or for save.
# does that cover this or not? i think not -- but i should do this before merge.

# i.e.:
# - when forming ladders, exclude pam mismatch between atoms themselves, or desired pam attrs.
# - then convert ladders as desired by their attrs -- updater should notice all that need this
# - then merge, sufficient to compare dsired attrs -- unless there were conversion errors.
#   - errors should set ladder.error, and should be visible, and should prevent the entire conversion op for entire ladder.

# digr: would it work for atom display style change to also stop ladders from joining? (or to have max ladder length of 1??)


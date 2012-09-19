# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
moviefile.py -- classes and other code for interpreting movie files
(of various formats, once we have them)

@author: Bruce
@version: $Id$
@copyright: 2005-2007 Nanorex, Inc.  See LICENSE file for details.
"""

# note that in future there's more than one class, and a function to figure out the right one to use
# for an existing file, or to be told this (being told the format) for a new file we'll cause to be made...
#
# so the external code should rarely know the actual classnames in this file!

# these imports are anticipated, perhaps not all needed
import os, sys
from struct import unpack # fyi: used for old-format header, no longer for delta frames
## from VQT import A
from numpy.oldnumeric import array, Int8
from utilities import debug_flags
from utilities.debug import print_compact_stack, print_compact_traceback
import foundation.env as env

def MovieFile(filename): #bruce 050913 removed history arg, since all callers passed env.history
    """
    Given the name of an existing old-format movie file,
    return an object which can read frames from it
    (perhaps only after receiving further advice from its client code,
     like the absolute atom positions for one specific frame).
       The returned object should also know whatever can be known
    from the moviefile itself about the movie... like number of frames and atoms...
    for the old format, that's all there is.
       In case of a fatal error, print an appropriate message to env.history
    and return None. We might also print warnings to history (I don't know #k).
       In future, when new format is available, we'll detect the format in the file
    and open it in the proper way, perhaps also taking optional arguments for a trace filename,
    perhaps handling files that have not yet been finished or perhaps not yet even started, etc....
       See also the docstring of class OldFormatMovieFile.
    """
    # for now, assume old format, and assume file exists and has reached its final size.
    reader = OldFormatMovieFile_startup( filename)
    if reader.open_and_read_header_errQ():
        return None
    return OldFormatMovieFile( reader)

class OldFormatMovieFile_startup:
    #e maybe make these same obj, so easier to recheck header later, and big one needs invalid state anyway
    def __init__(self, filename): #bruce 050913 removed history arg
        self.filename = filename
        self.fileobj = None
        self.errcode = None
    def open_and_read_header_errQ(self):
        # because we assume file is fully written, we can do all this stuff immediately for now:
        #e try/except too?
        self.open_file()
        self.read_header()
        return self.errcode
    def open_file(self):
        assert not self.fileobj #e if we relax this, then worry about whether we should seek to start of file
        self.fileobj = open(self.filename,'rb') ###@@@ missing file is possible when we reopen after closing; this is caught below
    def read_header(self):
        # assume we're at start of file
        # Read header (4 bytes) from file containing the number of frames in the moviefile.
        self.totalFramesActual = unpack('i',self.fileobj.read(4))[0]
        # Compute natoms
        filesize = os.path.getsize(self.filename)
        self.natoms = (filesize - 4) / (self.totalFramesActual * 3)
        if self.natoms * (self.totalFramesActual * 3) != (filesize - 4):
            msg = "Movie file [%s] has invalid length -- might be truncated or still being written." % self.filename
                # (Without knowing correct natoms (as we don't in this case), we can't reliably say whether it has
                #  missing frames, partly written frames, etc.)
                # For new format files this would only be a warning; we could use the whole frames.
                # But for old-format files, it means our calc of natoms will be wrong for them! So it's fatal.
            self.error(msg)
            return # how far do we return, on error?? (I mean, should we raise an exception instead?) ###k
        return
    def error(self, msg):
        self.errcode = msg or "error" # public attr for callers to see...
        from utilities.Log import redmsg
        env.history.message( redmsg( msg))
        return
    def delta_frame_bytes(self, n):
        """
        return the bytes of the delta frame which has index n (assuming our file is open and n is within legal range)
        """
        # note: the first one has index 1 (since it gives delta from time 0 to time 1).
        assert n > 0
        nbytes = self.natoms * 3 # number of bytes in frame (if complete) -- no relation to frame index n
        filepos = ((n-1) * nbytes) + 4
        try:
            # several things here can fail if file is changing on disk in various ways
            if not self.fileobj:
                # this might not yet ever happen, not sure.
                self.open_file() #e check for error? check length still the same, etc? 
            self.fileobj.seek( filepos) ####@@@@ failure here might be possible if file got shorter after size measured -- not sure
            res = self.fileobj.read(nbytes)
            assert len(res) == nbytes # this can fail, if file got shorter after we measured its size...
        except:
            # might be good to detect, warn, set flag, return 0s.... ####@@@@ test this
            if debug_flags.atom_debug: # if this happens at all it might happen a lot...
                print_compact_traceback( "atom_debug: ignoring exception reading delta_frame %d, returning all 00s: " % n)
            res = "\x00" * nbytes
            assert len(res) == nbytes, "mistake in python zero-byte syntax" # but I checked it, should be ok
        return res
    def close(self):
        if self.fileobj:
            self.fileobj.close()
        self.fileobj = None
    close_file = close
    def destroy(self):
        self.close()
        return # no other large state in this object
    pass 

class OldFormatMovieFile: #bruce 050426 
    """
    Know the filename and format of an existing moviefile, and enough about it to read requested frames from it
    and report absolute atom positions (even if those frames, or all frames in the file, are differential frames).
       Provide methods for renaming it (actually moving or copying the file), when this is safe.
       Sometimes keep it open with a known file pointer, for speed.
       Sometimes keep cached arrays of absolute positions (like key frames but perhaps computed rather than taken from the file),
    either for speed or since it's the only way to derive absolute positions from delta frames in the file.
       [#e Someday we'll work even on files that are still growing, but this probably won't be tried for Alpha5.]
       What we *don't* know includes: anything about the actual atoms (if any) being repositioned as this file is read;
    anything about associated files (like a tracefile) or sim run parameters (if any), except whatever might be needed
    to do our job of interpreting the one actual moviefile we know about.
       Possible generalizations: really we're one kind of "atom-set trajectory", and in future there might be other kinds
    which don't get their data from files. (E.g. an object to morph atom-set-positions smoothly between two endpoints.)
    """
    ##e How to extend this class to the new movie file format:
    # split it into one superclass with the toplevel caching-logic,
    # and two subclasses (one per file format) with the lower-level skills
    # specific to how often those files contain key frames (never vs. regularly),
    # and their other differences. But note that this obj's job is not really to interpret
    # the general parts of the new-format file header, only the "trajectory part".
    # So probably some other object would parse the header and only then hand off the rest of the file
    # to one of these.
    def __init__(self, filereader):
        self.filereader = filereader # this has file pointer, knows filename & header, can read raw frames

        #e someday:
        # conceivably the file does not yet exist and this is not an error
        # (if we're being used on a still-growing file whose producer didn't quite start writing it yet),
        # so let's check these things as needed/requested rather than on init.
        # For now we'll just "know that we don't know them".
        # This might be best done using __getattr__... and perhaps some quantities
        # are different each time we look (like file length)... not yet decided.
        #
        # now: just assume the file is complete before we're called, and grab these things from filereader.

        # Q: But does the caller need to tell us the set of starting atom positions,
        # in case the file doesn't? What if it doesn't know (for new-format file being explored)?
        # A: the way it tells us is by calling donate_immutable_cached_frame if it needs to,
        # on any single frame it wants (often but not always frame 0).
        # Re bug 1297, it better give us sim-corrected positions rather than raw ones, for any open bonds!
        # (For more info on that see comment in get_sim_posns.) [bruce 060111]

        self.totalFramesActual = filereader.totalFramesActual
        self.natoms = filereader.natoms # maybe these should be the same object... not sure
        self.temp_mutable_frames = {}
        self.cached_immutable_frames = {} #e for some callers, store a cached frame 0 here

    def get_totalFramesActual(self):
        return self.totalFramesActual
    def matches_alist(self, alist):
        return self.natoms == len(alist) #e could someday check more...
    def recheck_matches_alist(self, alist):
        return self.matches_alist(alist) ###@@@ stub, fails to recheck the file! should verify same header and same or larger nframes.
    def destroy(self):
        self.cached_immutable_frames = self.temp_mutable_frames = None
        self.filereader.destroy()
        self.filereader = None

    def frame_index_in_range(self, n):
        assert type(n) == type(1)
        return 0 <= n <= self.totalFramesActual # I think inclusive at both ends is correct...

    def ref_to_transient_frame_n(self, n):
        """
        [This is meant to be the main external method for retrieving our atom positions,
         when the caller cares about speed but doesn't need to keep this array
         (e.g. when it's playing us as a movie).]
        
        Return a Numeric array containing the absolute atom positions for frame n.
        Caller promises not to modify this array, and to never use it again after
        the next time anything calls any(??) method of this object. (Since we might
        keep modifying and returning the same mutable array, each time this method
        is called for the next n during a scan.)
           [#e Someday we might need to document some methods that are safe to call even while
        the caller still wants to use this array, and/or provide a scheme by which the
        caller can ask whether it's holding of that array remains valid or not -- note that
        several callers might have "different holdings of the same physical array" for which
        that answer differs. Note that a "copy on write" scheme (an alternative to much of this)
        might be better in the long run, but I'm not sure it's practical for Numeric arrays,
        or for advising self on which frames to keep and which to discard.
        """
        res = self.copy_of_frame(n) # res is owned by this method-run...
        self.donate_mutable_known_frame(n, res) # ... but not anymore!
            # But since we're a private implem, we can depend on res still
            # being valid and constant right now, and until the next method
            # on self is called sometime after we return.
        return res
    
    def copy_of_frame(self, n):
        """
        Return the array of absolute atom positions corresponding to
        the specified frame-number (0 = array of initial positions).
        If necessary, scan through the file as needed (from a key frame, in future format,
        or from the position of a frame whose abs posns we have cached, in old format)
        in order to figure this out.
        """
        assert self.frame_index_in_range(n)
        n0 = self.nearest_knownposns_frame_index(n)
        frame0 = self.copy_of_known_frame_or_None(n0) # an array of absposns we're allowed to modify, valid for n0
        assert frame0 is not None # don't test it as a boolean -- it might be all 0.0 which in Numeric means it's false!
        while n0 < n:
            # move forwards using a delta frame (which is never cached, tho this code doesn't need to know that)
            # (##e btw it might be faster to read several at once and combine them into one, or add all at once, using Numeric ops!
            #  I'm not sure, since intermediate states would use 4x the memory, so we might do smaller pieces at a time...)
            n0 += 1
            df = self.delta_frame(n0) # array of differences to add to frame n0-1 to get frame n0
            try:
                frame0 += df # note: += modifies frame0 in place (if it's a Numeric array, as we hope); that's desired
            except ValueError: # frames are not aligned -- happens when slider reaches right end
                print "frames not aligned; shapes:",frame0.shape, df.shape
                raise
        while n0 > n:
            # (this never happens if we just moved forwards, but there's no need to "confirm" or "enforce" that fact)
            # move backwards using a delta frame
            # (btw it might be faster to read all dfs forwards to make one big one to subtract all at once...
            #  or perhaps even to read them all at once into a single Numeric 2d array, and turn them into
            #  one big one using Numeric ops! ###e)
            df = self.delta_frame(n0)
            n0 -= 1 # note: we did this after grabbing the frame, not beforehand as above
            frame0 -= df
        #e future:
        #e   If we'd especially like to keep a cached copy for future speed, make one now...
        #e   Or do this inside forward-going loop?
        #e   Or in caller, having it stop for breath every so many frames, perhaps also to process user events?
##        if 0: #bruce 060111 debug code (two places), safe but could be removed when not needed (tiny bit slow) [bruce 060111] ###@@@
##            # maybe print coords for one atom
##            import runSim
##            if runSim.debug_all_frames:
##                ii = runSim.debug_all_frames_atom_index
##                print "copy_of_frame %d[%d] is" % (n, ii), frame0[ii]
        return frame0

    def donate_mutable_known_frame(self, n, frame):
        """
        Caller has a frame of absolute atom positions it no longer needs --
        add this to our cache of known frames, marked as able to be modified further as needed
        (i.e. as its data not needing to be retained in self after it's next returned by copy_of_known_frame_or_None).
        This optimizes serial scans of the file, since the donated frame tends to be one frame away
        from the next desired frame.
        """
        self.temp_mutable_frames[n] = frame
            # it's probably ok if we already had one for the same n and this discards it --
            # we don't really need more than one per n
        ###e do something to affect the retval of nearest_knownposns_frame_index?? it should optimize for the last one of these being near...
        return

    def donate_immutable_cached_frame(self, n, frame): # (this is how client code can tell us abs posns to start with)
        """
        Caller gives us the frame of abs positions for frame-index n,
        which we can keep and will never modify (in case caller wants to keep using it too),
        and caller also promises to never modify it (so we can keep trusting and copying it).
        This is the only way for client code using us on an all-differential file
        can tell us a known absolute frame from which other absolute frames can be derived.
        Note that that known frame need not be frame 0, and perhaps will sometimes not be
        (I don't know, as of 050426 2pm). [As of shortly before 060111 it can indeed be any frame.]
           Note: these positions better be sim-corrected (as if X was H) rather than raw, for any open bonds!
        Otherwise we'll get bug 1297. In fact, they really need to be a copy of positions the sim had,
        not just newly corrected H positions (see get_sim_posns comment for more info). [bruce 060111]
        """
        self.cached_immutable_frames[n] = frame
            # note: we only need one per n! so don't worry if this replaces an older one.
        ###e do something to affect the retval of nearest_knownposns_frame_index??
        return
    
    def copy_of_known_frame_or_None(self, n):
        """
        If we have a mutable known frame at index n, return it
        (and forget it internally since caller is allowed to modify it).
        If not, we should have an immutable one, or the file should have one (i.e. a key frame).
        Make a copy and return it.
        If we can't, return None (for some callers this will be an error; detecting it is up to them).
        """
        try:
            return self.temp_mutable_frames.pop(n)
        except KeyError:
            try:
                #e we don't yet support files with key frames, so a cached one is our only chance.
                frame_notouch = self.cached_immutable_frames[n]
            except KeyError:
                return None
            else:
                return + frame_notouch # the unary "+" makes a copy (since it's a Numeric array)
        pass

    def nearest_knownposns_frame_index(self, n):
        """
        Figure out and return n0, the nearest frame index to n
        for which we already know the absolute positions, either since it's a key frame in the file
        or since we've kept a cached copy of the positions (or been given those positions by our client code) --
        either a mutable copy or an immutable one.
        (This index is suitable for passing to copy_of_known_frame_or_None, but that method might or might not
         have to actually copy anything in order to come up with a mutable frame to return.)
           By "nearest", we really mean "fastest to scan over the delta frames from n0 to n",
        so if scanning forwards is faster then we should be biased towards returning n0 < n,
        but this issue is ignored for now (and will become barely relevant once we use the new file format
        with frequent occurrence of key frames).
           It's not an error if n is out of range, but the returned n0 will always be in range.
           If we can't find *any* known frame, return None (but for most callers this will be an error). ###e better to asfail??
        """
        # It's common during sequential movie playing that the frame we want is 1 away from what we have...
        # so it's worth testing this quickly, at least for the mutable frames used during that process.
        # (In fact, this is probably more common than an exact match! So we test it first.)
        if n - 1 in self.temp_mutable_frames:
            return n - 1
        if n + 1 in self.temp_mutable_frames:
            return n + 1
        # It's also common than n is already known, so test that quickly too.
        if n in self.temp_mutable_frames or n in self.cached_immutable_frames:
            return n
        # No exact match. In present code, we won't have very many known frames,
        # so it's ok to just scan them all and find the one that's actually nearest.
        # (For future moviefile format with frequent key frames, we'll revise this quite a bit.)
        max_lower = too_low = -1
        min_higher = too_high = 100000000000000000000000 # higher than any actual frame number (I hope!)
        for n0 in self.temp_mutable_frames.keys() + self.cached_immutable_frames.keys():
            if n0 < n:
                max_lower = max( max_lower, n0)
            else:
                min_higher = min( min_higher, n0)
        if max_lower > too_low and min_higher != too_high:
            # which is best: scanning forwards by n - max_lower, or scanning backwards by min_higher - n ?
            if n - max_lower <= min_higher - n:
                return max_lower
            else:
                return min_higher
        elif max_lower > too_low:
            return max_lower
        elif min_higher != too_high:
            return min_higher
        else:
            assert 0, "no known frame!" # for now, since I think this should never happen (unless file of new format is very incomplete)
            return None
        pass

    def delta_frame(self, n):
        """
        return the delta frame with index n, as an appropriately-typed Numeric array
        """
        bytes = self.filereader.delta_frame_bytes(n)
        ## older code: delta = A(unpack('bbb',file.read(3)))*0.01
        # (with luck, reading the whole frame at once will be a nice speedup for fast-forwarding...)
        res = array(bytes,Int8)
        res.shape = (-1,3)
        res = res * 0.01
            #e it might be nice to move that multiply into caller (for speedup and error-reduction):
            #bruce 060110 comment: 0.01 is not represented exactly, so including it here might introduce cumulative
            # roundoff errors into callers who add up lots of delta frames! Let's estimate the size: assume 53 significant bits,
            # and typical values within 10^6 of 0, and need for 10^-3 precision, then we're using about 30 bits,
            # so an error in last bit, accumulating badly, still has say 1/4 * 2^23 = >> 10^6 steps to cause trouble...
            # and I think adding or subtracting this delta frame should reverse properly (same error gets added or removed),
            # except perhaps for special coord values that won't occur most times, so if true, what matters is movie length
            # rather than how often user plays it forwards and back. So I think we can tolerate this error for A7, at least,
            # and I think we can rule it out as a possible cause of bug 1297 (and an experiment also seems to rule that out).
            # [For the true cause, see 060111 comment in get_sim_posns.]
            # In the long run, we should fix this, though I never observed a problem. ####@@@@
##        if 0: #bruce 060111 debug code (two places), safe but could be removed when not needed (tiny bit slow) [bruce 060111] ###@@@
##            # maybe print deltas for one atom
##            import runSim
##            if runSim.debug_all_frames:
##                ii = runSim.debug_all_frames_atom_index
##                print "delta_frame %d[%d] is" % (n, ii), res[ii]
        return res

    def close_file(self):
        self.filereader.close_file() # but don't forget about it!
    
    pass # end of class MovieFile


# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
GLPane_lighting_methods.py

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

bruce 080910 split this out of class GLPane
"""

from graphics.drawing.gl_lighting import glprefs_data_used_by_setup_standard_lights

from graphics.drawing.gl_lighting import _default_lights # REVIEW: rename as a constant?
from graphics.drawing.gl_lighting import setup_standard_lights

from utilities.prefs_constants import glpane_lights_prefs_key
from utilities.prefs_constants import light1Color_prefs_key
from utilities.prefs_constants import light2Color_prefs_key
from utilities.prefs_constants import light3Color_prefs_key

import foundation.preferences as preferences
import foundation.env as env

from OpenGL.GL import glMatrixMode
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import GL_PROJECTION
from OpenGL.GL import glLoadIdentity
from OpenGL.GL import glEnable
from OpenGL.GL import glDisable
from OpenGL.GL import GL_NORMALIZE

from utilities.debug_prefs import debug_pref
from utilities.debug_prefs import Choice_boolean_False

_DEBUG_LIGHTING = False #bruce 050418


class GLPane_lighting_methods(object):
    """
    private mixin for providing lighting methods to class GLPane
    """
    #bruce 050311 wrote these in class GLPane (rush order for Alpha4)
    #bruce 080910 split them into a separate file

    # default values of instance variables
    
    # [bruce 051212 comment: not sure if this needs to be in sync with any other values;
    #  also not sure if this is used anymore, since __init__ sets _lights from prefs db via loadLighting.]
    _lights = _default_lights

    _default_lights = _lights # this copy will never be changed

    need_setup_lighting = True # whether the next paintGL needs to call _setup_lighting (in our method setup_lighting_if_needed)

    _last_glprefs_data_used_by_lights = None #bruce 051212, replaces/generalizes _last_override_light_specular

    def setup_lighting_if_needed(self): #bruce 080910 un-inlined this
        if self.need_setup_lighting \
           or self._last_glprefs_data_used_by_lights != glprefs_data_used_by_setup_standard_lights() \
           or debug_pref("always setup_lighting?", Choice_boolean_False):
            #bruce 060415 added debug_pref("always setup_lighting?"), in GLPane and ThumbView [KEEP DFLTS THE SAME!!];
            # using it makes specularity work on my iMac G4,
            # except for brief periods as you move mouse around to change selobj (also observed on G5, but less frequently I think).
            # BTW using this (on G4) has no effect on whether "new wirespheres" is needed to make wirespheres visible.
            #
            # (bruce 051126 added override_light_specular part of condition)
            # I don't know if it matters to avoid calling this every time...
            # in case it's slow, we'll only do it when it might have changed.
            self.need_setup_lighting = False # set to true again if setLighting is called
            self._setup_lighting()
        return

    def setLighting(self, lights, _guard_ = 6574833, gl_update = True): 
        """
        Set current lighting parameters as specified
        (using the format as described in the getLighting method docstring).
        This does not save them in the preferences file; for that see the saveLighting method.
        If option gl_update is False, then don't do a gl_update, let caller do that if they want to.
        """
        assert _guard_ == 6574833 # don't permit optional args to be specified positionally!!
        try:
            # check, standardize, and copy what the caller gave us for lights
            res = []
            lights = list(lights)
            assert len(lights) == 3
            for c,a,d,s,x,y,z,e in lights:
                # check values, give them standard types
                r = float(c[0])
                g = float(c[1])
                b = float(c[2])
                a = float(a)
                d = float(d)
                s = float(s)
                x = float(x)
                y = float(y)
                z = float(z)
                assert 0.0 <= r <= 1.0
                assert 0.0 <= g <= 1.0
                assert 0.0 <= b <= 1.0
                assert 0.0 <= a <= 1.0
                assert 0.0 <= d <= 1.0
                assert 0.0 <= s <= 1.0
                assert e in [0,1,True,False]
                e = not not e
                res.append( ((r,g,b),a,d,s,x,y,z,e) )
            lights = res
        except:
            print_compact_traceback("erroneous lights %r (ignored): " % lights)
            return
        self._lights = lights
        # set a flag so we'll set up the new lighting in the next paintGL call
        self.need_setup_lighting = True
        #e maybe arrange to later save the lighting in prefs... don't know if this belongs here
        # update GLPane unless caller wanted to do that itself
        if gl_update:
            self.gl_update()
        return

    def getLighting(self):
        """
        Return the current lighting parameters.
        [For now, these are a list of 3 tuples, one per light,
        each giving several floats and booleans
        (specific format is only documented in other methods or in their code).]
        """
        return list(self._lights)

    def _setup_lighting(self):
        """
        [private method]
        Set up lighting in the model (according to self._lights).
        [Called from both initializeGL and paintGL.]
        """
        # note: there is some duplicated code in this method
        # in GLPane_lighting_methods (has more comments) and ThumbView,
        # but also significant differences. Should refactor sometime.
        # [bruce 060415/080912 comment]
        
        glEnable(GL_NORMALIZE)
            # bruce comment 050311: I don't know if this relates to lighting or not
            # grantham 20051121: Yes, if NORMALIZE is not enabled (and normals
            # aren't unit length or the modelview matrix isn't just rotation)
            # then the lighting equation can produce unexpected results.  

        #bruce 050413 try to fix bug 507 in direction of lighting:
        ##k might be partly redundant now; not sure whether projection matrix needs to be modified here [bruce 051212]
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glprefs = None
            #e someday this could be an argument providing a different glprefs object
            # for local use in part of a scenegraph (if other code was also revised) [bruce 051212 comment]

        #bruce 051212 moved most code from this method into new function, setup_standard_lights
        setup_standard_lights( self._lights, glprefs)

        # record what glprefs data was used by that, for comparison to see when we need to call it again
        # (not needed for _lights since another system tells us when that changes)
        self._last_glprefs_data_used_by_lights = glprefs_data_used_by_setup_standard_lights(glprefs)
        return

    def saveLighting(self):
        """
        save the current lighting values in the standard preferences database
        """
        try:
            prefs = preferences.prefs_context()
            key = glpane_lights_prefs_key
            # we'll store everything in a single value at this key,
            # making it a dict of dicts so it's easy to add more lighting attrs (or lights) later
            # in an upward-compatible way.
            # [update, bruce 051206: it turned out that when we added lots of info it became
            #  not upward compatible, causing bug 1181 and making the only practical fix of that bug
            #  a change in this prefs key. In successive commits I moved this key to prefs_constants,
            #  then renamed it (variable and key string) to try to fix bug 1181. I would also like to find out
            #  what's up with our two redundant storings of light color in prefs db, ###@@@
            #  but I think bug 1181 can be fixed safely this way without my understanding that.]

            (((r0,g0,b0),a0,d0,s0,x0,y0,z0,e0), \
             ( (r1,g1,b1),a1,d1,s1,x1,y1,z1,e1), \
             ( (r2,g2,b2),a2,d2,s2,x2,y2,z2,e2)) = self._lights

            # now process it in a cleaner way
            val = {}
            for (i, (c,a,d,s,x,y,z,e)) in zip(range(3), self._lights):
                name = "light%d" % i
                params = dict( color = c, \
                               ambient_intensity = a, \
                               diffuse_intensity = d, \
                               specular_intensity = s, \
                               xpos = x, ypos = y, zpos = z, \
                               enabled = e )
                val[name] = params
            # save the prefs to the database file
            prefs[key] = val
            # This was printing many redundant messages since this method is called 
            # many times while changing lighting parameters in the Preferences | Lighting dialog.
            # Mark 051125.
            #env.history.message( greenmsg( "Lighting preferences saved" ))
        except:
            print_compact_traceback("bug: exception in saveLighting (pref changes not saved): ")
            #e redmsg?
        return

    def loadLighting(self, gl_update = True):
        """
        load new lighting values from the standard preferences database, if possible;
        if correct values were loaded, start using them, and do gl_update unless option for that is False;
        return True if you loaded new values, False if that failed
        """
        try:
            prefs = preferences.prefs_context()
            key = glpane_lights_prefs_key
            try:
                val = prefs[key]
            except KeyError:
                # none were saved; not an error and not even worthy of a message
                # since this is called on startup and it's common for nothing to be saved.
                # Return with no changes.
                return False
            # At this point, you have a saved prefs val, and if this is wrong it's an error.        
            # val format is described (partly implicitly) in saveLighting method.
            res = [] # will become new argument to pass to self.setLighting method, if we succeed
            for name in ['light0','light1','light2']:
                params = val[name] # a dict of ambient, diffuse, specular, x, y, z, enabled
                color = params['color'] # light color (r,g,b)
                a = params['ambient_intensity'] # ambient intensity
                d = params['diffuse_intensity'] # diffuse intensity
                s = params['specular_intensity'] # specular intensity
                x = params['xpos'] # X position
                y = params['ypos'] # Y position
                z = params['zpos'] # Z position
                e = params['enabled'] # boolean

                res.append( (color,a,d,s,x,y,z,e) )
            self.setLighting( res, gl_update = gl_update)
            if _DEBUG_LIGHTING:
                print "_DEBUG_LIGHTING: fyi: Lighting preferences loaded"
            return True
        except:
            print_compact_traceback("bug: exception in loadLighting (current prefs not altered): ")
            #e redmsg?
            return False
        pass

    def restoreDefaultLighting(self, gl_update = True):
        """
        restore the default (built-in) lighting preferences (but don't save them).
        """
        # Restore light color prefs keys.
        env.prefs.restore_defaults([
            light1Color_prefs_key, 
            light2Color_prefs_key, 
            light3Color_prefs_key,
        ])
        self.setLighting( self._default_lights,  gl_update = gl_update )
        return True

    pass

# end

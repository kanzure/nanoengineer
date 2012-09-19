# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""
Api.py - superclass for testing API compliance

Note: this is used in NE1 if certain private debug flags are set,
but has not been tested or maintained for a long time (as of 081216).
If it is ever verified to work and be useful, it can be moved into a
more general place.

@author: Will
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""

# Yet another experiment with testing API compliance in Python

def _inheritance_chains(klas, endpoint):
    if klas is endpoint:
        return [ (endpoint,) ]
    lst = [ ]
    for base in klas.__bases__:
        for seq in _inheritance_chains(base, endpoint):
            lst.append((klas,) + seq)
    return lst

# This little hack is a way to ensure that a class implementing an API does so completely. API
# compliance also requires that the caller not call any methods _not_ defined by the API, but
# that's a harder problem that we'll ignore for the moment.

class Api(object):
    #bruce 081216 added superclass object, untested
    def _verify_api_compliance(self):
        from types import MethodType
        myclass = self.__class__
        mystuff = myclass.__dict__
        ouch = False
        for legacy in _inheritance_chains(myclass, Api):
            assert len(legacy) >= 3
            api = legacy[-2]
            print api, api.__dict__
            for method in api.__dict__:
                if not method.startswith("__"):
                    assert type(getattr(api, method)) is MethodType
                    assert type(getattr(self, method)) is MethodType
                    this_method_ok = False
                    for ancestor in legacy[:-2]:
                        if method in ancestor.__dict__:
                            this_method_ok = True
                    if not this_method_ok:
                        print myclass, 'does not implement', method, 'from', api
                        ouch = True
        if ouch:
            raise Exception('Class does not comply with its API')

# end

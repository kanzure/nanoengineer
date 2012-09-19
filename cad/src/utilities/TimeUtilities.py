# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

"""
utilities/TimeUtilities.py Stuff related to processing time values.

Not called utilities/time.py because of the python time package.

@author: EricM
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

"""

from datetime import datetime

def timeStamp(when = None):
    """
    Return a string suitable for use as a timestamp component of a
    filename.  You can pass in a datetime object to extract the time
    from, or pass nothing and the string will represent now.
    """
    if (when is None):
        when = datetime.now()
    stamp = "%04d-%02d-%02d-%02d-%02d-%02d" % (when.year,
                                               when.month,
                                               when.day,
                                               when.hour,
                                               when.minute,
                                               when.second)
    return stamp

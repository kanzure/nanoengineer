"""Version information for nanoENGINEER,
and other stuff like author list, license, etc."""

progname = "nanoENGINEER"
version_info=(0, 6, 7)  # "0-6.7"
# Anticipated date for the next release
releaseDate = "August 17, 2005"

__author__ = """Mark Sims
Josh Hall
Bruce Smith
Huaicai Mo
Ninad Sathaye
Eric Messick
Will Ware"""

__copyright__ = "Copyright (C) 2005, Nanorex, Inc."

__license__ = """nanoENGINEER, a molecular CAD program for nanotechnology
""" + __copyright__ + """

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA."""

############################

_major, _minor, _tiny = version_info
version = "%s-%d-%d.%d" % (progname, _major, _minor, _tiny)
status = {0: "alpha",
          1: "beta",
          2: "stable",
          3: "release"}[_major]

__version__ = version

if __name__ == "__main__":
    for x in dir():
        print x + ":", eval(x)
        print

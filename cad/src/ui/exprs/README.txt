$Id$

 Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 

NOTE: image files (like the ones in this directory)
need to be committed as binary files. When we used cvs,
this was done like this:

  % cvs add -kb binary.png
  % cvs commit -m "new image of an elephant" binary.png

Now that we use svn, I think it's sufficient to have a correct
~/.subversion/config file, as explained in

  http://www.nanoengineer-1.net/mediawiki/index.php?title=Subversion#subversion_config_file

Note: the .jpg versions below no longer work in NE1 on recent versions of Mac OS and/or Qt,
at least in some developer configurations. As of 081125, only the .png images are used.

Sources of these images (relevant for inferring copyright):

courier-128.png - derived by bruce from screenshot of IDLE (Python IDE) on Mac,
using courier font from Tk library on Mac (should be ok since font pixmaps
themselves are not copyrightable, AFAIK); hereby placed into the public domain, 
by bruce 061125

blueflake.jpg/.png - derived by bruce [as IMG_1613-p1.jpg] from a personally taken
photo [IMG_1613.jpg] of his minor son's painting; hereby placed into the public
domain, by bruce 061125

redblue-34x66.jpg/.png - trivial; saved from NE1

mac_checkbox_off.jpg/.png, mac_checkbox_on.jpg/.png -- screenshots of NE1 prefs (Qt3) on Mac OS X 10.3.9

These are classified into subdirectories based on their intended use
in the cad/src/exprs package or its client code.

# end

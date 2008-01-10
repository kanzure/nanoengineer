
QuteMol (http://qutemol.sourceforge.net/)
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
1/10/2008 - Brian Helfrich


Building
--------
So far I've only built QuteMol on Vista using wxDev-C++ 6.10.2
(http://wxdsgn.sourceforge.net/). There are Mac build files - I haven't
tried them, but they must work since M&P are building Mac binaries.

QuteMol depends on the following libraries:
- wxWidgets (this is taken care of when building with wxDev-C++)
- GLEW (http://glew.sourceforge.net/)
- VCG (http://vcg.sourceforge.net/)


Here's the directory structure that the wxDev-C++ project file assumes:

<your SourceForge (SF) CVS root>/
  glew/     - CVS it from SF, don't build it.
  qutemol/  - SVN it from our cad/plugins/QuteMol/qutemol, build this.
  vcg/      - CVS it from SF (the top-level vcg/ directory, not the vcg/
              from inside the top-level vcg/ directory), don't build it.

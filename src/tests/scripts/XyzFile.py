#!/usr/bin/python

import string

class Atom:
    def __init__(self, element, x, y, z):
        self.element = element
        self.x = x
        self.y = y
        self.z = z
    def toString(self):
        return ("%s %f %f %f" %
                (self.element, self.x, self.y, self.z))
    def __repr__(self):
        return "<" + self.toString() + ">"

class XyzFile:
    def __init__(self):
        self.atoms = [ ]
    def __getitem__(self, i):
        return self.atoms[i]
    def numAtoms(self):
        return len(self.atoms)
    def read(self, filename):
        inf = open(filename)
        self.readstring(inf.read())
        inf.close()
    def readstring(self, lines):
        lines = lines.split("\n")
        numAtoms = string.atoi(lines[0])
        lines = lines[2:]
        for i in range(numAtoms):
            element, x, y, z = lines[i].split()
            x, y, z = map(string.atof, (x, y, z))
            self.atoms.append(Atom(element, x, y, z))
    def write(self, title, filename=None):
        if filename != None:
            outf = open(filename, "w")
        else:
            outf = sys.stdout
        outf.write("%d\n%s\n" % (len(self.atoms), title))
        for atm in self.atoms:
            outf.write(atm.toString() + "\n")
        if filename != None:
            outf.close()

if __name__ == "__main__":
    # do a little test
    class StringCollector:
        def __init__(self):
            self.contents = ""
        def write(self, x):
            self.contents += x
    import sys
    example_xyz_file = """15
RMS=0.994508
C -0.193641 2.900593 -0.026523
X 0.093601 3.502437 0.394872
X -0.623522 3.154064 -0.637458
C -1.079249 2.005273 0.890906
X -1.803795 1.958430 0.584626
X -1.090331 2.310792 1.617200
C 0.986482 2.029986 -0.552402
X 0.945121 1.985940 -1.338110
X 1.667645 2.347089 -0.314849
C -0.443634 0.583852 0.936816
X -0.955793 0.061908 0.643109
X -0.248030 0.411844 1.680547
C 0.839719 0.603152 0.054672
X 1.466374 0.446893 0.504740
X 0.762053 0.079748 -0.528147
"""
    xyz = XyzFile()
    xyz.readstring(example_xyz_file)
    if False:
        sc = StringCollector()
        ss, sys.stdout = sys.stdout, sc
        xyz.write("RMS=0.994508")
        #xyz.write("Icky sticky goo")
        sys.stdout = ss
        assert sc.contents == example_xyz_file
    else:
        for i in range(xyz.numAtoms()):
            print xyz[i]

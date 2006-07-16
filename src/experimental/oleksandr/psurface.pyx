cdef extern from "csurface.h":
    void cAdd(double x, double y, double z, double r)
    void cCreateSurface()
    void cAllocate()
    void cFree()
    int cNp()
    int cNt()
    double cPx(int i)
    double cPy(int i)
    double cPz(int i)
    double cNx(int i)
    double cNy(int i)
    double cNz(int i)
    int cI(int i)
    void cLevel(int i)
def CreateSurface(spheres,level):
    cAllocate()
    for s in spheres:
        cAdd(s[0],s[1],s[2],s[3])
    cLevel(level)
    cCreateSurface()
    points = []
    normals = []
    for i in range(cNp()):
        points.append((cPx(i),cPy(i),cPz(i)))
        normals.append((cNx(i),cNy(i),cNz(i)))
    trias = []
    for i in range(cNt() / 3):
        trias.append((cI(3*i),cI(3*i+1),cI(3*i+2)))
    cFree()
    return ((trias, points), normals)

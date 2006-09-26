cdef extern from "csurface.h":
    void cAdd(double x, double y, double z, double r, int p)
    void cCreateSurface()
    void cAllocate()
    void cFree()
    int cNp()
    int cNt()
    int cNc()
    double cPx(int i)
    double cPy(int i)
    double cPz(int i)
    double cNx(int i)
    double cNy(int i)
    double cNz(int i)
    double cCr(int i)
    double cCg(int i)
    double cCb(int i)
    int cI(int i)
    void cLevel(int i)
    int cType()
    void cMethod(int m)
def CreateSurface(spheres,level,method):
    cAllocate()
    for s in spheres:
        cAdd(s[0],s[1],s[2],s[3],s[4])
    cLevel(level)
    cMethod(method)
    cCreateSurface()
    points = []
    normals = []
    colors = []
    for i in range(cNp()):
        points.append((cPx(i),cPy(i),cPz(i)))
        normals.append((cNx(i),cNy(i),cNz(i)))
        if cNc() != 0:
            colors.append((cCr(i),cCg(i),cCb(i)))
    entities = []
    if cType() == 0 :
        for i in range(cNt() / 3):
            entities.append((cI(3*i),cI(3*i+1),cI(3*i+2)))
    else:
        for i in range(cNt() / 4):
            entities.append((cI(4*i),cI(4*i+1),cI(4*i+2),cI(4*i+3)))
    cFree()
    return ((entities, points, colors), normals)

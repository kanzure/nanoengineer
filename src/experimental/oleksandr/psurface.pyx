# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
cdef extern from "csurface.h":
    void cAdd(double x, double y, double z, double r, int p)
    void cCreateSurface()
    void cCollisionDetection(double delta)
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
    int cC(int i)
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
        colors.append(cC(i)) 
    entities = []
    if cType() == 0 :
        for i in range(cNt() / 3):
            entities.append((cI(3*i),cI(3*i+1),cI(3*i+2)))
    else:
        for i in range(cNt() / 4):
            entities.append((cI(4*i),cI(4*i+1),cI(4*i+2),cI(4*i+3)))
    cFree()
    return ((entities, points, colors), normals)
def CollisionDetection(spheres,level,method,delta):    
    cAllocate()
    for s in spheres:
        cAdd(s[0],s[1],s[2],s[3],s[4])
    cLevel(level)
    cMethod(method)
    cCollisionDetection(delta)
    points = []
    normals = []
    colors = []
    for i in range(cNp()):
        points.append((cPx(i),cPy(i),cPz(i)))
        normals.append((cNx(i),cNy(i),cNz(i)))
        colors.append(cC(i)) 
    entities = []
    if cType() == 0 :
        for i in range(cNt() / 3):
            entities.append((cI(3*i),cI(3*i+1),cI(3*i+2)))
    else:
        for i in range(cNt() / 4):
            entities.append((cI(4*i),cI(4*i+1),cI(4*i+2),cI(4*i+3)))
    return ((entities, points, colors), normals)

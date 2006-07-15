cdef extern from "csurface.h":
    void cAdd(double x, double y, double z, double r)
    void cCreateSurface()
    void cClear()
    int cNp()
    int cNt()
    double cPx(int i)
    double cPy(int i)
    double cPz(int i)
    double cNx(int i)
    double cNy(int i)
    double cNz(int i)
    int cI(int i)
def Add(double x, double y, double z, double r):    
    cAdd(x, y, z, r)    
def CreateSurface():    
    cCreateSurface()    
def Clear():    
    cClear()    
def Np():    
    return cNp()    
def Nt():    
    return cNt()    
def Px(int i):    
    return cPx(i)    
def Py(int i):    
    return cPy(i)    
def Pz(int i):    
    return cPz(i)    
def Nx(int i):    
    return cNx(i)    
def Ny(int i):    
    return cNy(i)    
def Nz(int i):    
    return cNz(i)    
def I(int i):    
    return cI(i)    




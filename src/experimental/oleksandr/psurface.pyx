cdef extern from "csurface.h":
    void cAdd(double x, double y, double z, double r)
    void cCreateSurface()
    void cClear()
    int cNp()
    int cNt()
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
   




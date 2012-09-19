import array
import math

class A(object):
    # not sure if we could successfully subclass array.array;
    # at least we'd have to modify __new__ I guess?
    def __init__(self, sequence):
        self._data = array.array('f', sequence)
        return
    # these are only needed since we're not subclassing array.array
    def __len__(self):
        return len(self._data)
    def __getitem__(self, i):
        return self._data[i]
    def __eq__(self, other):
        try:
            lenother = len(other)
        except:
            print "fyi: can't get len(%r)" % (other,)
            return False
        if len(self) != lenother:
            print "fyi: diff lens"
            return False
        bad = [i for i in range(lenother) if self[i] != other[i]]
##        if bad:
##            print "fyi: bad = ", bad
        return not bad
    def __ne__(self, other):
        return not (self == other)
    def __repr__(self):
        # either is correct: "V%r" or "A(%r)"
        return "V%r" % (tuple(self._data),)
    # these would be needed even if we subclassed array.array
    def __add__(self, other):
        assert len(self._data) == len(other)
        return self.__class__( [self[i] + other[i] for i in range(len(self))] )
    def __sub__(self, other):
        assert len(self._data) == len(other)
        return self.__class__( [self[i] - other[i] for i in range(len(self))] )
    def __mul__(self, scalar):
        return self.__class__( [self[i] * scalar for i in range(len(self))] )
    __rmul__ = __mul__
    def __div__(self, scalar):
        return self.__class__( [self[i] / scalar for i in range(len(self))] )
    def dot(self, other):
        assert len(self._data) == len(other)
        return sum( [self[i] * other[i] for i in range(len(self))] )
    def is_zero(self):
        return self.dot(self) == 0
    def vlen(self):
        return math.sqrt(self.dot(self))
    pass

def V(*args):
    return A(args)

def dot(v1, v2):
    return v1.dot(v2)

def vlen(v):
    return v.vlen()

def vector_is_zero(v):
    return v.is_zero()

def cross(v1, v2):
    x1, y1, z1 = v1
    x2, y2, z2 = v2
    assert 0, "cross is nim"

def unitVector(v):
    length = vlen(v)
    if length == 0.0:
        return v
    return v / length

def rotate2d_90(vec_2d):
    x, y = vec_2d
    return V( -y, x )

# ==

def get_pos(obj_or_pos): # not sure if these belong here
    try:
        pos = obj_or_pos.pos
    except:
        pos = obj_or_pos
    return A(pos)

def pos_and_size_from_obj_or_pos(obj_or_pos, default_size = 5): # rename, get_pos_and_size?
    pos = get_pos(obj_or_pos)
    size = default_size # stub
    return pos, size

# ==

def _test():
    v = V(1,2,3)
    v2 = A([4,6,9])
    assert v == A((1,2,3))
    assert v == A([1,2,3])
    assert v == A(array.array('i', [1,2,3]))
    assert array.array('i', [1,2,3]) == array.array('f', [1,2,3])
    assert v.dot(v2) == 1*4 + 2*6 + 3*9
    assert dot(v,v2) == v.dot(v2)
    assert v.vlen() == math.sqrt(1*1 + 2*2 + 3*3)
    assert vlen(v) == v.vlen()
    assert v == v
    assert not (v != v)
    assert V(1,1,0) != V(1,0,0)
    assert not (V(1,1,0) == V(1,0,0))

    assert v + v == v * 2
    assert v * 2 == 2 * v
    assert v / 2 == v * 0.5
    assert vector_is_zero(v - v)

    assert unitVector(V(3,4)) == V(3,4)/5.0
    assert rotate2d_90(V(100,3)) == V(-3,100)
    print "tests done"

if __name__ == '__main__':
    _test()

# end

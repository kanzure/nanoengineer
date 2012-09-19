# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""

@author: EricM
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

import unittest
from samevals import same_vals, setArrayType
import Numeric

class SameValsTests(unittest.TestCase):

    def test_simple(self):
        assert same_vals(1, 1)
        assert not same_vals(1, 2)

    def test_dict1(self):
        a = {}
        b = {}
        assert same_vals(a, b)
        a["abc"] = 23 ;
        assert not same_vals(a, b)
        b["def"] = 45 ;
        assert not same_vals(a, b)
        a["def"] = 42 ;
        b["abc"] = 23 ;
        assert not same_vals(a, b)
        a["def"] = 45 ;
        assert same_vals(a, b)

    def test_list1(self):
        a = []
        b = []
        assert same_vals(a, b)
        a.append("ferd")
        assert not same_vals(a, b)
        b.append("asdf")
        assert not same_vals(a, b)
        a.append("poiu")
        b.append("poiu")
        assert not same_vals(a, b)
        a[0] = "asdf"
        assert same_vals(a, b)

    def test_tuple1(self):
        # anyone know how to generate a zero length tuple?
        assert same_vals((1,), (1,))
        assert not same_vals((1, 2), (1,))
        assert same_vals((1, 2), (1, 2))
        assert not same_vals((1, 2), (2, 1))

    def test_numericArray1(self):
        a = Numeric.array((1, 2, 3))
        b = Numeric.array((1, 2, 3))
        assert same_vals(a, b)
        b = Numeric.array((1, 2, 4))
        assert not same_vals(a, b)
        b = Numeric.array((1, 2))
        assert not same_vals(a, b)

        a = Numeric.array([[1, 2], [3, 4]])
        b = Numeric.array([[1, 2], [3, 4]])
        assert same_vals(a, b)

        b = Numeric.array([4, 3])
        c = a[1, 1::-1]
        assert same_vals(b, c)

        a = Numeric.array([[[[ 1,  2,  3], [ 4,  5,  6], [ 7,  8,  9]],
                            [[10, 11, 12], [13, 14, 15], [16, 17, 18]],
                            [[19, 20, 21], [22, 23, 24], [25, 26, 27]]],
                           [[[28, 29, 30], [31, 32, 33], [34, 35, 36]],
                            [[37, 38, 39], [40, 41, 42], [43, 44, 45]],
                            [[46, 47, 48], [49, 50, 51], [52, 53, 54]]]])
        b = Numeric.array([[[[ 1,  2,  3], [ 4,  5,  6], [ 7,  8,  9]],
                            [[10, 11, 12], [13, 14, 15], [16, 17, 18]],
                            [[19, 20, 21], [22, 23, 24], [25, 26, 27]]],
                           [[[28, 29, 30], [31, 32, 33], [34, 35, 36]],
                            [[37, 38, 39], [40, 41, 42], [43, 44, 45]],
                            [[46, 47, 48], [49, 50, 51], [52, 53, 54]]]])
        assert same_vals(a, b)
        b = Numeric.array([[[[ 1,  2,  3], [ 4,  5,  6], [ 7,  8,  9]],
                            [[10, 11, 12], [13, 14, 15], [16, 17, 18]],
                            [[19, 20, 21], [22, 23, 24], [25, 26, 27]]],
                           [[[28, 29, 30], [31, 32, 33], [34, 35, 36]],
                            [[37, 38, 39], [40, 41, 42], [43, 44, 45]],
                            [[46, 47, 48], [49, 50, 51], [52, 53, 55]]]])
        assert not same_vals(a, b)
        b = Numeric.array([[[[ 1,  2,  3], [ 4,  5,  6], [ 7,  8,  9]],
                            [[10, 11, 12], [13, 14, 15], [16, 17, 18]],
                            [[19, 20, 21], [22, 23, 24], [25, 26, 27]]],
                           [[[28, 29, 30], [31, 30, 33], [34, 35, 36]],
                            [[37, 38, 39], [40, 41, 42], [43, 44, 45]],
                            [[46, 47, 48], [49, 50, 51], [52, 53, 54]]]])
        assert not same_vals(a, b)
        b = Numeric.array([[[[ 1,  2,  3], [ 4,  5,  6], [ 7,  8,  9]],
                            [[10, 11, 12], [13, 14, 15], [16, 17, 18]],
                            [[19, 20, 21], [22, 23, 24], [25, 26, 27]]]])
        assert not same_vals(a, b)

        a = Numeric.array(["abc", "def"], Numeric.PyObject)
        b = Numeric.array(["abc", "def"], Numeric.PyObject)
        assert same_vals(a, b)
        b = Numeric.array(["abc", "defg"], Numeric.PyObject)
        assert not same_vals(a, b)

def test():
    suite = unittest.makeSuite(SameValsTests, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    setArrayType(type(Numeric.array((1,2,3))))
    test()

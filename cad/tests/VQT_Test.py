
import unittest
from VQT import angleBetween
from numpy.oldnumeric import array, alltrue


class GeometryFunctionsTestCase(unittest.TestCase):
    """Unit tests for the geometry functions defined in VQT.py"""

    def setUp(self):
        """Sets up any objects needed by this test case."""
        pass

    
    def tearDown(self):
        """Releases any resources used by this test case."""
        pass

    
    def testAngleBetween(self):
        vector1 = array((1, 0, 0))
        vector2 = array((0, 1, 0))
        angle = angleBetween(vector1, vector2)
        assert angle == 90, "Fails sanity check"
        assert alltrue(vector1 == array((1, 0, 0))) and \
               alltrue(vector2 == array((0, 1, 0))), \
               "Arguments were modified (recurrence of bug ####)"

               
if __name__ == "__main__":
    unittest.main() # Run all tests whose names begin with 'test'


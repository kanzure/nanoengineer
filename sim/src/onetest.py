#!/usr/bin/python
# Copyright 2005-2006 Nanorex, Inc.  See LICENSE file for details.

# usage:
#
# onetest.py <test_name> [args for tests.py]
#
# runs a single regression test by name
#

import sys
import tests

class Main(tests.Main):
    def main(self, args):
        self.theTest = args[0]
        tests.Main.main(self, args[1:])

    def getCasenames(self):
        return [
            self.theTest
            ]


if __name__ == "__main__":
    Main().main(sys.argv[1:])

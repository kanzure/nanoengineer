#!/usr/bin/env python
# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

"""
Reads a sequence of numbers from stdin, and calculates the mean and
standard deviation.
"""

import sys
from math import sqrt

def main():
    numbers = []
    line = sys.stdin.readline()
    while (line):
        numbers.append(float(line))
        line = sys.stdin.readline()

    samples = len(numbers)
    mean = sum(numbers) / samples
    if (samples < 2):
        variance = 0
    else:
        sampleVariance = map(lambda x: (x - mean) * (x - mean), numbers)
        variance = sum(sampleVariance) / (samples - 1)
    print "samples: %d, mean: %f, standardDeviation: %f" % (samples, mean, sqrt(variance))

if (__name__ == '__main__'):
    main()

#!/usr/bin/env python

from __future__ import print_function
from FreePointFinder import FreePointFinder

fpf = FreePointFinder('example_map.yaml')

print('Point (1.0, 1.0)', 'is' if fpf.is_free(1.0, 1.0) else 'is not', 'free')
print('Point (2.0, -2.0)', 'is' if fpf.is_free(2.0, -2.0) else 'is not', 'free')
print('Closest free point to (2.0, -2.0) is', fpf.closest_free_point(2.0, -2.0))

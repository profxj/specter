#!/usr/bin/env python

"""
Test Specter file formats.  Loop over example files and just make sure
that we can read them.
"""

import os
from os.path import basename
from glob import glob
import unittest

import specter.io
from specter.test import test_data_dir

class TestSpecIO(unittest.TestCase):
    def setUp(self):
        self.specfiles = sorted(glob(test_data_dir()+'/spec-*.fits'))
        
    def test_files(self):
        wipeout = None
        for specfile in self.specfiles:
            try:
                x = specter.io.read_simspec(specfile)
            except Exception, e:
                print "Failed on %s: %s" % (basename(specfile), str(e))
                wipeout = e
        if wipeout:
            raise wipeout
            
if __name__ == '__main__':
    unittest.main()            
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestSpecIO)
    # unittest.TextTestRunner(verbosity=2).run(suite)
        
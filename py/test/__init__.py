def test_data_dir():
    """
    Return location of test data using paths relative to where
    this code is.

    Code in [specter]/py/test/
    Data in [specter]/data/test/
    [datadir] = [codedir]/../../data/test/
    """
    import os.path
    codedir = os.path.dirname(os.path.abspath(__file__))
    basedir = os.path.realpath(codedir+'/../../')
    return basedir + '/data/test/'
        
from specter.test.test_psf import TestPixPSF, TestSpotPSF
from specter.test.test_specio import TestSpecIO
from specter.test.test_throughput import TestThroughput
from specter.test.test_util import TestUtil
from specter.test.test_extract import TestExtract
from specter.test.test_pixspline import TestPixSpline

def test():
    """
    Run a suite of specter tests
    """
    import unittest
    
    load = unittest.defaultTestLoader.loadTestsFromTestCase    
    tests = list()
    tests.append(load(TestPixPSF))
    tests.append(load(TestSpotPSF))
    tests.append(load(TestSpecIO))
    tests.append(load(TestThroughput))
    tests.append(load(TestUtil))
    tests.append(load(TestExtract))
    tests.append(load(TestPixSpline))

    suite = unittest.TestSuite(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
    
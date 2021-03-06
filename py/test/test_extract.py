#!/usr/bin/env python

"""
Unit tests for PSF classes.
"""

import sys
import os
import numpy as N
import unittest
from specter.test import test_data_dir
from specter.psf import load_psf
from specter.extract.ex2d import ex2d


class TestExtract(unittest.TestCase):
    """
    Test functions within specter.util
    """
    def setUp(self):
        N.random.seed(0)
        psf = load_psf(test_data_dir() + "/psf-spot.fits")

        nspec = 10
        wmin = min(psf.wavelength(0, y=0), psf.wavelength(nspec-1, y=0))
        ww = psf.wavelength(0, y=N.arange(10,60))
        nwave = len(ww)
        
        phot_shape = (nspec, nwave)
        phot = N.random.uniform(1, 1000, size=phot_shape)
        image_orig = psf.project(ww, phot, verbose=False)
        var = 1.0 + image_orig
        image = image_orig + N.random.normal(scale=N.sqrt(var))
                
        self.phot = phot
        self.image_orig = image_orig
        self.image = image
        self.ivar = 1.0 / var
        self.psf = psf        
        self.ww = ww
        self.nspec = nspec
                
    def _test_blat(self):
        from time import time
        specrange = (0, self.nspec)
        waverange = (self.ww[0], self.ww[-1])
        imgvar = 1/self.ivar
        xmin, xmax, ymin, ymax = xyrange = self.psf.xyrange(specrange, waverange)
        
        for i in range(3):
            pix = self.image_orig + N.random.normal(scale=N.sqrt(imgvar))
            d = ex2d(pix, self.ivar, self.psf, specrange, self.ww, full_output=True)
            flux, ivar, R = d['flux'], d['ivar'], d['R']
            rflux = R.dot(self.phot.ravel()).reshape(flux.shape)
            chi = (flux - rflux) * N.sqrt(ivar)
            
            xpix = d['A'].dot(d['xflux'].ravel())
            subpix = pix[ymin:ymax, xmin:xmax].ravel()
            subivar = self.ivar[ymin:ymax, xmin:xmax].ravel()
            
            pixchi = (xpix - subpix) * N.sqrt(subivar)
        
            print i, N.std(chi), N.std(pixchi)
    
    def test_noiseless_ex2d(self):
        specrange = (0, self.nspec)
        ivar = N.ones(self.ivar.shape)
        d = ex2d(self.image_orig, ivar, self.psf, specrange, self.ww, full_output=True)

        R = d['R']
        flux = d['flux']     #- resolution convolved extracted flux
        xflux = d['xflux']   #- original extracted flux
        
        #- Resolution convolved input photons (flux)
        rphot = R.dot(self.phot.ravel()).reshape(flux.shape)
        
        #- extracted flux projected back to image
        ximg = self.psf.project(self.ww, xflux, verbose=False)
        
        #- Compare inputs to outputs
        bias = (flux - rphot)/rphot
        dximg = ximg - self.image_orig

        self.assertTrue( N.max(N.abs(bias)) < 1e-9 )
        self.assertTrue( N.max(N.abs(dximg)) < 1e-6 )                

    #- Pull values are wrong.  Why?  Overfitting?
    @unittest.expectedFailure
    def test_ex2d(self):
        specrange = (0, self.nspec)
        d = ex2d(self.image, self.ivar, self.psf, specrange, self.ww, full_output=True)

        #- Pull flux
        R = d['R']
        flux = d['flux']     #- resolution convolved extracted flux
        rphot = R.dot(self.phot.ravel()).reshape(flux.shape)
        pull_flux = (flux - rphot) * N.sqrt(d['ivar'])
        
        #- Pull image
        specrange = (0, self.nspec)
        waverange = (self.ww[0], self.ww[-1])
        xmin, xmax, ymin, ymax = xyrange = self.psf.xyrange(specrange, waverange)
        nx, ny = xmax-xmin, ymax-ymin
        xflux = d['xflux']   #- original extracted flux
        ### ximage = self.psf.project(self.ww, xflux, verbose=False)
        ximage = d['A'].dot(xflux.ravel()).reshape((ny,nx))
        subimg = self.image[ymin:ymax, xmin:xmax]
        subivar = self.ivar[ymin:ymax, xmin:xmax]
        pull_image = ((ximage - subimg) * N.sqrt(subivar))

        print "Known problem: Overfitting may result in small pull value"
        ### print N.std(pull_flux), N.std(pull_image)
        self.assertTrue(N.abs(1-N.std(pull_flux)) < 0.05,
                        msg="pull_flux sigma is %f" % N.std(pull_flux))
        self.assertTrue(N.abs(1-N.std(pull_image)) < 0.05,
                        msg="pull_image sigma is %f" % N.std(pull_image))
        
    def test_ex2d_subimage(self):
        specrange = (0, self.nspec)
        waverange = self.ww[0], self.ww[-1]
        flux, ivar, R = ex2d(self.image, self.ivar, self.psf, specrange, self.ww)

        xmin, xmax, ymin, ymax = self.psf.xyrange(specrange, waverange)
        xmin = max(0, xmin-10)
        xmax = min(self.psf.npix_x, xmax+10)
        ymin = max(0, ymin-10)
        ymax = min(self.psf.npix_y, ymax+10)
        xyrange = (xmin, xmax, ymin, ymax)
        
        subimg = self.image[ymin:ymax, xmin:xmax]
        subivar = self.ivar[ymin:ymax, xmin:xmax]
        subflux, subivar, subR = ex2d(subimg, subivar, self.psf, \
            specrange, self.ww, xyrange=xyrange)

        self.assertTrue( N.all(subflux == flux) )
        self.assertTrue( N.all(subivar == ivar) )
        self.assertTrue( N.all(subR == R) )

    def test_wave_off_image(self):
        ww = self.psf.wmin - 5 + N.arange(10)
        nspec = 2
        specrange = [0,nspec]
        xyrange = self.psf.xyrange(specrange, ww)

        phot = N.ones([nspec,len(ww)])

        img = self.psf.project(ww, phot, xyrange=xyrange)
        ivar = N.ones(img.shape)

        flux, fluxivar, R = ex2d(img, ivar, self.psf, specrange, ww, xyrange=xyrange)
        
        self.assertTrue( N.all(flux == flux) )
        
        
if __name__ == '__main__':
    unittest.main()           

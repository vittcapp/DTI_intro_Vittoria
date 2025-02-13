'''-----------------------------------------------------------------------------
This pipeline is for diffusion data ONLY.

Author: Emma Thomson 
Institution: Danish Research Centre for Magnetic Resonance
Data: February 2024
Email: emmat@drcmr.dk

#NOTE: Before running this file, run the sortDataBIDS.py file to sort the data 
       into the appropriate format 

-----------------------------------------------------------------------------'''
def diffusionMain(subject, session, ENum, b0Num, delta, Delta,
                  applyDenoise, applyMaskToData, dtiAnalysis, 
                  sandiAnalysis, noddiAnalysis, alignScans):

       '''--------------------------packages---------------------------------'''

       import numpy as np
       import os
       import nibabel as nib
       #import matplotlib.pyplot as plt
       from math import log10, floor

       os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'
       os.environ['PYDEVD_DISABLE_FILE_VALIDATION']='1'

       '''--------------------------functions--------------------------------'''

       from functions.applyMask import applyMask
       from functions.dti import dti
       from functions.sandi import sandi
       from functions.noddi import noddi

       '''-------------  -------------inputs---------------------------------'''

       #Define key strings for processing
       dwiFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub_' + 
                     subject + '/ses_' + str(session) + '/dwi/')
       processedFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub_'
                     +  subject + '/ses_' + str(session) + '/processed/'
                     + str(ENum) + '/')
       fileBase = 'sub_' +  subject + '_ses_' + str(session) + '_E' +  str(ENum)

       DeltaSec = Delta/1000 #s
       deltaSec = delta/1000 #s

       '''--------------------------denoising--------------------------------'''
       if applyDenoise is True:
              dwiFile = processedFolder + fileBase + '_denoised.nii'
       if applyDenoise is False and alignScans is True:
              dwiFile = processedFolder + fileBase + '_regrid_registered.nii'
       else: 
              dwiFile = dwiFolder + fileBase + '_DWI.nii'

       fullDwi = nib.load(dwiFile)

       '''------------------------------DTI----------------------------------'''

       if dtiAnalysis is True: 
              if applyMaskToData is True: 
                     dwiFile = applyMask(dwiFile, processedFolder)

              dti(dwiFile, fileBase, dwiFolder, processedFolder)

       '''----------------------------SANDI----------------------------------'''

       if sandiAnalysis is True:       ## THIS DOES NOT WORK YET
              sandi(dwiFolder, fileBase, processedFolder, Delta, delta, 
                    applyDenoise, ENum)
       '''-----------------------------NODDI---------------------------------'''

       if noddiAnalysis is True:       ## THIS DOES NOT WORK YET
              noddi(dwiFolder, fileBase, processedFolder, maskFolder, DeltaSec, 
                    deltaSec, applyDenoise)
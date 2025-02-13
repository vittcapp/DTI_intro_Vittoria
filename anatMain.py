'''----------------------------------------------------------------------
Eventually the whole pipeline will be run from this file.
- This pipeline is for anatomy data ONLY.

Author: Emma Thomson 
Institution: Danish Research Centre for Magnetic Resonance
Data: February 2024
Email: emmat@drcmr.dk

#NOTE: Before running this file, run the sortDataBIDS.py file to sort the data 
       into the appropriate format 

------------------------------------------------------------------------'''
'''--------------------------packages---------------------------------'''
import numpy as np
import os
import nibabel as nib
#import matplotlib.pyplot as plt
from math import log10, floor
os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'
'''--------------------------user inputs---------------------------------'''
#Main scan folder
subject = '1.2.24M'
session = 4

#E numbers associated with the scan to be concatenated
ENum = [7,9]

#Denoise data?
denoise = 1
#Mask data?
mask = 1

'''--------------------------inputs---------------------------------'''

#Define key strings for processing
anatFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub_' +  subject + '/ses_' 
              + str(session) + '/anat/')
processedFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub_' +  subject + '/ses_'
                         + str(session) + '/processed/' + str(ENum[1]) + '/')
maskFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub_' +  subject + '/ses_' 
              + str(session) + '/mask/')

'''--------------------------denoising---------------------------------'''
if denoise == 1:
       #Combine the anatomical data along the 4th dimension
       #Load the first file
       fileBase = 'sub_' +  subject + '_ses_' + str(session) + '_E' +  str(ENum[0])
       img1 = nib.load(anatFolder + fileBase + '_T2.nii')
       img1Data = img1.get_fdata()
       #expand the dimensions
       img1Data = np.expand_dims(img1Data, axis = 3)

       #Load the second file
       fileBase = 'sub_' +  subject + '_ses_' + str(session) + '_E' +  str(ENum[1])
       img2 = nib.load(anatFolder + fileBase + '_T2.nii')
       img2Data = img2.get_fdata()
       #expand the dimensions
       img2Data = np.expand_dims(img2Data, axis = 3)

       #Combine the data 
       combinedData = np.concatenate((img1Data, img2Data), axis = 3)

       #Save the combined data
       combinedImg = nib.Nifti1Image(combinedData, img1.affine)
       nib.save(combinedImg, anatFolder + fileBase + '_T2_combined.nii')

       #Denoise data 
       #MP-PCA denoising
       command = ('dwidenoise ' + anatFolder + fileBase + '_T2_combined.nii ' + anatFolder +
                   fileBase +'_T2_denoised.nii.gz -force')
       os.system(command)

       #Calculate residuals
       command = ('mrcalc ' + anatFolder + fileBase + '_T2_combined.nii ' + anatFolder + fileBase + 
                 '_T2_denoised.nii.gz -subtract ' + processedFolder + '_T2_denoised_residuals.nii.gz')
       os.system(command)

       #DeGibbs data
       command = ('mrdegibbs ' + anatFolder + fileBase + '_T2_denoised.nii.gz ' 
                  + anatFolder + fileBase + '_T2_denoised_degibbs.nii.gz -force')
       os.system(command)

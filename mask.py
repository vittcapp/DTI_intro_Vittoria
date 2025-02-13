'''-----------------------------------------------------------------------------
Masking function for diffusion weighted images

Author: Emma Thomson 
Institution: Danish Research Centre for Magnetic Resonance
Date: May 2024
Email: emmat@drcmr.dk

-----------------------------------------------------------------------------'''

def mask(collected_data, scan, testSwitch):
       import os
       import numpy as np
       import nibabel as nib
       import pandas as pd


       '''----------------------------folders----------------------------------'''

       dwiFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' +
              collected_data['subject'] + '/ses-' + collected_data['session'] +
              '/processed/aligned/')
       processedFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' +
              collected_data['subject'] + '/ses-' + collected_data['session'] +
              '/mask/')
       if not os.path.exists(processedFolder):
              os.system('mkdir ' + processedFolder)

       infoPath = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' +
              collected_data['subject'] + '/sequenceData_ses-' + 
              collected_data['session'] + '.xlsx')

       '''-------------------------------file-------------------------------'''
       #Find a high b value image to use for the mask
       #List all files in the folder
       files = os.listdir(dwiFolder)

       #Files containing the letter 'a' after the run number
       cFiles = [ff for ff in files if 'a_dwi' in ff]

       #Find the ones that are images
       cFiles = [ff for ff in cFiles if '.nii.gz' in ff]

       #Use the first file
       file = cFiles[0]
       filePath = dwiFolder + file

       #Load the file
       fullDwi = nib.load(filePath)
       fullDwiData = fullDwi.get_fdata()

       #Load the info file
       info = pd.read_excel(infoPath)

       #Find the row in the info file with the run number and DWI
       runNum = file.split('run-0')[1].split('_')[0]
       scanRow = info[(info['Run Number'] == int(runNum[0])) & (np.isnan(info['nDir']) == False)]

       #Find the b0 number
       b0Num = int(scanRow['nb0'].iloc[0])

       #Remove b0 images
       strippedData = fullDwiData[:,:,:,b0Num:]

       #Mean over the directions 
       meanData = np.mean(strippedData, axis=3)

       #Save the mean image
       img = nib.Nifti1Image(meanData, fullDwi.affine, fullDwi.header)
       savePath = processedFolder + 'meanDWI.nii.gz'
       nib.save(img, savePath)

       maskPath = processedFolder + 'mask.nii.gz'

       #Generate mask using FSL FAST
       command = ('fast -B -t 1 -n 2 -H 0.1 -I 4 -l 20.0 -o ' + processedFolder + ' ' +  
                       savePath)
       os.system(command)

       #Load the mask
       maskIm = nib.load(processedFolder + '/_mixeltype.nii.gz').get_fdata()
       maskIm[maskIm != 1] = 0

       #Subtract 1 
       #maskIm = maskIm - 1
       #Resave
       maskNifti = nib.Nifti1Image(maskIm, np.eye(4))
       nib.save(maskNifti, maskPath)

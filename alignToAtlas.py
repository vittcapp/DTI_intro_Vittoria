'''----------------------------------------------------------------------------- 
Regrid and register scans using MRTrix3
Author: Emma Thomson 
Institution: Danish Research Centre for Magnetic Resonance
Date: May 2024
Email: emmat@drcmr.dk

#NOTE: Before running this file, run the sortDataBIDS.py file to sort the data 
       into the appropriate format 
-----------------------------------------------------------------------------'''

def alignToAtlas(collected_data):
       '''----------------------------packages----------------------------------'''
       import os
       import numpy as np
       import nibabel as nib
       import string

       '''----------------------------user inputs-------------------------------'''
       #Main scan folder
       subject = collected_data['subject']
       session = collected_data['session']

       '''-------------------------find reference data--------------------------'''

       proccessedFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' +
              subject + '/ses-' + str(session) + '/processed/aligned/')

       #Get the anatomical file path
       fileBase = 'sub-' + subject + '_ses-' + str(session) + '_t2'
       anatFilePath = (proccessedFolder + fileBase + '_regrid_registered.nii.gz')

       #Load the anatomical file
       anatImg = nib.load(anatFilePath)
       anatData = anatImg.get_fdata()

       #Get voxel size
       voxelSize = anatImg.header.get_zooms() 

       '''-----------------------------atlas data-------------------------------'''
       #Load the atlas data
       atlasPath = ('/Users/emmathomson/Dropbox/Work/Coding/toolboxes/atlas/' + 
                    'ALLEN_MOUSE_COMMON_COORDINATE_FRAMEWORK_V3.nii.gz')
       atlasImg = nib.load(atlasPath)

       #Transform the atlas to the same orientation
       atlasData = atlasImg.get_fdata()
       atlasData = atlasData.transpose(2,1,0)
       atlasDataArray = np.array(atlasData)
       #Resizing the atlas to be larger than the anatomical scan
       atlasDataHold = np.zeros((np.shape(atlasData)[0]*2 , np.shape(atlasData)[1]*2,
                            np.shape(atlasData)[2]*2))
       #Fill the new array with the atlas data
       for ii in range(np.shape(atlasData)[0]):
              for jj in range(np.shape(atlasData)[1]):
                     for kk in range(np.shape(atlasData)[2]):
                            atlasDataHold[ii*2, jj*2, kk*2] = atlasData[ii,jj,kk]
       #Save the resized atlas
       atlasData = atlasDataHold

       #Save 
       img = nib.Nifti1Image(atlasData, anatImg.affine)
       atlasPathOut = proccessedFolder + 'atlas.nii.gz'
       nib.save(img, atlasPathOut)

       outputPath = proccessedFolder + fileBase + '_atlas_regrid.nii.gz'
       outputTransform = proccessedFolder + fileBase + '_atlas_transform.txt'

       #Regrid the data to the anatomical scan
       command  = ('mrgrid ' + anatFilePath  + ' regrid -template ' + 
                     atlasPathOut +  ' ' +  outputPath + ' -force')
       os.system(command)

       '''---------------------------register-------------------------------'''
       #Register the data to the atlas scan
       command = ('mrregister ' + outputPath + ' ' + atlasPathOut + ' -rigid '
                     + outputTransform + ' -type rigid -force')
       os.system(command)

       #Transform the data
       command = ('mrtransform ' + outputPath + ' -linear ' + outputTransform +
                     ' ' + outputPath[:-7] + '_registered.nii.gz -force')
       os.system(command)
       
'''-----------------------------------------------------------------------------
Apply mask to data 

Author: Emma Thomson 
Institution: Danish Research Centre for Magnetic Resonance
Date: May 2024
Email: emmat@drcmr.dk

#NOTE: Before running this file, run the sortDataBIDS.py file to sort the data 
       into the appropriate format 

-----------------------------------------------------------------------------'''

def applyMask(file, maskFolder, fileBase):

       import nibabel as nib
       import numpy as np

       #load mask
       mask = nib.load(maskFolder + fileBase + '_mask.nii.gz')
       mask = mask.get_fdata()

       scan = nib.load(file)
       scanData = scan.get_fdata()
       try:
              #Apply mask
              scanDataMasked = np.multiply(scanData, mask)
       except:
              #If the data is multi-dimensional, tile the mask and then apply
              maskTile = np.tile(mask[...,np.newaxis],(1,1,1,scanData.shape[3]))
              scanDataMasked = np.multiply(scanData, maskTile)

       #Save masked data
       img = nib.Nifti1Image(scanDataMasked, scan.affine, scan.header)
       maskedFile = file.replace('.nii.gz','_masked.nii.gz')
       nib.save(img, maskedFile)

       return maskedFile
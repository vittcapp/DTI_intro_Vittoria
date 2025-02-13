'''-----------------------------------------------------------------------------
Rotate an array in 3D space

Author: Emma Thomson 
Institution: Danish Research Centre for Magnetic Resonance
Date: May 2024
Email: emmat@drcmr.dk

#NOTE: Before running this file, run the sortDataBIDS.py file to sort the data 
       into the appropriate format 

-----------------------------------------------------------------------------'''

def rotate(array , xAngle, yAngle, zAngle):
    import numpy as np
    import scipy.ndimage

    # Rotate the array
    rotatedArray = scipy.ndimage.rotate(array, xAngle, axes=(0,1), 
                                        reshape=False)
    rotatedArray = scipy.ndimage.rotate(rotatedArray, yAngle, axes=(0,2), 
                                        reshape=False)
    rotatedArray = scipy.ndimage.rotate(rotatedArray, zAngle, axes=(1,2), 
                                        reshape=False)


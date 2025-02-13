'''-----------------------------------------------------------------------------
Data No function

Author: Emma Thomson 
Institution: Danish Research Centre for Magnetic Resonance
Date: October 2024
Email: emmat@drcmr.dk

-----------------------------------------------------------------------------'''

def normalisation(collected_data, testSwitch):

        import os
        import numpy as np
        import nibabel as nib
        import pandas as pd
        import matplotlib.pyplot as plt

        '''-----------------------------folders----------------------------------'''

        #Output folder
        processedFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' +
                collected_data['subject'] + '/ses-' + collected_data['session'] +
                '/processed/normalised/')
        inputFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' +
                collected_data['subject'] + '/ses-' + collected_data['session'] +
                '/processed/aligned/')
        # If it doesnt exist then create it
        if not os.path.exists(processedFolder):
                os.system('mkdir ' + processedFolder)
    
        infoPath = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' +
                collected_data['subject'] + '/sequenceData_ses-' + 
                collected_data['session'] + '_splitData.xlsx')
        
        #Iterate through the files in the input folder
        for file in os.listdir(inputFolder):
                #If the file is a nifti file
                if file.endswith('registered.nii.gz')and 'run' in file:
                        #Read in the file
                        img = nib.load(inputFolder + file)
                        #Get the data
                        imgData = img.get_fdata()

                        #Remove NaNs
                        imgData[np.isnan(imgData)] = 0

                        #Find the run number from the file name
                        run = file.split('_run-0')[1].split('_')[0]

                        #If run does not contain a letter then skip the scan
                        if not any(char.isalpha() for char in run):
                                continue
                        else: 
                                info = pd.read_excel(infoPath)
 
                                #Find the row with the matching run number
                                runRow = info[info['Run Number'] == run]
                                # b0 image is the first nb0 images
                                b0s = imgData[:,:,:,0:int(runRow['nb0'].iloc[0])]

                                # Average the b0 images
                                b0 = np.mean(b0s, axis=3)

                                #Tile the b0 image to the same size as the data
                                b0 = np.tile(np.expand_dims(b0,axis=3), (1, 1, 1, imgData.shape[3]))

                                #Multiply the bias field by the data
                                correctedData =imgData/b0

                                #Save the corrected data
                                correctedImg = nib.Nifti1Image(correctedData, img.affine)
                                outputName = file.split('_registered')[0] + '_normalised.nii.gz'
                                nib.save(correctedImg, processedFolder + file.split('_regrid')[0] + '_normalised.nii')
                        

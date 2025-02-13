'''-----------------------------------------------------------------------------
Code for generating mean images for each b value in a DWI dataset.
In compy format with adjusted filenames

Author: Emma Thomson 
Institution: Danish Research Centre for Magnetic Resonance
Date: May 2024
Email: emmat@drcmr.dk

#NOTE: Before running this file, run the sortDataBIDScompy.py file to sort the data 
       into the appropriate format 

-----------------------------------------------------------------------------'''

'''--------------------------------packages----------------------------------'''
import os
import numpy as np
import nibabel as nib
import pandas as pd

def powderAve(collected_data, infoPath):
    '''---------------------------------inputs------------------------------------'''

    splitFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' + 
                collected_data['subject'] + '/ses-' + collected_data['session'] + '/processed/split/')
    normFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' + 
                collected_data['subject'] + '/ses-' + collected_data['session'] + '/processed/normalised/')

    processedFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' + 
                collected_data['subject'] + '/ses-' + collected_data['session'] + '/processed/powder/')

    if not os.path.exists(processedFolder):
        os.makedirs(processedFolder)

    fileBase = ('sub-' +  collected_data['subject'] + '_ses-' + 
                collected_data['session'] + '_run-0')
    
    #Split the DWI data into individual volumes
    #Load the info file
    info = pd.read_excel(infoPath)

    for file in os.listdir(splitFolder):

        if 'nii' in file:
            #Find the run number
            runNum = file.split('run-0')[1].split('_')[0]

            #If run number contains a letter
            if runNum[-1].isalpha():
                

                #Get the number of b0 images
                #Find the row in the info file with the run number and DWI
                rowInfo = info[(info['Run Number'] == str(runNum)) & (np.isnan(info['nDir']) == False)]

                #Load the scan
                scanHold = nib.load(splitFolder + file)
                scanData = scanHold.get_fdata()

                #b0s 
                b0s = int(rowInfo['nb0'].iloc[0])
                
                '''----------------------------load data---------------------------------'''
                #Remove b0 images
                strippedData = scanData[:,:,:,b0s:]
                #b0 images
                b0Data = scanData[:,:,:,:b0s]

                #Load b values 
                bvals = np.loadtxt(splitFolder + fileBase + runNum + '_dwi_denoised_degibbs.bval')
                #Find unique b values
                #Incase they are similiar but not the same, round to 2 significant figures
                bvalRound = np.round(bvals,-2)
                bvalsUnique = np.unique(bvalRound)

                #Load b vector 
                bvec = np.loadtxt(splitFolder + fileBase + runNum + '_dwi_denoised_degibbs.bvec')
                #Find unique b values

                #For each b value, generate a mean image
                for gg in bvalsUnique:
                    if gg != 0: 

                        #Find indices of b value
                        bInd = np.where(bvalRound == gg)[0]

                        #Make powder average
                        powderAve = np.mean(strippedData,axis=3)

                        #Save powder average
                        img = nib.Nifti1Image(powderAve, scanHold.affine, scanHold.header)
                        #Save file
                        nib.save(img,  processedFolder + fileBase + runNum + '_average.nii')

                        #Save powder average bvectors 
                        bvecHold = np.mean(bvec[:,bInd], axis=1)
                        np.savetxt(processedFolder + fileBase + runNum + '_average.bvec', bvecHold)

                        #Make powder average
                        powderVar = np.std(strippedData,axis=3)

                        #Save powder average
                        img = nib.Nifti1Image(powderVar, scanHold.affine, scanHold.header)
                        #Save file
                        nib.save(img,  processedFolder + fileBase + runNum + '_variance.nii')

                        #Save powder average bvectors 
                        bvecHold = np.mean(bvec[:,bInd],axis=1)
                        np.savetxt(processedFolder + fileBase + runNum + '_variance.bvec', 
                                    bvecHold)
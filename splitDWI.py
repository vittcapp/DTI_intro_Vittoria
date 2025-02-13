#!/usr/bin/python

'''----------------------------------------------------------------------
Split the DWI data into individual volumes and save them as separate files 
with the b0s in each volume

Author: Emma Thomson 
Institution: Danish Research Centre for Magnetic Resonance
Data: October 2024
Email: emmat@drcmr.dk

------------------------------------------------------------------------'''

def splitDWI(subject, session, infoPath):  

    '''----------------------------packages----------------------------------'''
    import numpy as np
    import nibabel as nib
    import pandas as pd
    import os
    import math

    gamma = 0.2675 # Unit: rad/(mT.ms)


    #processedFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' + 
     #           subject + '/ses-' + session + '/processed/denoised/')
    processedFolder =( 'C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/sub-' + 
                subject + '/ses-' + session + '/processed/denoised/')
    
   
    
    dwiFolder = ('C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/sub-' + 
                subject + '/ses-' + session +  '/dwi/')
    
    #Split the DWI data into individual volumes
    #Load the info file
    info = pd.read_excel(infoPath)

    #Create split spreadsheet path 
    splitInfoPath = infoPath.split('ses-')[0] +  'ses-' + session + '_splitData.xlsx'

    dataList = list()
    dataListTitle = ['Date', 'ENum', 'Run Number', 'nAve', 'TE [ms]', 'TR [ms]', 
                    'flipAngle [degrees]', 'VoxelSize [mm]', 'AcqTime [s]', 
                    'bvalue [s/mm2]', 'nDir', 'nDwi', 'nb0', 'delta [ms]', 
                    'Delta [ms]', 'G_mag [mT/mm]']
    
   #Split folder 
    splitFolder = ('C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/sub-' + 
                 subject + '/ses-' + session +  '/processed/split/')
    # If it doesnt exist then create it
    if not os.path.exists(splitFolder):
        os.makedirs(splitFolder) 
    
    #For each scan, split the volumes
    for scan in os.listdir(processedFolder):
        if 'denoised_degibbs' in scan:


            #Find in the info file
            runNum = scan.split('run-0')[1].split('_')[0]

            #Find the row in the info file with the run number and DWI
            rowInfo = info[(info['Run Number'] == int(runNum)) & (np.isnan(info['nDir']) == False)]

            #Load the scan
            scanHold = nib.load(processedFolder + scan)
            scanData = scanHold.get_fdata()

            #b0s 
            b0s = int(rowInfo['nb0'].iloc[0])
            b0scans = np.zeros((scanData.shape[0], scanData.shape[1], scanData.shape[2], b0s))

            #Save the b0s
            b0scans = scanData[:,:,:,0:b0s]
            meanB0 = np.mean(b0scans, axis=3)
            b0name = scan[:-7] + '_b0' + scan[-7:]
            b0Scan = nib.Nifti1Image(meanB0, scanHold.affine)
            nib.save(b0Scan, splitFolder + b0name)

            #How many volumes are there
            NumOfScans = scanData.shape[3] - b0s
            nVolumes = int(NumOfScans/int(rowInfo['nDir'].iloc[0]))

            splitData = np.zeros((scanData.shape[0], scanData.shape[1], scanData.shape[2], 
                                int(rowInfo['nDir'].iloc[0]) + b0s))
            
            #Load the bvector file 
            bvectorFile = (dwiFolder + 'sub-' + subject + '_ses-' + session + 
            '_run-0' + str(runNum) + '_dwi.bvec')
            bvector = np.loadtxt(bvectorFile)

            #Load the bvalue file
            bvalueFile = (dwiFolder + 'sub-' + subject + '_ses-' + session +
            '_run-0' + str(runNum) + '_dwi.bval')
            bvalue = np.loadtxt(bvalueFile)

            splitVector = np.zeros((3, int(rowInfo['nDir'].iloc[0]) + b0s))
            splitValue = np.zeros((1, int(rowInfo['nDir'].iloc[0]) + b0s))
            
            #for each volume add the b0s    
            for i in range(nVolumes):
                splitData[:,:,:,0:b0s] = scanData[:,:,:,0:b0s]
                splitData[:,:,:,b0s:] = scanData[:,:,:,b0s + i::nVolumes]

                scanName = scan.split('_run-0' + str(runNum))
                scanName = scanName[0] + '_run-0' + str(runNum) + chr(97 + i) + scanName[1]
                #Save the split scan
                splitScan = nib.Nifti1Image(splitData, scanHold.affine)

                #Add the bvector to the split vector
                splitVector[:,:b0s] = bvector[:,:b0s]
                splitVector[:,b0s:] = bvector[:,b0s + i::nVolumes]

                vectorOut = splitFolder + scanName[:-7] + '.bvec'

                #Add the bvalue to the split value
                splitValue[:,:b0s] = bvalue[:b0s]
                splitValue[:,b0s:] = bvalue[b0s + i::nVolumes]

                valueOut = splitFolder + scanName[:-7] + '.bval'

                #Save the scan
                nib.save(splitScan, splitFolder + scanName)

                #Save the bvector
                np.savetxt(vectorOut, splitVector)

                #Save the bvalue
                np.savetxt(valueOut, splitValue)

                #Isolate the bvalue
                bvalues = rowInfo['bvalue [s/mm2]'].iloc[0]
                bvalues = bvalues.split('[')[1].split(']')[0]
                bval = bvalues.split(',')[i]

                #Calculate Gradient Magnitude
                G_mag = math.sqrt(int(float(bval)*10**-3) / (gamma**2 * int(rowInfo['delta [ms]'].iloc[0])**2 * 
                            (int(rowInfo['Delta [ms]'].iloc[0]) - int(rowInfo['delta [ms]'].iloc[0]))))*10**3

                #Add the scan to the data list 
                dataList.append([rowInfo['Date'].iloc[0], rowInfo['ENum'].iloc[0], 
                                (str(rowInfo['Run Number'].iloc[0]) + chr(97+i)), rowInfo['nAve'].iloc[0], 
                                rowInfo['TE [ms]'].iloc[0], rowInfo['TR [ms]'].iloc[0], 
                                rowInfo['flipAngle [degrees]'].iloc[0], 
                                rowInfo['VoxelSize [mm]'].iloc[0], rowInfo['AcqTime [s]'].iloc[0], 
                                bval, str(1), 
                                rowInfo['nDwi'].iloc[0], rowInfo['nb0'].iloc[0], 
                                rowInfo['delta [ms]'].iloc[0], rowInfo['Delta [ms]'].iloc[0], 
                                G_mag])
            
    #Add the data to the info file
    dataList = pd.DataFrame(dataList, columns = dataListTitle)
    dataList.to_excel(splitInfoPath, sheet_name='Split Data', index=False)
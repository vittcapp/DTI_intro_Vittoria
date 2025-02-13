'''-----------------------------------------------------------------------------
T2 fitting function

Author: Emma Thomson 
Institution: Danish Research Centre for Magnetic Resonance
Date: October 2024
Email: emmat@drcmr.dk

-----------------------------------------------------------------------------'''

def t2fitting(subject, session, ET2):

    '''----------------------------packages----------------------------------'''
    import os
    import numpy as np
    import nibabel as nib
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_squared_error
    from scipy.signal import medfilt2d


    '''---------------------------chose scans--------------------------------'''

    #Output folder 
    processedFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' +
             str(subject) + '/ses-' + str(session) + '/fitting/')
    
    if not os.path.exists(processedFolder):
        os.system('mkdir ' + processedFolder)
        processedFolder = processedFolder + '/t2fit/'
        os.system('mkdir ' + processedFolder)
    

    #Folder with split scans
    alignedFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' +
            str(subject) + '/ses-' + str(session) + '/processed/aligned/')

    #Read in info file
    infoPath = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' +
            str(subject) + '/sequenceData_ses-' + str(session) + '_splitData.xlsx')
    
    maskPath = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' +
            str(subject) + '/ses-' + str(session) + '/mask/mask.nii.gz')

    info = pd.read_excel(infoPath)

    #Find the delta 
    runNum = ET2[0]
    delta = info[info['Run Number'] == str(runNum)]['Delta [ms]'].iloc[0]

    #Load the data 
    for ii in range(len(ET2)):
        runNum = ET2[ii]
        scan = [ff for ff in os.listdir(alignedFolder) if 'run-0' + str(runNum) in ff]
        scan = [ff for ff in scan if '.nii' in ff]
        scanPath = alignedFolder + scan[0]
        scanDataHold = nib.load(scanPath).get_fdata()
        #Only the b0s
        nb0 = info[info['Run Number'] == str(runNum)]['nb0'].iloc[0]
        scanDataHold = scanDataHold[:,:,:,0:nb0]
        #Mean over the b0s
        scanDataHold = np.mean(scanDataHold, axis=3)
        scanDataHold = np.expand_dims(scanDataHold, axis=3)
        #If scan data does not exist
        if not 'scanData' in locals():
            scanData = scanDataHold
        else:
            scanData = np.concatenate((scanData, scanDataHold), axis=3)
        #scanData = scanData/np.linalg.norm(scanData)
        
    
    scanData = scanData[:,:,:,np.argsort(TE)]

    #Sort TEs by ascending order
    TE = np.array(TE)
    TE = TE[np.argsort(TE)]

    #Save the data
    scanData = nib.Nifti1Image(scanData, np.eye(4))
    nib.save(scanData, processedFolder + 't2data.nii.gz')

    '''---------------------------fitting------------------------------------'''

    #Fit an exponential decay to the data

    #Fit the data
    TE = TE/1000 #Convert to seconds
    TE = TE.reshape(-1,1)
    scanData = scanData.get_fdata()

    scanDataShape = scanData.shape

    #Mask the data
    mask = nib.load(maskPath).get_fdata()
    #tile mask
    mask = np.tile(np.expand_dims(mask,axis=3), (1,1,1, len(TE)))

    scanData = scanData*mask
    scanData[scanData == 0] = np.nan

    #Flatten scanData
    scanData = scanData.reshape(scanData.shape[0]*scanData.shape[1]*scanData.shape[2], scanData.shape[3])

    #Create the model
    model = LinearRegression()

    t2 = np.zeros(scanData.shape[0])
    mseArray = np.zeros(scanData.shape[0])
    for i in range(scanData.shape[0]):

        if np.isnan(scanData[i,:]).all():
            continue
        else:
            #Fit the model
            model.fit(TE.reshape(-1, 1), np.log(scanData[i,:].reshape(-1, 1)))

            #Predict the data
            y_pred = model.predict(TE)

            #Calculate the MSE
            mse = mean_squared_error(np.log(scanData[i,:]), y_pred)

            #Save the data and error to array 
            t2[i] = np.exp(-1/model.coef_)
            mseArray[i] = mse

    # Reshape the data 
    t2 = t2.reshape(scanDataShape[0], scanDataShape[1], scanDataShape[2])

    #Median filter the data in 2D
    for i in range(scanDataShape[2]):
       t2[:,:,i] = medfilt2d(t2[:,:,i], kernel_size=3)

    mseArray = mseArray.reshape(scanDataShape[0], scanDataShape[1], scanDataShape[2])

    #Save the data
    img = nib.Nifti1Image(t2, np.eye(4))
    nib.save(img, processedFolder + 't2map.nii.gz')

    #Save the error
    img = nib.Nifti1Image(mseArray, np.eye(4))
    nib.save(img, processedFolder + 'mse.nii.gz')




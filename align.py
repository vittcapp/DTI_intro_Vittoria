'''----------------------------------------------------------------------------- 
Regrid and register scans using MRTrix3
Author: Emma Thomson 
Institution: Danish Research Centre for Magnetic Resonance
Date: May 2024
Email: emmat@drcmr.dk

-----------------------------------------------------------------------------'''

def align(collected_data, testSwitch):
    '''----------------------------packages----------------------------------'''
    import os
    import numpy as np
    import nibabel as nib
   # from testFunctions import alignCheck
    import string
    from scipy.ndimage import affine_transform
    import subprocess

    '''---------------------------test inputs--------------------------------'''

    #if testSwitch:
     #   alignCheck.alignChecks(collected_data)

    '''----------------------------user inputs-------------------------------'''
    #Main scan folder
    subject = collected_data['subject']
    session = collected_data['session']
    
    '''-------------------------find reference data--------------------------'''

    #E numbers associated with the scan to be concatenated
    ENum = [file['file_value'] for file in collected_data['file_data']]

    #Find which is the anatomical scan
    #If multiple, pick the first
    for file in collected_data['file_data']:
        if file['data_type'] == 'Anatomy':
            anatFile = file['file_value']

    #Get the anatomical file path
    fileBase = 'sub-' + subject + '_ses-' + str(session) + '_t2_degibbs'
    anatFilePath = ('C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/sub-' +
                subject + '/ses-' + str(session) + '/processed/denoised/' + fileBase + '.nii.gz')
    
    #Load the anatomical file
    anatImg = nib.load(anatFilePath)
    anatData = anatImg.get_fdata()

    #Processed folder
    proccessedFolder = ('C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/sub-' +
                        subject + '/ses-' + str(session) + '/processed/aligned/')
    if not os.path.exists(proccessedFolder):
        os.makedirs(proccessedFolder)

    #Flip data updown 
    #anatData = np.fliplr(anatData)
    anatData = np.flipud(anatData)
    
    #Save the anatomical data with 'regrid'
    img = nib.Nifti1Image(anatData, anatImg.affine)

    anatFileRotPath = proccessedFolder + fileBase + '_regrid_registered.nii.gz'
    nib.save(img, anatFileRotPath)

    #Get voxel size
    voxelSize = anatImg.header.get_zooms() 
    
    '''------------------------regrid and register--------------------------'''

    #Loop through the non-anatomical scans
    for file in collected_data['file_data']:
        if file['file_value'] != anatFile:

            fileBase = ('sub-' +  subject + '_ses-' + str(session) + '_run-0' +  
                        str(file['run']) + '_dwi_denoised_degibbs_b0')
        
            filePath = ('C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/sub-'
                        + subject + '/ses-' + str(session) + '/processed/split/' + 
                        fileBase + '.nii.gz')
            outputPath = ('C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/sub-'
                        + subject + '/ses-' + str(session) + '/processed/aligned/' +
                        fileBase[:-20] + '_regrid.nii.gz')
            outputTransform = ('C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/sub-'
                        + subject + '/ses-' + str(session) + '/processed/aligned/' +
                        fileBase[:-20] + '_transform.txt')

            '''----------------------------regrid-------------------------------'''
            #This command does nothing
            #Regrid the data to the anatomical scan
            #command  = ('mrgrid ' + filePath  + ' regrid -template ' + 
             #           anatFileRotPath +  ' ' +  outputPath + ' -force')
             #os.system(command)

            command = ('C:/msys64/mingw64/bin/mrgrid "' + filePath.replace('"', '\\"') + '" regrid -template "' +
            anatFileRotPath.replace('"', '\\"') + '" "' + outputPath.replace('"', '\\"') + '" -force')

            print('command is ', command)
            subprocess.run([r"C:/msys64/usr/bin/bash.exe", "-c", command])

            '''---------------------------register-------------------------------'''
            #Register the data to the anatomical scan
            #command = ('mrregister ' + filePath + ' ' + anatFileRotPath + ' -rigid '
             #           + outputTransform + ' -type rigid -force')
            #os.system(command)
            command = ('C:/msys64/mingw64/bin/mrregister "' + filePath.replace('"', '\\"') + '" "' + 
             anatFileRotPath.replace('"', '\\"') + '" -rigid "' + outputTransform.replace('"', '\\"') + 
           '" -type rigid -force')
            subprocess.run([r"C:/msys64/usr/bin/bash.exe", "-c", command])


            #Transform the data
            #command = ('mrtransform ' + filePath + ' -linear ' + outputTransform +
             #           ' ' + outputPath[:-7] + '_registered.nii.gz -force')
            command = ('C:/msys64/mingw64/bin/mrtransform "' + filePath.replace('"', '\\"') + '" -linear "' + 
            outputTransform.replace('"', '\\"') + '" "' + outputPath[:-7].replace('"', '\\"') + 
            '_registered.nii.gz" -force')
            #os.system(command)
            subprocess.run([r"C:/msys64/usr/bin/bash.exe", "-c", command])


            #Remove the regrid file
            #os.system('rm ' + outputPath)
            os.system('del "' + outputPath.replace('"', '\\"') + '"')

    #Apply the appropriate transformations to the full dwi volumes 
    splitFolder = ('C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/sub-' +
                        subject + '/ses-' + str(session) + '/processed/split/')
    
    #Output folder 
    alignedFolder = ('C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/sub-' +
                        subject + '/ses-' + str(session) + '/processed/aligned/')
    
    for scan in os.listdir(splitFolder):
        if 'degibbs.nii.gz' in scan and 'b0' not in scan:
                
            #File base
            fileBase = scan[:-24]

            #Open the scan
            scanPath = splitFolder + scan
            scanImg = nib.load(scanPath).get_fdata()

            #Get the run number
            runNum = scan.split('run-0')[1].split('_')[0]

            bvectorFile = ('C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/sub-'
                + subject + '/ses-' + str(session) + '/processed/split/' +
                'sub-' +  subject + '_ses-' + str(session) + '_run-0' +
                str(runNum) + '_dwi_denoised_degibbs.bvec')

            #If the run number contains a letter, remove it
            if runNum[-1] in string.ascii_lowercase:
                runNum = runNum[:-1]

            transformFile = ('C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/sub-'
                        + subject + '/ses-' + str(session) + '/processed/aligned/' +
                        'sub-' +  subject + '_ses-' + str(session) + '_run-0' +
                        str(runNum) + '_dwi_transform.txt')
            
            
            outputPath = alignedFolder + fileBase + '_regrid_registered.nii.gz'
            
            #Regrid the scan
           # command  = ('mrgrid ' + scanPath  + ' regrid -template ' + 
            #            anatFileRotPath +  ' -scale 1,1,1 ' +  outputPath + ' -force')
            #os.system(command)
            command  = ('C:/msys64/mingw64/bin/mrgrid "' + scanPath.replace('"', '\\"') + '" regrid -template "' + 
                    anatFileRotPath.replace('"', '\\"') + '" -scale 1,1,1 "' + outputPath.replace('"', '\\"') + '" -force')
            subprocess.run([r"C:/msys64/usr/bin/bash.exe", "-c", command])  # Apply the transformation

            command = ('C:/msys64/mingw64/bin/mrtransform "' + scanPath.replace('"', '\\"') + '" -linear "' + 
                    transformFile.replace('"', '\\"') + '" "' + outputPath[:-7].replace('"', '\\"') + '_registered.nii.gz" -force')
            subprocess.run([r"C:/msys64/usr/bin/bash.exe", "-c", command])


            #Apply the transformation
            #command = ('mrtransform ' + scanPath + ' -linear ' + transformFile +
             #           ' ' + outputPath[:-7] + '_registered.nii.gz -force')
            #os.system(command)

            #Apply the transformation to the bvector file
            bvector = np.loadtxt(bvectorFile)
            transform = np.loadtxt(transformFile)
            transform = transform[:3,:3]
            bvector = np.dot(transform, bvector)
            np.savetxt(alignedFolder + fileBase + '_regrid_registered.bvec', bvector, fmt='%.6f')

            #Remove the regrid file
            #os.system('rm ' + outputPath)
            os.system('del "' + outputPath.replace('"', '\\"') + '"')


            
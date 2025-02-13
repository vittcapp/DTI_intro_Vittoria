'''-----------------------------------------------------------------------------
Denoise DWI data using MP-PCA denoising and Gibbs ringing removal

Author: Emma Thomson 
Institution: Danish Research Centre for Magnetic Resonance
Date: May 2024
Email: emmat@drcmr.dk

#NOTE: Before running this file, run the sortDataBIDS.py file to sort the data 
       into the appropriate format 

-----------------------------------------------------------------------------'''

def denoise(collected_data, processedFolder, testSwitch):
    import os
    import nibabel as nib
    import numpy as np
    import subprocess

    

    '''---------------------------concatenate--------------------------------'''

    #Concatenate the images to create a single nifti file
    splittingDims = []
    for files in collected_data['file_data']:
        
       #For the first file, get the number of time dimensions
        if files['data_type'] == 'DWI':
            print('here')
            #dwiFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' + 
             #   collected_data['subject'] + '/ses-' + collected_data['session'] + '/dwi/')
            
            dwiFolder = ("C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/sub-"+
                        collected_data['subject'] + '/ses-' + collected_data['session'] + "/dwi/")
            print('dwiFolder is', dwiFolder)
            fileBase = ('sub-' +  collected_data['subject'] + '_ses-' + 
                collected_data['session'] + '_run-0' +  files['run'])
            print('filebase is', fileBase)

            
            fileName = dwiFolder + fileBase + '_dwi.nii.gz' 
            img =nib.load(fileName)
            data = img.get_fdata()
            print("Input Image Shape:", data.shape)
            splittingDims.append(data.shape[3])
            print("Input Image Shape:", data.shape)
            #Output file
            denoiseFile = processedFolder + fileBase + '_dwi_denoised.nii.gz'
            print('denoiseFile:' +denoiseFile, 'filebase', fileBase, 'processedfolder', processedFolder )

            '''-----------------------------tests-----------------------------'''

            '''----------------------------denoising---------------------------------'''

            #Denoise data
            
            #MP-PCA denoising
            command = ('C:/msys64/mingw64/bin/dwidenoise "' + fileName.replace('"', '\\"') + '" "' 
            + denoiseFile.replace('"', '\\"') + '" -force -extent 5,5,5' )
            print('command is ', command)
            subprocess.run([r"C:/msys64/usr/bin/bash.exe", "-c", command])

            #command = ('dipy_denoise_mppca ' + fileName + ' --patch_radius 1 --out_dir ' + processedFolder)
            #command = ('dipy_denoise_nlmeans ' + fileName + ' --sigma 100 --patch_radius 2 --out_dir ' + processedFolder + ' --force')
           # os.system(command)
           
             # Command for denoising using dipy
            command = ('dipy_denoise_nlmeans ' + denoiseFile + ' --sigma 100 --patch_radius 5 --out_denoised ' + denoiseFile + ' --force')

            # Run the command using subprocess
            subprocess.run(command, shell=True)

        
            if os.path.exists(denoiseFile):
                command = ('C:/msys64/mingw64/bin/mrcalc "' + fileName.replace('"', '\\"') + '" "' + 
                    denoiseFile.replace('"', '\\"') + '" -subtract "' + 
                    (denoiseFile[:-7]).replace('"', '\\"') + '_residuals.nii.gz" -force')
                subprocess.run([r"C:/msys64/usr/bin/bash.exe", "-c", command])
            else:
                print(f"Error: The file {denoiseFile} does not exist.")
            #Calculate residuals
            
            # Calculate residuals using mrcalc
            command = ('C:/msys64/mingw64/bin/mrcalc "' + fileName.replace('"', '\\"') + '" "' + 
                    denoiseFile.replace('"', '\\"') + '" -subtract "' + 
                    (denoiseFile[:-7]).replace('"', '\\"') + '_residuals.nii.gz" -force')
            subprocess.run([r"C:/msys64/usr/bin/bash.exe", "-c", command])

            #DeGibbs data
            
            command = ('C:/msys64/mingw64/bin/mrdegibbs "' + fileName.replace('"', '\\"') + '" "' + denoiseFile[:-7].replace('"', '\\"') + '_degibbs.nii.gz" -force')
            subprocess.run([r"C:/msys64/usr/bin/bash.exe", "-c", command])


        if files['data_type'] == 'Anatomy':

            #anatFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' +  
             #   collected_data['subject'] + '/ses-' + collected_data['session'] + '/anat/')
            anatFolder = ("C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/sub-"+
                         collected_data['subject'] + '/ses-' + collected_data['session'] + "/anat/")
            fileBase = ('sub-' +  collected_data['subject'] + '_ses-' + 
                collected_data['session'])
            
            fileName = anatFolder + fileBase + '_mtir.nii.gz'
            img = nib.load(fileName)
            data = img.get_fdata()

            #Output file
            denoiseFile = processedFolder + fileBase + '_t2_degibbs.nii.gz'
            print(denoiseFile)

            #DeGibbs data
            #command = ('mrdegibbs ' + fileName + ' ' + denoiseFile + 
             #       ' -force') 
            #os.system(command)


    if testSwitch:
        print(' ---> Denoising checks complete')

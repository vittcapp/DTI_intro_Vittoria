'''-----------------------------------------------------------------------------
Author: Emma Thomson 
Institution: Danish Research Centre for Magnetic Resonance
Date: October 2024
Email: emmat@drcmr.dk

The steps performed in this pipeline are as follows:

DATA PROCESSING:

1. Bids-ification of the data - THIS IS WRONG. SPEAK TO MARIO
2. Input checks - scans exist, are in the correct format, etc.
3. Denoising - MPPCA and deGibbs
4. Split scans - into individual volumes
5. Aligning - to anatomy image 
6. Masking - to remove non-brain tissue
7. Normalisation - against b0
8. Powder averaging - processing for SANDI fitting

DEBUG HINTS:
 - BIDS will fail with multiple reconstuction types (e.g. DTI)
 - Masking requires one scan with at least 3 non-zero b values
 - Cannot handle scan sessions with only one DWI image acquired (can fix this manually) 
 - Cannot handle more than 9 DWI scans
-----------------------------------------------------------------------------'''

'''-----------------------------packages-------------------------------------'''
import numpy as np
import nibabel as nib
import pandas as pd
import os
import sys
import shutil
'''-----------------------------functions------------------------------------'''

# Add the directory containing the 'functions' folder to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from functions.align import align
from functions.denoise import denoise
from functions.mask import mask
from functions.bids import bidsConvert
from functions.splitDWI import splitDWI
from functions.normalisation import normalisation
from functions.powderAve import powderAve

'''--------------------------------user inputs-------------------------------'''

#Folder name 
folder = 'M1436_1_1_20241202_131735'

#Subject name 
subject = '423M'


session = '1'

#Anatomy image 
EAnat = 14 

#DWI images 
EDWI = [15]

#Turn all switches on
switchOn = False

'''----------------------------0. Switches------------------------------------'''

#For test purposes you can switch off any part of the pipeline but it is not 
#compatible unless these steps have been run previously.

bidsSwitch =    False ; denoiseSwitch = False; splitSwitch = False; alignSwitch = True
maskSwitch = False; normaliseSwitch = False; powAveSwitch = False 


if switchOn:
    bidsSwitch = True; denoiseSwitch = True; splitSwitch = True; alignSwitch = True
    maskSwitch = True; normaliseSwitch = True; powAveSwitch = True

'''-----------------------1. Bids-ification of the data----------------------'''

if bidsSwitch:

    #Create new folder for containing only the scans you're interested in 
    rawFolder = 'C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/rawData/'
    holdFolder =  rawFolder + 'hold'
    # create new folder with only the two files for subjects 14 and 15
    print(holdFolder)

    # Ensure the destination exists
    if not os.path.exists(holdFolder):
        print('No hold folder')
        os.makedirs(holdFolder)

    #If it exists clear it, if not then create it
    # if os.path.exists(holdFolder):
    #    os.system('rmdir /s /q' + holdFolder)
    #os.system('mkdir ' + holdFolder)

    #Find old folder full name 
    #unfilteredDataFolderName = [ x for x in os.listdir(rawFolder) if folder in x]
    unfilteredDataFolderName = [x for x in os.listdir(rawFolder) if folder in x and not x.startswith('._')]

    # Ensure we found the correct folder
    if not unfilteredDataFolderName:
        raise FileNotFoundError("Matching unfiltered data folder not found!")

    #Add files to the new folder 
    #DWI
    #for scan in EDWI:
    #    os.system('cp -r ' + rawFolder + unfilteredDataFolderName[0] + '/' + 
     #             str(scan) + ' ' + holdFolder + '/' + str(scan))
    #Anatomy
   # os.system('cp -r ' + rawFolder + unfilteredDataFolderName[0] + '/' + 
     #       str(EAnat) + ' ' + holdFolder + '/' + str(EAnat))
    
    # Other files
    #os.system('cp -r ' + rawFolder + unfilteredDataFolderName[0] + 
    #    '/ScanProgram.scanProgram ' + holdFolder + '/ScanProgram.scanProgram')
    #os.system('cp -r ' + rawFolder + unfilteredDataFolderName[0] + 
     #   '/subject ' + holdFolder + '/subject')
    #os.system('cp -r ' + rawFolder + unfilteredDataFolderName[0] +
     #   '/AdjStatePerStudy ' + holdFolder + '/AdjStatePerStudy')
    #os.system('cp -r ' + rawFolder + unfilteredDataFolderName[0] +
     #   '/AdjProtocols ' + holdFolder + '/AdjProtocols')
   
# Get the full source path
    print('unfiltered dataname[0]:'+unfilteredDataFolderName[0])
    sourceFolder = os.path.join(rawFolder, unfilteredDataFolderName[0]) 

    # Define the copy function for Windows
    def windows_copy(source, destination):
        os.system(f'xcopy /E /I /Y "{source}" "{destination}"')

    #Add files to the new folder
    # Copy DWI scans
    for scan in EDWI:
        source = os.path.join(rawFolder, unfilteredDataFolderName[0], str(scan))
        destination = os.path.join(holdFolder, str(scan))
        windows_copy(source, destination)
    
    # Copy Anatomy folder (t2)
    source = os.path.join(rawFolder, unfilteredDataFolderName[0], str(EAnat))
    print('SOURCE:',source)
    destination = os.path.join(holdFolder, str(EAnat))
    windows_copy(source, destination)

    # Copy Other files
    files_to_copy = [
        ('ScanProgram.scanProgram', 'ScanProgram.scanProgram'),
        ('subject', 'subject'),
        ('AdjStatePerStudy', 'AdjStatePerStudy'),
        ('AdjProtocols', 'AdjProtocols')
    ]

    for src_file, dest_file in files_to_copy:
        source = os.path.join(rawFolder, unfilteredDataFolderName[0], src_file)
        destination = os.path.join(holdFolder, dest_file)
        windows_copy(source, destination)


    
    #Bidsify the data
    bidsConvert(holdFolder, session)

    print('---> BIDs-ification complete')

'''-----------------------2. Input checks------------------------------------'''

#Create collected data dictionary
collected_data = {'subject': subject, 'session': session}

#Add file data to the dictionary
file_data = []
#Anat scan 
file_data.append({"file_value": str(EAnat), "data_type": "Anatomy"})
#DWI scans
for scan in EDWI:
    file_data.append({"file_value": str(scan), "data_type": "DWI"})
collected_data['file_data'] = file_data
print(collected_data)

#Read in the info file and add the additional fields
#infoPath = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' + subject + 
#            '/sequenceData_ses-' + session + '.xlsx')
infoPath = ('C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/sub-' + subject + 
            '/sequenceData_ses-' + session + '.xlsx')
            
            
# to ask if it is correct


info = pd.read_excel(infoPath)
print(info.columns)

for scan in collected_data['file_data']:
        
    scanNum = int(scan['file_value'])
    scanRow = info[info['ENum'] == scanNum]

    #TE, TR and run number
    scan['TE'] = str(int(scanRow['TE [ms]'].iloc[0]))
    scan['TR'] = str(int(scanRow['TR [ms]'].iloc[0]))
    scan['run'] = str(int(scanRow['Run Number'].iloc[0]))

    # DWI fields
    if scan['data_type'] == 'DWI':
        scan['b0'] = str(int(scanRow['nb0'].iloc[0]))
        scan['delta'] = str(int(scanRow['delta [ms]'].iloc[0]))
        scan['Delta'] = str(int(scanRow['Delta [ms]'].iloc[0]))
    else: 
        scan['b0'] = '0'; scan['delta'] = '0'; scan['Delta'] = '0'
        
'''-----------------------3. Denoising--------------------------------------'''

if denoiseSwitch:

    #Create processed folder
    #processedFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' + 
    #                    subject + '/ses-' + session + '/processed')

    processedFolder = ('C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/sub-' + 
                    subject + '/ses-' + session + '/processed')
    # If it doesnt exist then create it
    if not os.path.exists(processedFolder):
       os.system(f'mkdir "{processedFolder}"')
        
    processedFolder = processedFolder + '/denoised/'
    if not os.path.exists(processedFolder):
        os.system(f'mkdir "{processedFolder}"')

    #processedFolder = os.path.join(processedFolder, 'denoised')
    #if not os.path.exists(processedFolder):
    #    os.system(f'mkdir "{processedFolder}"')
    
                
    #Run the denoising
    denoise(collected_data, processedFolder, False)



    print(' ---> Denoising complete')

'''-----------------------------4. Split scans-------------------------------'''

if splitSwitch:
   
   splitDWI(subject, session, infoPath)

   print(' ---> Splitting DWIs complete')

'''-----------------------------5. Aligning----------------------------------'''

if alignSwitch:
    #Align the DWI scans to the anatomy image
    align(collected_data, False)

    ## THIS DOES NOT WORK YET
    #Or rather the code runs but the output is not as expected

    #alignToAtlas(collected_data)

    print(' ---> Aligning complete')

'''-----------------------------6. Masking-----------------------------------'''

if maskSwitch:
    #Create processed folder
    #maskFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' + 
    #                    subject + '/ses-' + session + '/mask/')
    maskFolder = ('C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/sub-' + 
                        subject + '/ses-' + session + '/mask/')
    # If it doesnt exist then create it
    if not os.path.exists(maskFolder):
        os.system('mkdir ' + maskFolder)

    #Run the mask
    mask(collected_data, maskFolder, False)

    print(' ---> Masking complete')

'''-----------------------------7. Normalisation----------------------------'''

if normaliseSwitch:
    #Normalise the DWI scans
    normalisation(collected_data, False)

    print(' ---> Normalisation complete')


'''--------------------------8. Powder averaging ----------------------------'''

if powAveSwitch:
    #Run the powder averaging
    infoPath = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' + subject + 
            '/sequenceData_ses-' + session + '_splitData.xlsx')

    # output of split DWI???
    powderAve(collected_data, infoPath)

    print(' ---> Powder averaging complete')


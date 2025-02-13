#!/usr/bin/python

'''----------------------------------------------------------------------
Convert dataset to BIDS format

Author: Emma Thomson 
Institution: Danish Research Centre for Magnetic Resonance
Data: May 2024
Email: emmat@drcmr.dk

Code adapted from CoMPy toolbox by Mario Corral

------------------------------------------------------------------------'''
'''--------------------------packages---------------------------------'''
import os
#Add CoMPy toolbox to the path
import sys
import pandas as pd
sys.path.append(os.path.join('C:/Users/vitto'))
#sys.path.append(os.path.join('/Users/emmathomson/Dropbox/Work/Coding/toolboxes'))
from CoMPy.compy.bids import bids_helper
from CoMPy.compy.bids import bids_convert
import pydicom
import numpy as np
import re

'''--------------------------user inputs---------------------------------'''

def bidsConvert(imagingFolder, session):

    imagingFolder = imagingFolder.split('/')[-1] # CHECK if imaging forlder is fine like that
    # take the last folder in the path of imaging_folder.
   # e.g. if imaging folder is rawFolder = 'C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/rawData'
   # then in takes raw data
                  
    """-----------------parsing sequence information -------------------"""

    #mainFolder = '/Users/emmathomson/Dropbox/Work/Scanning/MRdata'
    mainFolder =  'C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode'
    
    unfilteredDataFolder = mainFolder +'/rawData/' + imagingFolder #'/rawData/' + imagingFolder
     
    print(unfilteredDataFolder)
   #Load sequence information file
    path = unfilteredDataFolder + '/ScanProgram.scanProgram'
    print(path)
    with open(path , 'r') as f2:
        sequenceInformation = f2.read()

    #Split the sequence information at the sequecne identifiers '(E XX)'
    splittingSequenceInfo = sequenceInformation.split('(E')
    #Now have set of strings beginning 'XX)</display name>\n' 
    #Isolate those numbers 
    #Need to do iteratively as splittingSequenceInfo is a list
    #Save new split string as a list
    ENumberSplit = list()
    for xx in range(len(splittingSequenceInfo)):
        ENumberSplit.extend(splittingSequenceInfo[xx].split(')</displayName>\n'))

    #Save these E numbers as an array, to iterate through
    ENumbers = ENumberSplit[1::2]
    print(ENumbers)
    '''---------------------------check for dicom------------------------------'''

    ENumberNew = []

    for ee in range(len(ENumbers)):
        
        #Find the file number 
        ENum = ENumbers[ee]
        print(ENum)
        #File path
        dataPath = unfilteredDataFolder + '/' + str(ENum)  + '/pdata/1/dicom'
        #print(dataPath)

        #Check if the dicom folder exists
        if os.path.exists(dataPath):
            #Add the E number to the new list
            ENumberNew.append(ENum)


    ENumbers = ENumberNew

    '''--------------------------extract subject ID---------------------------------'''

    #from first folder take the visu_pars file and extract the subject ID
    with open(unfilteredDataFolder + '/' + str(ENumbers[0]) + '/visu_pars', 'r') as f: 
        visu_pars = f.read()
   # with open(os.path.join(unfilteredDataFolder, str(ENumbers[0]), 'visu_pars'), 'r') as f: 
      #  visu_pars = f.read()


    #Find the subject ID
    subjectID = visu_pars.split('>\n##$VisuSubjectId=')[0].split('<')[-1]
    print(subjectID)

    '''--------------------------create initial files---------------------------------'''

    # Set the path to the dataset
    dicom_dir = unfilteredDataFolder

    # For the sake of the organization, let's create a project folder
    # and get the output of the conversion inside it
    #metadata_dir = '/Users/emmathomson/Dropbox/Work/Scanning/MRdata/rawDataFiles'
    metadata_dir = 'C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/rawDataFiles' # correct to create a new folder?
    #metadata_dir = os.path.join('C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/rawDataFiles')
    metadata_file = os.path.join(metadata_dir, imagingFolder)
    json         = True  # If you want to generate a json file template. Later, bids_convert will use it to fill the bids-sidecar files.
    format       = 'xlsx'
    bids_helper(input = dicom_dir, output = metadata_file, json = json, format = format)

    # Pause execution
    #input("Press Enter to continue after editing the metadata file")

    '''--------------------------modify metadata file---------------------------------'''

    #Read in the xlsx metadata file
    metadata = pd.read_excel(metadata_file + '.xlsx')
    print('metadata file name:', metadata)

    #Modify the metadata file to include the correct subject and session information
    #For each row in the metadata file
    for ii in range(len(metadata)):

        #Update the subject ID
        metadata.loc[ii,'SubjID'] = subjectID
        #Update the session ID
        metadata.loc[ii,'SessID'] = session

        #Update the dataType (I want SWI in a separate folder)
        #Check E number 
        ENum = metadata['ScanID'][ii]
        #Check if in the list of E numbers 
        if str(round(ENum)) in ENumbers:
            #dataPath = unfilteredDataFolder + '/' + str(ENum)
            dataPath = os.path.join(unfilteredDataFolder, str(ENum))
            #Sequence name 
            #From method file 
            with open(os.path.join(dataPath, 'method')) as methodFile:
                methodFile = methodFile.read()
              
           # methodFile = open(dataPath +  '/method')
           # methodFile = methodFile.read()
            #Split at identifier
            sequenceName = methodFile.split('##$Method=')
            #Remove trailing arrow
            sequenceName = sequenceName[1].split('<')
            sequenceName = sequenceName[1].split('>')[0]
            if 'FLASH' in sequenceName:
                metadata.loc[ii, 'DataType'] = 'swi'
            
            #Update the modality
            if 'FLASH' in sequenceName:
                modality = 'swi'
            elif 'FISP' in sequenceName:
                modality = 't2'
            elif 'RARE' in sequenceName:
                modality = 'mtir'
            elif 'Dti' in sequenceName:
                modality = 'dwi'
            metadata.loc[ii,'modality'] = modality
        else: 
            #Remove the row if the E number is not in the list
            metadata = metadata.drop(ii)

    #Save the updated metadata file
    metadata.to_excel(metadata_file + '.xlsx', index = False)
        
    '''--------------------------convert data to BIDS---------------------------------'''

    # Now you are ready to convert the dataset to BIDS
    datasheet_path = metadata_file + '.xlsx'
    json_path      = metadata_file + '.json'

    bids_convert(dicom_dir, datasheet_path, json_path, mainFolder)

    '''--------------------------clean up folder---------------------------------'''
    #Remove the json files 
    #If there are json files in the mainFolder, remove them
    jsonFiles = [ x for x in os.listdir(mainFolder) if '.json' in x]
    for jj in range(len(jsonFiles)):
        os.remove(mainFolder + '/' + jsonFiles[jj])

    #Repeat for tsv files
    tsvFiles = [ x for x in os.listdir(mainFolder) if '.tsv' in x]
    for jj in range(len(tsvFiles)):
        os.remove(mainFolder + '/' + tsvFiles[jj])

    #And for the README file
    readmeFiles = [ x for x in os.listdir(mainFolder) if 'README' in x]
    for jj in range(len(readmeFiles)):
        os.remove(mainFolder + '/' + readmeFiles[jj])

        '''---------------------add sequence data to sheet-----------------------'''

    #Open empty list to save data
    dataList = list()
    dataListTitle = ['Date', 'ENum', 'Run Number', 'nAve', 'TE [ms]', 'TR [ms]', 
                    'flipAngle [degrees]', 'VoxelSize [mm]', 'AcqTime [s]', 
                    'bvalue [s/mm2]', 'nDir', 'nDwi', 'nb0', 'delta [ms]', 
                    'Delta [ms]', 'G_mag [mT/m]']

    #For each of the relavant sequences (E numbers) add the data to a xslx file
    count = 1
    for ee in range(len(ENumbers)):
        
        #Find the file number 
        ENum = ENumbers[ee]
        #File path
        dataPath = unfilteredDataFolder + '/' + str(ENum)

        #Find if its a dti sequence or not
        #Sequence name 
        #From method file 
        methodFile = open(dataPath +  '/method')
        methodFile = methodFile.read()
        

        #Split at identifier
        sequenceName = methodFile.split('##$Method=')
        #Remove trailing arrow
        sequenceName = sequenceName[1].split('<')
        sequenceName = sequenceName[1].split('>')[0]

        if 'Dti' not in sequenceName:
            try:
                # This doesnt work for mulitple folders because the BIDs convert
                # function can't handle multiple reconstructions
                dicomFolderRecon = dataPath + '/pdata/1/dicom'

                exampleDicom = os.listdir(dicomFolderRecon)[0]
                ds = pydicom.dcmread(dicomFolderRecon + "/" + exampleDicom, force=True)

                #Find information about the sequence
                #Not diffusion so some can be set to None
                bvalue = None;  nDir = None; nDwi = None; nb0 = None; 
                delta = None; Delta = None; G_mag = None
                nAve = int(ds["NumberOfAverages"].value)
                TE = float(ds["EchoTime"].value) 
                print('ECHO TIME IS', TE)
                TR = float(ds["RepetitionTime"].value)
                flipAngle = float(ds["FlipAngle"].value)
                date = ds["AcquisitionDate"].value
                voxelSize = [float(ds["PixelSpacing"].value[0]), 
                            float(ds["PixelSpacing"].value[1]), 
                            float(ds["SliceThickness"].value)]

                #Calculate the time between the first and last image
                #Find the first and last image
                firstImage = os.listdir(dicomFolderRecon)[0]
                lastImage = os.listdir(dicomFolderRecon)[-1]

                #Load the first and last image headers
                firstImage = pydicom.dcmread(dicomFolderRecon + "/" + firstImage)
                lastImage = pydicom.dcmread(dicomFolderRecon + "/" + lastImage)
                
                #Find the time between the first and last image
                acqTime = float(lastImage.timestamp) - float(firstImage.timestamp)

                dataList.append([date, ENum, 1, nAve, TE, TR,
                                flipAngle,  voxelSize, acqTime, bvalue, nDir,
                                nDwi, nb0, delta, Delta, G_mag])  
            except: 
                print('Error with non DTI sequence: ' + str(ENum))            
        else: 

            # This doesnt work for mulitple folders because the BIDs convert
            # function can't handle multiple reconstructions
            dicomFolderRecon = dataPath + '/pdata/1/dicom'
            exampleDicom = os.listdir(dicomFolderRecon)[0]
           
            if exampleDicom.startswith('._'): # eliminate files with _.
                    # Create the new file name by removing '._'
                    exampleDicom = exampleDicom[2:]
 
            print(exampleDicom)
            print(dicomFolderRecon + "/" + exampleDicom)
            #C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/rawData/M1436_1_1_20241202_131735/13/pdata/1/dicom/._MRIm01.dcm
            
            ds = pydicom.dcmread(dicomFolderRecon + "/" + exampleDicom, force=True)
            
            #Find the bvec and bval files
            methodPath = os.path.join(dataPath, 'method')
            with open(methodPath, 'r') as fid:
                lines = fid.readlines()
            nRep = None
            nDir = None
            nDwi = None
            nb0 = None
            dirs = []
            bvalue = []
            line = 0
            while 'PVM_NRepetitions' not in lines[line]:
                line += 1
            nRep = int(re.search(r'\d+', lines[line]).group())
            while 'PVM_DwNDiffDir' not in lines[line]:
                line += 1
            nDir = int(re.search(r'\d+', lines[line]).group())

            while 'PVM_DwNDiffExpEach' not in lines[line]:
                line += 1
            nDwi = int(re.search(r'\d+', lines[line]).group())

            while 'PVM_DwAoImages' not in lines[line]:
                line += 1
            nb0 = int(re.search(r'\d+', lines[line]).group())

            while 'PVM_DwDir' not in lines[line]:
                line += 1
            while len(dirs) < 3*nDir:
                line += 1
                dirs.extend([float(x) for x in 
                            re.findall(r"[-+]?\d*\.\d+|\d+",
                                        lines[line])])
            
            dirs = np.array(dirs).reshape((3, nDir)).T
            dirs = np.repeat(dirs, nDwi, axis=0)
            dirs = np.vstack((np.zeros((nb0, 3)), dirs))

            while 'PVM_DwBvalEach' not in lines[line]:
                line += 1
            while len(bvalue) < nDwi:
                line += 1
                bvalue.extend([float(x) for x in 
                            re.findall(r"[-+]?\d*\.\d+|\d+",
                                        lines[line])])

            bvalues = np.array(bvalue)
            bvalues = np.hstack((np.zeros(nb0), np.tile(bvalues, nDir)))

            #Find the effective bvec and bval files
            methodPath = os.path.join(dataPath, 'method')
            with open(methodPath, 'r') as fid:
                lines = fid.readlines()
            nRep = None
            nDir = None
            nDwi = None
            nb0 = None
            dirs = []
            bvalues = []
            line = 0
            while 'PVM_NRepetitions' not in lines[line]:
                line += 1
            nRep = int(re.search(r'\d+', lines[line]).group())
            while 'PVM_DwNDiffDir' not in lines[line]:
                line += 1
            nDir = int(re.search(r'\d+', lines[line]).group())

            while 'PVM_DwNDiffExpEach' not in lines[line]:
                line += 1
            nDwi = int(re.search(r'\d+', lines[line]).group())

            while 'PVM_DwAoImages' not in lines[line]:
                line += 1
            nb0 = int(re.search(r'\d+', lines[line]).group())

            while 'PVM_DwDir' not in lines[line]:
                line += 1
            while len(dirs) < 3*nDir:
                line += 1
                dirs.extend([float(x) for x in 
                            re.findall(r"[-+]?\d*\.\d+|\d+",
                                        lines[line])])
            dirs = np.array(dirs).reshape((3, nDir)).T
            dirs = np.repeat(dirs, nDwi, axis=0)
            dirs = np.vstack((np.zeros((nb0, 3)), dirs))

            while 'PVM_DwEffBval' not in lines[line]:
                line += 1
            while len(bvalues) < nb0+nDwi*nDir:
                line += 1
                bvalues.extend([int(float(x)) for x in 
                                re.findall(r"[-+]?\d*\.\d+|\d+", 
                                        lines[line])])

            bvalues = np.array(bvalues)
            #bvalues = np.hstack((np.zeros(nb0), np.tile(bvalues, nDir)))

            # Swap X and Y columns and flip Y
            dirs[:, [0, 1]] = dirs[:, [1, 0]]
            dirs[:, 1] = -dirs[:, 1]
            scheme = np.column_stack((dirs, bvalues))
            scheme = np.tile(scheme, (nRep, 1))

            #Find the STEJSKALTANNER bvec and bval files
            methodPath = os.path.join(dataPath, 'method')
            with open(methodPath, 'r') as fid:
                lines = fid.readlines()
            nRep = None
            nDir = None
            nDwi = None
            nb0 = None
            G = []

            line = 0
            while 'PVM_EchoTime' not in lines[line]:
                line += 1
            TE = float(re.search(r'\d+', lines[line]).group())
            while 'PVM_NRepetitions' not in lines[line]:
                line += 1   
            nRep = int(re.search(r'\d+', lines[line]).group())
            while 'PVM_DwGradDur' not in lines[line]:
                line += 1
            delta = float(re.search(r'\d+', lines[line]).group())
            while 'PVM_DwGradSep' not in lines[line]:
                line += 1
            Delta = float(re.search(r'\d+', lines[line]).group())
            while 'PVM_DwNDiffDir' not in lines[line]:
                line += 1
            nDir = int(re.search(r'\d+', lines[line]).group())
            while 'PVM_DwNDiffExpEach' not in lines[line]:
                line += 1
            nDwi = int(re.search(r'\d+', lines[line]).group())
            while 'PVM_DwAoImages' not in lines[line]:
                line += 1
            nb0 = int(re.search(r'\d+', lines[line]).group())
            while 'PVM_DwGradVec' not in lines[line]:
                line += 1
            while len(G) < 3*(nb0+nDwi*nDir):
                line += 1
                G.extend([float(x) for x in re.findall(r"[-+]?\d*\.\d+|\d+",
                                                        lines[line])])
            
            Delta = np.hstack((np.zeros(nb0), np.ones(nDwi*nDir)*Delta))
            delta = np.hstack((np.zeros(nb0), np.ones(nDwi*nDir)*delta))
            G = np.array(G).reshape((nb0+nDwi*nDir, 3))
            G_mag = np.sqrt(np.sum(G**2, axis=1))
            dirs = G / (np.expand_dims(G_mag, axis=1) + np.finfo(float).eps)
            G_mag = G_mag * 0.6648565234445639
            
            
                    
            #Find information about the sequence
            nAve = int(ds["NumberOfAverages"].value)
            TE = float(ds["EchoTime"].value)
            TR = float(ds["RepetitionTime"].value)
            flipAngle = float(ds["FlipAngle"].value)
            date = ds["AcquisitionDate"].value
            voxelSize = [float(ds["PixelSpacing"].value[0]), 
                        float(ds["PixelSpacing"].value[1]),
                        float(ds["SliceThickness"].value)]
            
            with open(dataPath + '/method', 'r') as parsFile:
                lines = parsFile.readlines()
            #Turn lines int a signle string 
            parsString = str(lines)
            #Strip all ' and '' from string
            parsString = parsString.replace("'", "")
            parsString = parsString.replace('"', '')
            #Remove commas too
            parsString = parsString.replace(',', '')

            '''-----------------------extract data-----------------------'''
            #Delta and delta variable names
            deltaName = 'PVM_DwGradDur'
            DeltaName = 'PVM_DwGradSep'

            #Find deltaName in string
            deltaSplit = parsString.split('PVM_DwGradDur')
            #Split again to isolate value
            deltaSplit2 = deltaSplit[1].split('\\n')
            #Extract value
            delta = float(deltaSplit2[1])

            #Find DeltaName in string
            DeltaSplit = parsString.split('PVM_DwGradSep')
            #Split again to isolate value
            DeltaSplit2 = DeltaSplit[1].split('\\n')
            #Extract value
            Delta = float(DeltaSplit2[1])

            #Calculate the time between the first and last image
            # List all files in dicomFolderRecon, excluding files that start with '._'
            valid_images = [file for file in os.listdir(dicomFolderRecon) if not file.startswith('._')]

            # Ensure we found valid image files
            if not valid_images:
                raise FileNotFoundError("No valid image files found in the directory!")

            # Get the first and last image
            firstImage = valid_images[0]
            lastImage = valid_images[-1]

            #Find the first and last image
            #firstImage = os.listdir(dicomFolderRecon)[0]
            #lastImage = os.listdir(dicomFolderRecon)[-1]
            # remove ._ from header 

           
            print(firstImage, lastImage)

            print('path is' , dicomFolderRecon + "/" + firstImage) 
             # Check the file path

            print('path is' , dicomFolderRecon + "/" + lastImage) 
            
            #Load the first and last image headers
            firstImage = pydicom.dcmread(dicomFolderRecon + "/" + firstImage)
            lastImage = pydicom.dcmread(dicomFolderRecon + "/" + lastImage)
            
            #Find the time between the first and last image
            acqTime = float(lastImage.timestamp) - float(firstImage.timestamp)

            dataList.append([date, ENum, count, nAve, TE, TR, 
                            flipAngle,  voxelSize, acqTime, bvalue, nDir, 
                            nDwi, nb0, delta, Delta, np.mean(np.nonzero(G_mag))])  
            count += 1
              
    #Save the data to a xlsx file
    dataList = pd.DataFrame(dataList, columns = dataListTitle)
    savePath = ('C:/Users/vitto/OneDrive - Danmarks Tekniske Universitet/A_Master_Thesis/dataAndCode/sub-' + 
                subjectID + '/sequenceData_ses-' + session + '.xlsx')
    

    #savePath = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' + 
       #         subjectID + '/sequenceData_ses-' + session + '.xlsx')
    dataList.to_excel(savePath, index = False)

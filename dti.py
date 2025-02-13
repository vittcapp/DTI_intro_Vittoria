'''-----------------------------------------------------------------------------
DTI analysis function

Author: Emma Thomson 
Institution: Danish Research Centre for Magnetic Resonance
Date: May 2024
Email: emmat@drcmr.dk

#NOTE: Before running this file, run the sortDataBIDS.py file to sort the data 
       into the appropriate format 

-----------------------------------------------------------------------------'''

def dti(subject, session, EDTI):
        import os
        import numpy as np
        import nibabel as nib
        import pandas as pd
        import matplotlib.pyplot as plt
        from dipy.reconst.dti import fractional_anisotropy

        processedFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' +
                str(subject) + '/ses-' + str(session) + '/fitting/')
        
        if not os.path.exists(processedFolder):
                os.system('mkdir ' + processedFolder)
          
        '''---------------------------chose scans--------------------------------'''

        #Folder with split scans
        alignedFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' +
                str(subject) + '/ses-' + str(session) + '/processed/aligned/')
        
        normalisedFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' +
                str(subject) + '/ses-' + str(session) + '/processed/normalised/')
        
        splitFolder = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' +
                str(subject) + '/ses-' + str(session) + '/processed/split/')
        
        #Read in info file
        infoPath = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' +
                str(subject) + '/sequenceData_ses-' + str(session) + '_splitData.xlsx')
        
        info = pd.read_excel(infoPath)
    
        maskPath = ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' +
                str(subject) + '/ses-' + str(session) + '/mask/mask.nii.gz')
        
        for ii in range(len(EDTI)):
                runNum = EDTI[ii]

                processedFolder =  ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' +
                str(subject) + '/ses-' + str(session) + '/fitting/dti_run-0' + str(runNum) + '/')

                if not os.path.exists(processedFolder):
                        os.system('mkdir ' + processedFolder)

                outputFile = processedFolder + 'dti.nii.gz'

                scan = [ff for ff in os.listdir(normalisedFolder) if 'run-0' + str(runNum) in ff]
                scan = [ff for ff in scan if '.nii' in ff]


                try:
                        scanPath = normalisedFolder + scan[1]
                except: 
                        scanPath = normalisedFolder + scan[0]
                bvecPath = alignedFolder + scan[0][:-15] + '_regrid_registered.bvec' #[:-24]
                bvalPath = splitFolder +  scan[0][:-15] + '_denoised_degibbs.bval' #[:-35]

                #Load the bvector file
                bvector = np.loadtxt(bvecPath)

                #Save bvector file
                BvectorFile = outputFile[:-10] + 'dti_bvector.txt'
                np.savetxt(BvectorFile, bvector)

                #Perform DTI analysis
                command = ('dwi2tensor ' + scanPath + ' ' + outputFile + 
                                ' -force -fslgrad ' +  BvectorFile + ' ' + bvalPath)
                os.system(command)

                #Create FA and MD maps
                command = ('tensor2metric ' + outputFile + ' -force -vec  ' + 
                        outputFile[:-10] + 'fa.nii.gz -adc ' + outputFile[:-10]+ 
                                'md.nii.gz -ad  '+ outputFile[:-10] + 'ad.nii.gz -rd '
                                + outputFile[:-10] + 'rd.nii.gz' )
                os.system(command)

                #Load all outputs and mask 
                dti = nib.load(outputFile).get_fdata()
                fa = nib.load(outputFile[:-10] + 'fa.nii.gz').get_fdata()
                md = nib.load(outputFile[:-10] + 'md.nii.gz').get_fdata()
                ad = nib.load(outputFile[:-10] + 'ad.nii.gz').get_fdata()
                rd = nib.load(outputFile[:-10] + 'rd.nii.gz').get_fdata()
                mask = nib.load(maskPath).get_fdata()
                
                #Mask the data
                dti = dti * np.tile(np.expand_dims(mask, axis=3), (1,1,1,np.shape(dti)[3]))
                fa = fa * np.tile(np.expand_dims(mask, axis=3), (1,1,1,np.shape(fa)[3]))
                md = md * mask
                ad = ad * mask
                rd = rd * mask

                #Save the data
                dti = nib.Nifti1Image(dti, np.eye(4))
                fa = nib.Nifti1Image(fa, np.eye(4))
                md = nib.Nifti1Image(md, np.eye(4))
                ad = nib.Nifti1Image(ad, np.eye(4))
                rd = nib.Nifti1Image(rd, np.eye(4))

                nib.save(dti, outputFile)
                nib.save(fa, outputFile[:-10] + 'fa_masked.nii.gz')
                nib.save(md, outputFile[:-10] + 'md_masked.nii.gz')
                nib.save(ad, outputFile[:-10] + 'ad_masked.nii.gz')
                nib.save(rd, outputFile[:-10] + 'rd_masked.nii.gz')
                
'''-----------------------------------------------------------------------------
DKI analysis function

Author: Emma Thomson 
Institution: Danish Research Centre for Magnetic Resonance
Date: May 2024
Email: emmat@drcmr.dk

#NOTE: Before running this file, run the sortDataBIDS.py file to sort the data 
       into the appropriate format 

-----------------------------------------------------------------------------'''

def dki(subject, session, EDKI):
        import os
        import numpy as np
        import nibabel as nib
        import pandas as pd
        import matplotlib.pyplot as plt
        from dipy.reconst.dti import fractional_anisotropy
        import dipy.reconst.dki as dki
        from dipy.core.gradients import gradient_table
        from dipy.io.gradients import read_bvals_bvecs

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
        
        for ii in range(len(EDKI)):
                runNum = EDKI[ii]

                processedFolder =  ('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-' +
                str(subject) + '/ses-' + str(session) + '/fitting/dki_run-0' + str(runNum) + '/')

                if not os.path.exists(processedFolder):
                        os.system('mkdir ' + processedFolder)

                outputFile = processedFolder + 'dki.nii.gz'

                scan = [ff for ff in os.listdir(normalisedFolder) if 'run-0' + str(runNum) in ff]
                scan = [ff for ff in scan if '.nii' in ff]

                #Hold data 
                scanPathB = normalisedFolder + scan[0]
                scanImgB = nib.load(scanPathB).get_fdata()

                #Strip the 'b0s' from the file
                strippedScanImgB = scanImgB[:,:,:,int(info[info['Run Number'] == runNum]['nb0'].iloc[0]):]

                #Replace the 'b' with 'a'
                scanPathA = scanPathB.replace('b_dwi', 'a_dwi')
                scanImgA = nib.load(scanPathA).get_fdata()

                #Hold the data
                scanImg = np.concatenate((scanImgA, strippedScanImgB), axis=3)

                #Save the data
                scanImg = nib.Nifti1Image(scanImg, np.eye(4))
                scanDKI = processedFolder + 'dkiScan.nii.gz'
                nib.save(scanImg, scanDKI)

                bvecPathA = alignedFolder + scan[0][:-15] + '_regrid_registered.bvec' #[:-18]
                #Load the bvector file
                bvectorA = np.loadtxt(bvecPathA)

                bvecPathB = bvecPathA.replace('b_dwi', 'a_dwi')
                bvectorB = np.loadtxt(bvecPathB)

                #Remove the first nb0 b vectors
                bvectorB = bvectorB[:,int(info[info['Run Number'] == runNum]['nb0'].iloc[0]):]

                #Combine the bvector files
                bvector = np.concatenate((bvectorA, bvectorB), axis=1)
                bvector = bvector

                #Save bvector file
                BvectorDKI = outputFile[:-10] + 'dki_bvector.txt'
                np.savetxt(BvectorDKI, bvector.T)

                bvalPathB = splitFolder +  scan[0][:-15] + '_denoised_degibbs.bval' #[:-35]
                bvalPathA = bvalPathB.replace('b_dwi', 'a_dwi')

                #Load the bvalue files
                bvalsA = np.loadtxt(bvalPathA)
                bvalsB = np.loadtxt(bvalPathB)

                #Remove the first nb0 b values
                bvalsB = bvalsB[int(info[info['Run Number'] == runNum]['nb0'].iloc[0]):]

                #Combine the bvalue files
                bvals = np.concatenate((bvalsA, bvalsB))

                #Save bvalue file
                BvalDKI = outputFile[:-10] + 'dki.bval'
                np.savetxt(BvalDKI, bvals)

                #Perform DKI analysis
                #Load the data
                data = nib.load(scanDKI).get_fdata()
                gtab = gradient_table(bvals, bvector)

                #Fit the data
                dkimodel = dki.DiffusionKurtosisModel(gtab)
                dkifit = dkimodel.fit(data)

                MK = dkifit.mk(0, 3)
                AK = dkifit.ak(0, 3)
                RK = dkifit.rk(0, 3)
                KFA = dkifit.kfa

                #Save the data
                MKImg = nib.Nifti1Image(MK, np.eye(4))
                AKImg = nib.Nifti1Image(AK, np.eye(4))
                RKImg = nib.Nifti1Image(RK, np.eye(4))
                KFAImg = nib.Nifti1Image(KFA, np.eye(4))

                nib.save(MKImg, outputFile[:-10] + 'MK.nii.gz')
                nib.save(AKImg, outputFile[:-10] + 'AK.nii.gz')
                nib.save(RKImg, outputFile[:-10] + 'RK.nii.gz')
                nib.save(KFAImg, outputFile[:-10] + 'KFA.nii.gz')

                '''
                #Perform DTI analysis
                command = ('dwi2tensor ' + scanDKI + ' ' + outputFile +
                                ' -force -fslgrad ' +  BvectorDKI + ' ' + BvalDKI + ' -dkt ' +  outputFile)
                os.system(command)

                #Create kurtosis maps
                command = ('tensor2metric ' + outputFile + ' -force -mk  ' + 
                        outputFile[:-10] + 'mk.nii.gz -ak ' + outputFile[:-10] +
                        'ak.nii.gz -rk  '+ outputFile[:-10] + 'rk.nii.gz -dkt ' +
                        outputFile[:-10] + 'dkt.nii.gz')
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
                '''
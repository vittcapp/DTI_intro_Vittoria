def noddi(dwiFolder, fileBase, processedFolder, maskFolder, DeltaSec, deltaSec, applyDenoise):
       
       ## Will not work on local computer - must be performed on cluster 
       
       import os
       import numpy as np
       import mdt
       #Create NODDI output folder
       outputFolder = processedFolder + 'NODDI/'
       if not os.path.exists(outputFolder):
              os.makedirs(outputFolder)

       #Perform NODDI analysis
       
       #Isolate bvector and bval files
       bvectorfile = dwiFolder + fileBase + '_DWI_bvector.txt'
       bvalfile = dwiFolder + fileBase + '_DWI.bval'

       #Name protocol file
       protocolFile = outputFolder + fileBase + '_bvals.prtcl'

       #Name dwi file
       if applyDenoise is True:
              dwiFile = dwiFolder + fileBase + '_dwi_denoised_degibbs.nii.gz'
       else:
              dwiFile = dwiFolder + fileBase + '_DWI.nii'

       #Name mask file
       maskFile = maskFolder + fileBase + '_mask.nii.gz'

       #Create protocol file
       protocol = mdt.create_protocol(bvecs=bvectorfile, bvals=bvalfile, out_file=protocolFile,
                     Delta=DeltaSec, delta=deltaSec) #, TE=60e-3, TR=7.1)
       
       #Load input data
       input_data = mdt.load_input_data(dwiFile, protocolFile, maskFile)

       #Output file
       output_file = outputFolder + fileBase + '_NODDI.nii.gz'

       mdt.fit_model('NODDI', input_data, output_file,  use_cascaded_inits=False)

       #inits = mdt.get_optimization_inits('NODDI', input_data, 'output')

       #mdt.fit_model('NODDI', input_data, 'output', use_cascaded_inits=False, initialization_data={'inits': inits})
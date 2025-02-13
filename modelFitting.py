'''-----------------------------------------------------------------------------
Author: Emma Thomson 
Institution: Danish Research Centre for Magnetic Resonance
Date: October 2024
Email: emmat@drcmr.dk

The steps performed in this pipeline are as follows:


MODEL FITTING:

1. Fit T2 map 
2. Fit DTI parameters
3. Fit DKI parameters
4. Fit SANDI parameters

NOTES: 
DTI and DKI are performed on each scan specified in the EDTI and EDKI lists separately.
SANDI is performed on each scan specified in the ESANDI list together.
    To perform multiple SANDI fits run this code multiple times with different ESANDI lists.

DEBUG HINTS:
- Need to manually unzip the mask file before SANDI fitting - automate this

-----------------------------------------------------------------------------'''

'''-----------------------------packages-------------------------------------'''
import numpy as np
import nibabel as nib
import pandas as pd
import os
import sys

'''-----------------------------functions------------------------------------'''
# Add the directory containing the 'functions' folder to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from functions.dti import dti
from functions.sandi import sandi
from functions.dki import dki
from functions.t2fitting import t2fitting

'''--------------------------------switches----------------------------------'''

#For test purposes you can switch off any part of the pipeline but it is not 
#compatible unless these steps have been run previously.
fitT2Switch = False; fitDKISwitch = False; fitDTISwitch = True; fitSANDISwitch = False; 

'''--------------------------------user inputs-------------------------------'''
#Folder name 
folder = 'M1457'

#Subject name 
subject = '22.2.24M'
session = '3'

#For each fitting type you must input the scan numbers for the scans you want to
#fit. If you want to fit multiple scans then you must input them as a list.
#This includes the alphabetical letter at the end of the scan number.

#T2 fitting
ET2 = ['1a']

#DTI fitting
EDTI = ['1a']

#DKI fitting
EDKI = ['1b']

#SANDI fitting
ESANDI = ['1a', '1b', '1c']
#Fitting with the powder average or the variance images
type = 'average' #'average' or 'variance'

'''-----------------------------8. Fit T2 map---------------------------------'''

if fitT2Switch:
    #Fit the T2 map

    t2fitting(subject, session, ET2)

    print(' ---> Fitting T2 map complete')

'''-----------------------------9. Fit DTI parameters-------------------------'''

if fitDTISwitch:
    #Fit the DTI parameters

    dti(subject, session, EDTI)

    print(' ---> Fitting DTI parameters complete')

'''-----------------------------10. Fit DKI parameters-------------------------'''

if fitDKISwitch:
    #Fit the DKI parameters

    dki(subject, session, EDKI)

    print(' ---> Fitting DKI parameters complete')

'''-----------------------------11. Fit SANDI parameters----------------------'''

if fitSANDISwitch:
    #Fit the SANDI parameters

    sandi(subject, session, ESANDI, type)

    print(' ---> Fitting SANDI parameters complete')


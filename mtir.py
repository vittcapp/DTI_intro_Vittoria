'''-----------------------------------------------------------------------------
Function for running MTIR processing (using REMMI toolbox and MATLAB)

https://github.com/remmi-toolbox/remmi-matlab

Author: Emma Thomson 
Institution: Danish Research Centre for Magnetic Resonance
Date: June 2024
Email: emmat@drcmr.dk

#NOTE: Before running this file, run the sortDataBIDS.py file to sort the data 
       into the appropriate format 

-----------------------------------------------------------------------------'''

def mtir(collected_data, processedFolder):

    '''-----------------------------packages--------------------------------'''
    import os
    import pandas as pd

    '''--------------------------find folders--------------------------------'''
    session = collected_data['session']
    subject = collected_data['subject']

    #Load the session information
    sessionInfo = '/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub_' + subject 
    infoSheet = sessionInfo + '/ses_' + session + '_info.xlsx'

    #Load the data
    info = pd.read_excel(infoSheet)

    #Find the date 
    date = info['Date'][1]

    f =gg

    '''---------------------------Run MTIR processing----------------------------'''

    commandString = ('cd /Dropbox/Work/Coding/MRprocessing/functions && matlab -nosplash -nodisplay -nodesktop -r mtir( '
                      + rawFolder + ',' + outputFolder + ' )' )
    os.system(commandString)


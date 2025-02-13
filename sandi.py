def sandi(subject, session, ESANDI, type):


        import os 

        if type == 'average':
                snr = 5
        elif type == 'variance':
                snr = 10

        '''-------------------------run command-----------------------------'''

        # Convert ESANDI list to a MATLAB-style cell array string
        ESANDI_str = "{" + ",".join(["'" + str(item) + "'" for item in ESANDI]) + "}"

        # Create the full command string
        commandString = ('/Applications/MATLAB_R2023a.app/bin/matlab -r "addpath('"'functions'"'); sandi(' 
                         + "'" + str(subject) + "'" + ' , ' + str(session) + ' , ' + ESANDI_str + 
                         ' , ' + "'" + type + "'" + ' , ' + str(snr) + ' ); exit"')
        os.system(commandString)
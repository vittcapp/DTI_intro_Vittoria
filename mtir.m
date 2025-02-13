def mtir(outerFolder, outputFolder)

    %Add the REMMI toolbox to path 
    addpath('/Users/emmathomson/Dropbox/Work/Coding/toolboxes/REMMItoolbox/');

    %% Loading data and data sorting

    %Step into the next folder 
    studyPath = strcat(outerFolder, '/dicomData');
    % List the study path and experiments to process
    info.spath = studyPath;
    info.exps = eNumber;

    %If the output folder does not exist then 
    if ~exist(outputFolder, 'dir')
        mkdir(outputFolder)
    end
    ws = remmi.workspace(strcat(outputFolder, 'MTIR.mat'));

    % perform mtir analysis
    ws.mtir = remmi.ir.qmt(info);
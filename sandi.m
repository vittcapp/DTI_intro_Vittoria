% Main script to perform the SANDI analysis (on one or more datasets) using machine learning, as in Palombo M. et al. Neuroimage 2020: https://doi.org/10.1016/j.neuroimage.2020.116835
% Modified to allow for variable diffusion time scans - requires fixed
% gradient strength 

% Author:
% Dr. Marco Palombo
% Cardiff University Brain Research Imaging Centre (CUBRIC)
% Cardiff University, UK
% 8th December 2021
% Email: palombom@cardiff.ac.uk
%
% Modified by:
% Emma Thomson
% Danish Research Centre for Magnetic Resonance 
% July 2024 
% Email: emmat@drcmr.dk

function out = sandi(subject, session, ENums, type, snr)
    %% User inputs 

    SNR = snr; % Average signal-to-noise ratio (SNR) of an individual b=0 image for the whole brain
    
    Dsoma =  2; % in micrometers^2/ms, e.g. 2
    Din_UB = 3; % in micrometers^2/ms, e.g. 3
    Rsoma_UB = 12 ; % in micrometers, e.g. 12
    De_UB = 4; % in micrometers^2/ms, e.g. 3
    seed_rng = 1; % for reproducibility
    MLmodel = 'MLP'; % can be 'RF' for Random Forest (default); 'MLP' for multi-layer perceptron; 'GRNN' for Generalized Regression NEural Network
    tau = 1e-4;
    
    %% Add the path to main and support functions used for SANDI analysis
    
    addpath(genpath(fullfile(['/Users/emmathomson/Dropbox/Work/Coding/' ...
        'toolboxes/SANDItoolboxET/SANDI-Matlab-Toolbox-v1.0/functions'])));
    addpath(genpath(fullfile(pwd, 'functions')));
    
    % output folder where the SANDI fit results for each subject will be stored
    outputFolder = strcat('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-', ...
        subject, '/ses-', string(session), '/fitting/') ; 
    
    if ~exist("outputFolder","dir")
        mkdir(outputFolder);
    end

     % output folder where the SANDI fit results for each subject will be stored
    outputFolder = strcat('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-', ...
        subject, '/ses-', string(session), '/fitting/sandi_', strjoin(ENums, '')) ; 
    
    if ~exist("outputFolder","dir")
        mkdir(outputFolder);
    end 
    
    maskFolder = strcat('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-',  ...
        subject, '/ses-', string(session), '/mask/mask.nii.gz');
    
    dataFolder = strcat('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-',  ...
        subject, '/ses-', string(session), '/processed/powder/');

    bvalFolder = strcat('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-',  ...
        subject, '/ses-', string(session), '/processed/split/');
    
    fileBase = strcat('sub-', subject, '_ses-', string(session), '_run-0');

    %% Create data array 
    
    %b-value images
    for ii = 1:length(ENums)
    
        EN = ENums(ii);
    
        dataHold = niftiread(strcat(dataFolder, fileBase, string(EN), '_', type,'.nii')); 
        dataHold = dataHold./(max(max(max(dataHold))));

        data(:,:,:,:,ii) = dataHold;
    
    end 
    
    %saveData
    imgDataFolder = strcat(outputFolder, '/sandiData.nii');
    niftiwrite(data, imgDataFolder);

    %% Isolate the td, G, TE and b-values
    
    scans = readtable(strcat('/Users/emmathomson/Dropbox/Work/Scanning/MRdata/sub-', ...
        subject, '/sequenceData_ses-',string(session), '_splitData.xlsx'));
    
    % gradient = zeros(size(,4));
    % td = zeros(1,size(data,4));
    % TE = zeros(1,size(data,4));
    % bval = zeros(1,size(data,4));

     rowIdx = find(strcmp(scans{:, 'RunNumber'}, ENums(1)));   
     smalldelta = scans{rowIdx, 'delta_ms_'};
    
    for ii = 1:length(ENums)

     EHold = ENums(ii);

     rowIdx = find(strcmp(scans{:, 'RunNumber'}, EHold));   

     % Fill the data for the b0 images too 
     gradient(ii)= scans{rowIdx, 'G_mag_mT_mm_'};
     td(ii)= scans{rowIdx, 'Delta_ms_'};
     TE(ii)= scans{rowIdx, 'TE_ms_'};
     bval(ii)= str2double(scans{rowIdx, 'bvalue_s_mm2_'});
    
    end 
    
    %% Sort data 
    
    sortNum = (gradient.^2).*(td-smalldelta/3) + TE;
    
    [~, sortedIndices] = sort(sortNum);
    bval = bval(sortedIndices);
    gradient = gradient(sortedIndices);
    td = td(sortedIndices);
    TE = TE(sortedIndices);
    
    data = data(:,:,:,sortedIndices);
    
    %% Create schemefile 
    
    %Add fixed gradient instead of fixed delta, ET, 11/07/24
    protocol = make_protocol(bval./1E3, gradient, smalldelta, td, TE);
    schemefile = fullfile(outputFolder, 'diravg.scheme');
    ProtocolToScheme(protocol, schemefile, tau)
    
    %%  Train model 
    
    % Train the ML model
    schemefile = fullfile(outputFolder, 'diravg.scheme');
    [Mdl, train_perf] = setup_and_run_model_training(schemefile, SNR, outputFolder, Dsoma, Din_UB, Rsoma_UB, De_UB, seed_rng, MLmodel); % Funciton that train the ML model. For options 'RF' and 'MLP', the training performance (mean squared error as a function of #trees or training epochs, respectively) are also saved in 'train_perf'
    
    %% SANDI fit
    maskData = niftiread(maskFolder);
    
    schemefile = fullfile (outputFolder,'diravg.scheme'); % corresponding acquisition scheme
    run_model_fitting(imgDataFolder, maskFolder, schemefile,outputFolder, Mdl, MLmodel);

# name and type of the submission
cfg_name = "electron_E100GeV_z_NANO"
cfg_type = "cmsRun"

# run and storage directories
cfg_run_dir = "/afs/cern.ch/work/j/jaeyserm/HGCAL/CMSSW_11_3_0_pre1/src/HGCAL/HGProducer/runs/%s" % cfg_name
cfg_storage_dir = "/eos/user/j/jaeyserm/HGCAL/HGSamples/%s/" % cfg_name

# output ROOT filenames
cfg_output_name = "NANO" 

# input config file for nano producer
cfg_input_file = "test/ConfFile_fig.py" 

# input dataset conditions: input config file and the name of the output ROOT file which is served as input
cfg_input_dataset_file = "/afs/cern.ch/work/j/jaeyserm/HGCAL/CMSSW_11_3_0_pre1/src/HGCAL/HGProducer/input/electron_E100GeV_z.py"
cfg_input_dataset_name = "RECO" # e.g. RECO or RECO_inMINIAODSIM


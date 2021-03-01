
# RECO
step3 = "step3 --conditions auto:phase2_realistic_T21 --era Phase2C11 --eventcontent FEVTDEBUGHLT,MINIAODSIM -s RAW2DIGI,L1Reco,RECO,RECOSIM,PAT --datatier GEN-SIM-RECO,MINIAODSIM --geometry Extended2026D71"



### define configuration

# name of the submission
cfg_name = "electron_E100GeV_z_RECO"

# type: cmsDriver or cmsRun
cfg_type = "cmsDriver"

# full path for run dir, where job submission takes place (will be automatically created)
cfg_run_dir = "/afs/cern.ch/work/j/jaeyserm/HGCAL/CMSSW_11_3_0_pre1/src/HGCAL/HGProducer/runs/%s" % cfg_name

# full path for storage dir (will be automatically created)
cfg_storage_dir = "/eos/user/j/jaeyserm/HGCAL/HGSamples/%s/" % cfg_name

# definition of commands: provide name and command in list
cfg_cmsdriver_command_names = ["RECO"]
cfg_cmsdriver_commands = [step3]

# input dataset conditions: input config file and the name of the output ROOT file which is served as input
cfg_input_dataset_file = "/afs/cern.ch/work/j/jaeyserm/HGCAL/CMSSW_11_3_0_pre1/src/HGCAL/HGProducer/input/electron_E100GeV_z.py"
cfg_input_dataset_name = "DIGI"


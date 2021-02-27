
# GEN-SIM
step1 = "electron_E35GeV_z_cfi --conditions auto:phase2_realistic_T21 --era Phase2C11 --eventcontent FEVTDEBUG -s GEN,SIM --datatier GEN-SIM --beamspot HLLHC14TeV --geometry Extended2026D71"

# DIGI
step2 = "step2 --conditions auto:phase2_realistic_T21 -s DIGI:pdigi_valid,L1,L1TrackTrigger,DIGI2RAW,HLT:@fake2 --datatier GEN-SIM-DIGI-RAW --geometry Extended2026D71 --era Phase2C11 --eventcontent FEVTDEBUGHLT"

# RECO
step3 = "step3 --conditions auto:phase2_realistic_T21 --era Phase2C11 --eventcontent FEVTDEBUGHLT,MINIAODSIM -s RAW2DIGI,L1Reco,RECO,RECOSIM,PAT --datatier GEN-SIM-RECO,MINIAODSIM --geometry Extended2026D71"



### define configuration

# name of the submission
cfg_name = "electron_E35GeV_z_test"

# type: cmsDriver or cmsRun
cfg_type = "cmsDriver"

# number of events and jobs
cfg_nevents = 1000
cfg_njobs = 10

# full path for run dir (where job submission takes place), will be automatically created
cfg_run_dir = "/afs/cern.ch/work/j/jaeyserm/HGCAL/CMSSW_11_3_0_pre1/src/HGCAL/HGProducer/runs/%s" % cfg_name

# full path for storage dir, will be automatically created
cfg_storage_dir = "/eos/user/j/jaeyserm/HGCAL/HGSamples/%s/" % cfg_name

# definition of commands: provide name and command in list
cfg_command_names = ["GEN-SIM", "DIGI", "RECO"]
cfg_commands = [step1, step2, step3]

# input conditions. Leave empty if GEN step in command list
cfg_input_file = "" # only provide input if the first command does not contain a GEN step
cfg_input_name = ""


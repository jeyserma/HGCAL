#!/usr/bin/env python

import os, sys, math, datetime, shutil, time, glob, shlex
from optparse import OptionParser
from subprocess import call, check_output

sys.dont_write_bytecode = True

parser = OptionParser()
parser.add_option("-i", "--ifile", dest = "ifile", help = "Input file")
parser.add_option("-f", "--jobflavor", dest='jobflavor', type='string', help="Job flavor",default="workday")

parser.add_option("", "--dryrun", dest = "dryrun", action = 'store_true', help = "Dry run", default = False)
parser.add_option("", "--submit", dest = "submit", action = 'store_true', help = "Submit", default = False)
parser.add_option("", "--resubmit", dest = "resubmit", action = 'store_true', help = "Resubmit failed/missing ones", default = False)
parser.add_option("", "--status", dest = "status", action = 'store_true', help = "Status", default = False)
parser.add_option("", "--jobids", dest='jobids', type='string', help="Job ids to resubmit")

(opts,args) = parser.parse_args()



'''
espresso     = 20 minutes
microcentury = 1 hour
longlunch    = 2 hours
workday      = 8 hours
tomorrow     = 1 day
testmatch    = 3 days
nextweek     = 1 week
'''


def printColor(t, col):

    class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKCYAN = '\033[96m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
    
    print(getattr(bcolors, col) + t + bcolors.ENDC)
    
    
def printLine(list):
    ''' convert list in list of int number, sort and compress consecutive numbers. Then print the result:
    4,5,8,3 -> 3-5,8
    '''
    nums = [ int(s) for s in list ]
    nums.sort()
    compress = []
    last = None
    blockinit = None

    for n in nums:
        #first if it is not consecutive
        if last == None: ## INIT
            blockinit = n

        elif last != n-1:
            #close a block and open a new one
            if last != blockinit:
                compress.append( str(blockinit) + "-" + str(last) ) 
            else:
                compress.append( str(last) ) 
            blockinit = n

        last = n

    #consider also the last number
    #close a block and open a new one
    if last != blockinit:
        compress.append( str(blockinit) + "-" + str(last) ) 
    else:
        compress.append( str(last) ) 

    return ",".join(compress)
    

def submit():

    printColor("Prepare submission", "OKBLUE")
    
    

    if os.path.exists(cfg_submission_dir): raise Exception("Submission directory %s exists. Please remove or change submission name" % cfg_submission_dir)
    if os.path.isdir(cfg_storage_dir): raise Exception("Storage directory %s exists. Please remove or change submission name" % cfg_storage_dir)
    
    os.makedirs(cfg_submission_dir)
    os.makedirs(cfg_storage_dir)

    nevents = int(1.*cfg_nevents / cfg_njobs) # events per job


    print("Generate %d condor jobs" % cfg_njobs)
    for i in range(0, cfg_njobs):

        rundir_ = "%s/%04d" % (cfg_submission_dir, i)
        os.makedirs(rundir_)
        
        istring = "%04d" % i
        filename = "%s/submit_%s" % (rundir_, istring) # store all files to run the job in the run directory

        print(" > submit %s" % istring)
        
        bashFile = "%s.sh" % filename
        
        with open(bashFile, 'w') as fout:

            fout.write("#!/bin/sh\n")
            fout.write("# auto generated at %s\n" % datetime.datetime.now())
            fout.write('cd %s\n' % rundir_)
            #fout.write('pwd\n')
            fout.write('eval `scramv1 runtime -sh`\n') # cmsenv
            fout.write('LD_LIBRARY_PATH=%s:$LD_LIBRARY_PATH\n' % os.getcwd())
            
            fout.write('date > ' + filename + '.run\n') # temporary make .run file
            fout.write('SEED=$(($(date +%s%3N) % 10000 + 1 ))\n') # set random seed based on date
            fout.write('echo "Seed: $SEED"\n\n')
            
            fout.write('echo "Execute commands at $(date)"\n')
            
            if cfg_type == "cmsDriver":

                cmds = ""
                for i, cmd in enumerate(cfg_cmsdriver_commands):

                    cmd_cmdDriver = "cmsDriver.py %s --no_exec --python_filename %s_%s.py --fileout %s/%s_%s.root -n %d" % (cmd, istring, cfg_cmsdriver_command_names[i], cfg_storage_dir, istring, cfg_cmsdriver_command_names[i], nevents)
                    if i == 0 and not cfg_isGEN: cmd_cmdDriver += " --filein file:%s/%s_%s.root" % (cfg_input_dataset_storage_dir, istring, cfg_input_dataset_name)
                    if i != 0: cmd_cmdDriver += " --filein file:%s/%s_%s.root " % (cfg_storage_dir, istring, cfg_cmsdriver_command_names[i-1])
                   
                    cmd_cmsRun = "cmsRun %s_%s.py" % (istring, cfg_cmsdriver_command_names[i])
                    
                    # append commands to bash file
                    cmds += '%s\n' % cmd_cmdDriver
                    if i == 0 and cfg_isGEN: cmds += "sed -i '/Configuration.StandardSequences.Services_cff/a process.RandomNumberGeneratorService.generator.initialSeed = '\"$SEED\"' ' %s_%s.py\n" % (istring, cfg_cmsdriver_command_names[i]) # change seed
                    cmds += '%s\n\n' % cmd_cmsRun

                fout.write(cmds)    
            
            
            if cfg_type == "cmsRun":

                cfg_input_file_ = "%s/%s" % (rundir_, cfg_input_file.split("/")[-1])
                shutil.copyfile(cfg_input_file, cfg_input_file_)
                    
                fIn_ = "%s/%s_%s.root" % (cfg_input_dataset_storage_dir, istring, cfg_input_dataset_name)
                fOut_ = "%s/%s_%s.root" % (cfg_storage_dir, istring, cfg_output_name)
                    
                call("sed -i -e 's#input.root#%s#g' %s" % (fIn_, cfg_input_file_), shell=True)
                call("sed -i -e 's#output.root#%s#g' %s" % (fOut_, cfg_input_file_), shell=True)

                fout.write('cmsRun %s\n' % cfg_input_file.split("/")[-1])
            
            fout.write('\necho "Finished commands at $(date)"\n')
            
            fout.write('EXITCODE=${PIPESTATUS[0]}\n')
            fout.write('echo $EXITCODE\n')
            fout.write('rm %s.run 2>&1 >/dev/null\n' % filename)
            fout.write('[ $EXITCODE == 0 ] && touch %s.done\n' % filename)
            fout.write('[ $EXITCODE != 0 ] && echo $EXITCODE > %s.fail\n' % filename)
            fout.write('echo "Job finished at $(date)"\n')
            fout.write('echo "EXIT_SUCCESS"\n')

        call(["chmod", "u+x", bashFile]) # chmod .sh file

        condorFile = "%s.sub" % filename
        with open(condorFile, 'w') as fout:
            
            fout.write("executable              = %s.sh\n" % filename)
            fout.write("arguments               = $(ClusterId) $(ProcId)\n")
            fout.write("output                  = %s.out\n" % filename)
            fout.write("error                   = %s.err\n" % filename)
            fout.write("log                     = %s.log\n" % filename)
            #fout.write("getenv                  = True\n") # throws error?
            fout.write("should_transfer_files   = YES\n")
            fout.write("max_retries             = 3\n")
            #fout.write("transfer_input_files    = python,config,bin,interface,src\n") # transfer python dir and contents

                
            fout.write("+JobFlavour = \"%s\"\n" % opts.jobflavor)
            fout.write("queue")
        
        
        # submit it
        cmd = "condor_submit %s >& /dev/null" % (condorFile)
        call(cmd, shell=True)
        

    
def resubmit():

    printColor("Prepare resubmission", "OKBLUE")


    toResubmit = []
    for i in opts.jobids.split(","):
        
        if '-' in i:
            for j in range(int(i.split('-')[0]), int(i.split('-')[1])+1): toResubmit.append(j)
        else: toResubmit.append(int(i))

    for i in toResubmit:
    
        rundir_ = "%s/%04d" % (cfg_submission_dir, i)
        storagedir_ = "%s/%04d" % (cfg_storage_dir, i)
        istring = "%04d" % i
        filename = "%s/submit_%s" % (rundir_, istring)
        #bashFile = "%s.sh" % filename
        condorFile = "%s.sub" % filename
        
        print(" > resubmit %s" % istring)
        
        
        # remove all log/input/ROOT files
        call("rm -f %s.log" % filename, shell=True)
        call("rm -f %s.err" % filename, shell=True)
        call("rm -f %s.fail" % filename, shell=True)
        call("rm -f %s.run" % filename, shell=True)
        call("rm -f %s.done" % filename, shell=True)
        call("rm -f %s.out" % filename, shell=True)
        call("rm -f %s/*%s*.root" % (storagedir_, istring), shell=True)
       
        
        # submit it
        cmd = "condor_submit %s >& /dev/null" % (condorFile)
        call(cmd, shell=True)
        time.sleep(1)


def status():

    printColor("Job status", "OKBLUE")


    jobs = glob.glob("%s/*" % cfg_submission_dir)
    #out = check_output("condor_q -json", shell=True)

    PENDING = []    # store IDs that are still pending
    FAILED = []        # store IDs that failed
    DONE = []        # store IDs that are done
    RUNNING = []    # store IDs that are still running
    UNKNOWN = []
    
    for i,jobdir in enumerate(jobs):
    
        istring = jobdir.split("/")[-1]
        filename = "%s/submit_%s" % (jobdir, istring)
                
        if os.path.isfile("%s.run" % filename): RUNNING.append(i) # run file only exists when running (created and deleted automatically)
        elif not os.path.isfile("%s.out" % filename) and not os.path.isfile("%s.run" % filename): PENDING.append(i) # out file generated when starting?
        elif os.path.isfile("%s.fail" % filename) or 'Begin Fatal Exception' in open("%s.err" % filename).read(): FAILED.append(i) # 
        elif 'EXIT_SUCCESS' in open("%s.out" % filename).read(): DONE.append(i)
        else: UNKNOWN.append(i)

    
    printColor("Pending:       %s" % printLine(PENDING), "OKBLUE")
    printColor("Running:       %s" % printLine(RUNNING), "WARNING") 
    printColor("Done:          %s" % printLine(DONE), "OKGREEN")
    printColor("Failed:        %s" % printLine(FAILED), "FAIL")
    printColor("Unknown:       %s" % printLine(UNKNOWN), "HEADER")


def dryrun():

    printColor("Prepare dryrun", "OKBLUE")
    
    if not os.path.isdir(cfg_run_dir): os.makedirs(cfg_run_dir)

    
    if os.path.isdir(cfg_dryrun_dir):
        
        print(" > dry run directory exists... remove it")
        shutil.rmtree(cfg_dryrun_dir)
        os.makedirs(cfg_dryrun_dir)
    
    else: os.makedirs(cfg_dryrun_dir)

    filename = "%s/%s" % (cfg_dryrun_dir, "dryrun") # store all files to run the job in the run directory
    nevents = 10
    
    
    bashFile = "%s.sh" % filename
    with open(bashFile, 'w') as fout:

        fout.write("#!/bin/sh\n")
        fout.write("# auto generated at %s\n" % datetime.datetime.now())
        fout.write('LD_LIBRARY_PATH=%s:$LD_LIBRARY_PATH\n' % os.getcwd())
        fout.write('eval `scramv1 runtime -sh`\n')
        fout.write('cd %s\n\n' % cfg_dryrun_dir)

        if cfg_type == "cmsDriver":
        
            for i, cmd in enumerate(cfg_cmsdriver_commands):

                print(" > append command %s" % cfg_cmsdriver_command_names[i])
                
                cmd_cmdDriver = "cmsDriver.py %s --no_exec --python_filename %s.py --fileout %s.root -n %d" % (cmd, cfg_cmsdriver_command_names[i], cfg_cmsdriver_command_names[i], nevents)
                if i == 0 and not cfg_isGEN: cmd_cmdDriver += " --filein file:%s " % cfg_dryrun_input_file
                if i != 0: cmd_cmdDriver += " --filein file:%s.root " % cfg_cmsdriver_command_names[i-1]
            
                cmd_cmsRun = "cmsRun %s.py" % cfg_cmsdriver_command_names[i]
            
                # append commands to bash file
                fout.write('echo "Execute commands for %s"\n' % cfg_cmsdriver_command_names[i])
                fout.write('%s\n' % cmd_cmdDriver)
                fout.write('%s\n' % cmd_cmsRun)
                fout.write('\n')
                
        if cfg_type == "cmsRun":
        
            cfg_input_file_ = "%s/%s" % (cfg_dryrun_dir, cfg_input_file.split("/")[-1])
            shutil.copyfile(cfg_input_file, cfg_input_file_)
            
            fIn_ = "%s/dryrun/%s.root" % (cfg_input_dataset_run_dir, cfg_input_dataset_name)
            fOut_ = "%s/%s.root" % (cfg_dryrun_dir, cfg_output_name)
            
            call("sed -i -e 's#input.root#%s#g' %s" % (fIn_, cfg_input_file_), shell=True)
            call("sed -i -e 's#output.root#%s#g' %s" % (fOut_, cfg_input_file_), shell=True)

            
            # append commands to bash file
            fout.write('echo "Execute command"\n')
            fout.write('cmsRun %s\n' % cfg_input_file_)
            fout.write('\n')


    printColor("Execute dryrun", "OKBLUE")
    
    t_start = time.time()
    call(["chmod", "u+x", bashFile]) # chmod .sh file
    call("%s" % bashFile, shell=True)
    t_end = time.time()
    dt = t_end - t_start
    print(" > done! Executed commands for %d events within %.2f seconds (%.3f s/ev)" % (nevents, dt, dt/nevents))


if __name__ == "__main__":

    if not (opts.dryrun or opts.submit or opts.resubmit or opts.status): parser.error('Please provide action (--dryrun, --submit, --resubmit or --status)')

    # check and parse input file
    if opts.ifile is None: parser.error('Please provide input file')
    try:
        
        if not (opts.status or opts.resubmit): printColor("Parse input file", "OKBLUE")
        
        if not os.path.isfile(opts.ifile): raise Exception('Input file %s does not exist' % opts.ifile)

        sys.path.append(os.path.dirname(opts.ifile)) # append directory of input file to syspath
        fin = __import__(os.path.basename(opts.ifile).split(".")[0])
        
        cfg_name = fin.cfg_name
        cfg_type = fin.cfg_type
        
        cfg_run_dir = fin.cfg_run_dir
        cfg_storage_dir = fin.cfg_storage_dir

        if ' ' in cfg_name: raise Exception("Name cannot contain whitespaces")
        if cfg_type != "cmsRun" and cfg_type != "cmsDriver": raise Exception("Type should be cmsRun or cmsDriver (is %s)" % cfg_type)
       
        # check commands in case of cmsDriver: is first step a GEN step ?
        if cfg_type == "cmsDriver":
        
            cfg_cmsdriver_commands = fin.cfg_cmsdriver_commands
            cfg_cmsdriver_command_names = fin.cfg_cmsdriver_command_names
            
            for cfg_command_name in cfg_cmsdriver_command_names: 
                if ' ' in cfg_command_name: raise Exception("Command name cannot contain whitespaces")
            if len(cfg_cmsdriver_command_names) != len(cfg_cmsdriver_commands): raise Exception("Command names and command should have identical size")
        
            if not (opts.status or opts.resubmit): print(" > cmsDriver type detected")
            
            # check if commands contain cmsDriver.py (and remove)
            for i,cmd in enumerate(cfg_cmsdriver_commands): cfg_cmsdriver_commands[i] = cfg_cmsdriver_commands[i].replace("cmsDriver.py", "")

            # determine if the first step contains GEN
            cmdSplit = shlex.split(cfg_cmsdriver_commands[0]) # split cmsDriver arguments
            if "-s" in cmdSplit: idx = cmdSplit.index("-s")
            elif "--step" in cmdSplit: idx = cmdSplit.index("-step")
            else: raise Exception("No step (-s or --step) found in command %s" % cfg_cmsdriver_command_names[i])
            cfg_isGEN = "GEN" in cmdSplit[idx+1]
            
            if cfg_isGEN: # if GEN step: number of jobs and events must be given
            
                cfg_nevents = fin.cfg_nevents
                cfg_njobs = fin.cfg_njobs
            
                if not (opts.status or opts.resubmit): print(" > GEN step detected in first command")
                if not isinstance(cfg_nevents, int) or cfg_nevents <= 0: raise Exception("Provide valid number of events when using GEN step")
                if not isinstance(cfg_njobs, int) or cfg_njobs <= 0: raise Exception("Provide valid number of jobs")
                if cfg_nevents < cfg_njobs: raise Exception("Number of jobs should be smaller than number of events")
                if opts.dryrun: print(" > will perform dryrun with 10 events")
                elif not (opts.status or opts.resubmit): print(" > will run %d events over %s jobs" % (cfg_nevents, cfg_njobs))
            
            else: # if not GEN step: fetch number of jobs from input
            
                cfg_input_dataset_file = fin.cfg_input_dataset_file
                cfg_input_dataset_name = fin.cfg_input_dataset_name
            
                if not (opts.status or opts.resubmit): print(" > No GEN step detected, use input tag to run the jobs")
                if not os.path.isfile(cfg_input_dataset_file): raise Exception('Input tag file %s does not exist' % cfg_input_dataset_file)
                
                # load config file for input tag
                fin = __import__(os.path.basename(cfg_input_dataset_file).split(".")[0])

                # overwrite settings
                cfg_input_dataset_run_dir = fin.cfg_run_dir
                cfg_nevents = fin.cfg_nevents
                cfg_njobs = fin.cfg_njobs
                cfg_input_dataset_storage_dir = fin.cfg_storage_dir
                
                
                
                # look for dryrun input file
                if opts.dryrun:
                
                    # check if dryrun dir exists
                    if not os.path.isdir("%s/dryrun" % cfg_input_dataset_run_dir): raise Exception('Dryrun directory for input tag %s not found, please run it' % cfg_input_dataset_file)
                    
                    # check if dryrun input file exists
                    cfg_dryrun_input_file = "%s/dryrun/%s.root" % (cfg_input_dataset_run_dir, cfg_input_dataset_name)
                    if not os.path.isfile(cfg_dryrun_input_file): raise Exception('Cannot find dryrun input file %s' % cfg_dryrun_input_file)
                    
                # collect ROOT input files... do check
                if opts.submit:
                
                    if not os.path.isdir(cfg_input_dataset_storage_dir): raise Exception('Associated input directory %s does not exist' % cfg_input_dataset_storage_dir)
                
                    for i in range(0, cfg_njobs):
                    
                        root_file = "%s/%04d_%s.root" % (cfg_input_dataset_storage_dir, i, cfg_input_dataset_name)
                        if not os.path.isfile(root_file): raise Exception(' > ERROR: ROOT file %s not found' % root_file)

        if cfg_type == "cmsRun":
        
            cfg_output_name = fin.cfg_output_name
            cfg_input_file = fin.cfg_input_file
            if not os.path.isfile(cfg_input_file): raise Exception('Input file %s does not exist' % cfg_input_file)
        
            cfg_input_dataset_file = fin.cfg_input_dataset_file
            cfg_input_dataset_name = fin.cfg_input_dataset_name  
            if not os.path.isfile(cfg_input_dataset_file): raise Exception('Input dataset file %s does not exist' % cfg_input_dataset_file)
            
            # load config file for input tag
            fin = __import__(os.path.basename(cfg_input_dataset_file).split(".")[0])

            # overwrite settings
            cfg_input_dataset_run_dir = fin.cfg_run_dir
            cfg_nevents = fin.cfg_nevents
            cfg_njobs = fin.cfg_njobs
            cfg_input_dataset_storage_dir = fin.cfg_storage_dir
            
        

    except Exception, e: 
        print(e)
        sys.exit()
        
    cfg_dryrun_dir = "%s/dryrun/" % cfg_run_dir
    cfg_submission_dir = "%s/submission/" % cfg_run_dir
        
    try:
    
        if opts.dryrun: dryrun()
        if opts.submit: submit()
        if opts.resubmit: resubmit()
        if opts.status: status()

        
    except Exception, e: 
        print(e)
        sys.exit()
    

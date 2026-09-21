#!/usr/bin/env python

# Import Packages

import os
import sys
import os.path as path
import json


# Read the Input JSON File

# Input file paths for testing and experimentation.
# Uncomment and edit these to run the script outside the batch system.

#json_file_simulate = '/p/lustre2/jha3/Wildfire/Wildfire_LDRD_SI/InputJson/Simulate/json_simulate_000.json'


# Input file paths taken from the command line.
# This is how the batch scripts invoke this file, and the normal path.

json_file_simulate = sys.argv[1]

# Load the JSON file for simulation

print('Loading the JSON file for simulation: \n {}'.format(json_file_simulate))


with open(json_file_simulate) as json_file_handle:
    json_content_simulate = json.load(json_file_handle)


# Action To Be Taken

action = json_content_simulate['action']


# Execution Options

execution_options = json_content_simulate['execution_options']
print_interactive_command = execution_options['print_interactive_command']
print_sbatch_command = execution_options['print_sbatch_command']
run_interactively = execution_options['run_interactively']
submit_job    = execution_options['submit_job']


exempt_flag = json_content_simulate['exempt_flag'] #'--qos=exempt'


# Simulation Directory

sim_dir = json_content_simulate['paths']['sim_dir']


# `sbatch` Scripts

sbatch_scripts = json_content_simulate['paths']['sbatch_scripts']


sbatch_script_extract = os.path.join(sbatch_scripts['base'], sbatch_scripts['extract'])
sbatch_script_prep = os.path.join(sbatch_scripts['base'], sbatch_scripts['prep'])
sbatch_script_train = os.path.join(sbatch_scripts['base'], sbatch_scripts['train'])


# `python` Scripts

python_scripts = json_content_simulate['paths']['python_scripts']


python_script_extract = os.path.join(python_scripts['base'], python_scripts['extract'])
python_script_prep = os.path.join(python_scripts['base'], python_scripts['prep'])
python_script_train = os.path.join(python_scripts['base'], python_scripts['train'])


# `json` Input Files

json_base = json_content_simulate['paths']['json_base']


json_extract_base = os.path.join(sim_dir, json_base['extract'])
json_prep_base = os.path.join(sim_dir, json_base['prep'])
json_train_base = os.path.join(sim_dir, json_base['train'])


# `json` Collections

collection_options = json_content_simulate['collection_options']
json_extract_counts = collection_options['json_extract_counts']
json_prep_counts = collection_options['json_prep_counts']
json_train_counts = collection_options['json_train_counts']


json_extract_counts, json_prep_counts, json_train_counts


# Generate and Execute `command`

def get_commands (exempt_flag, sbatch_script, base_command):
    run_command = 'python {}'.format(base_command)
    sbatch_submit_command = 'sbatch {} {} {}'.format(                                exempt_flag, sbatch_script, base_command)
    
    return run_command, sbatch_submit_command
    

def print_and_execute (print_interactive_command, print_sbatch_command,                        run_interactively, submit_job,                        run_command, sbatch_submit_command):
    if (print_interactive_command):
        print('\n', run_command)
    if (print_sbatch_command):
        print('\n', sbatch_submit_command)
    if (run_interactively):
        os.system (run_command)
    if (submit_job):
        os.system (sbatch_submit_command)


for data_count in json_extract_counts:
    json_extract = '%s_%03d.json'%(json_extract_base, data_count)
    #print(json_extract)
    if (action == 'Extract'):
        base_command = '{} {}'.format(python_script_extract,
                                      json_extract)
        run_command, sbatch_submit_command = get_commands (                                    exempt_flag, sbatch_script_extract, base_command)
        print_and_execute (print_interactive_command, print_sbatch_command,                            run_interactively, submit_job,                            run_command, sbatch_submit_command)
        continue
        
    for label_count in json_prep_counts:
        json_prep    = '%s_%03d.json'%(json_prep_base, label_count)
        #print(json_prep)
        if (action == "Prep"):
            base_command = '{} {} {}'.format(python_script_prep,
                                             json_extract,
                                             json_prep)
            run_command, sbatch_submit_command = get_commands (                                        exempt_flag, sbatch_script_prep, base_command)
            print_and_execute (print_interactive_command, print_sbatch_command,                                run_interactively, submit_job,                                run_command, sbatch_submit_command)
            continue
            
        for train_count in json_train_counts:
            json_train   = '%s_%03d.json'%(json_train_base, train_count)
            #print(json_train)
            if (action == "Train"):
                base_command = '{} {} {} {}'.format(python_script_train,
                                                    json_extract,
                                                    json_prep,
                                                    json_train)
                run_command, sbatch_submit_command = get_commands (                                        exempt_flag, sbatch_script_train, base_command)
                print_and_execute (print_interactive_command, print_sbatch_command,                                    run_interactively, submit_job,                                    run_command, sbatch_submit_command)
                continue

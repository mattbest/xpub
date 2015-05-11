#!/usr/bin/env python 
#            / 
#  )( /) (/ () 
#    /       
"""
A CLI for `xromm.uchicago.edu` data portal.

Prompts the user for metadata when transferring a file.  Also permits 
users to create a new study or trial on the portal.

See `xpub.py --help` for usage.

Examples:

    xpub.py --study     (create a new study)
    xpub.py --trial     (create a new trial)
    xpub.py FILE        (transfer a file)

"""
import os
import json
import argparse
from datetime import datetime
from prompter import Prompt, Prompter
from mediatype import get_mediatype
from action import prompt_for_action

# set config dir based on $XROMM_CONFIG env variable if present
# otherwise look for a `config` dir in current working dir
cwd_config = os.path.join(os.getcwd(), 'config')
CONFIG_DIR = os.environ.get('XROMM_CONFIG', cwd_config)

# setup the argument parser
parser = argparse.ArgumentParser(version="0.1", description=__doc__)
parser.add_argument('--required', 
                    action="store_true", 
                    help="Only prompt for required input")
parser.add_argument('--verbose', 
                    action="store_true", 
                    help="Provide additional info when prompting")

group = parser.add_mutually_exclusive_group()
group.add_argument('--study', 
                   action="store_true", 
                   help="Create a new study")
group.add_argument('--trial', 
                    action="store_true",
                    help="Create a new trial")
group.add_argument('file', nargs='?', help="Transfer a file")

args = parser.parse_args()

if args.study:
    resource = 'study.json'
elif args.trial:
    resource = 'trial.json'
elif args.file:
    resource = 'file.json'
else:
    parser.print_help()
    raise SystemExit

config_path = os.path.join(CONFIG_DIR, resource)        # resource config
cache_path  = os.path.join(CONFIG_DIR, 'cache.json')    # cached info
    
config = json.load(open(config_path))   # load resource config file
cache = json.load(open(cache_path))     # load cached study/trial options


# supplement config with cached info if out of date
if config['updated_at'] < cache['updated_at']:

    # if creating a trial, add cached study names
    if config['key'] == 'trial':
        # first prompt should be for name of study
        config['prompts'][0]['options'] = cache['studies'].keys()

    # if transferring a file, add cached study/trial names 
    elif config['key'] == 'file':
        # first prompt should be for name of study/trial
        options = []
        for study in cache['studies'].keys():
            options.append(study)
            for trial in cache['studies'][study]:
                options.append('{}/{}'.format(study, trial))
        config['prompts'][0]['options'] = options


prompt = Prompter(config, verbose=args.verbose,
                          required=args.required)   # initialize a prompter
prompt()                                            # prompt for input


# save/update a json config file (at `path`) with config `data`
def save_json(data, path):
    data['updated_at'] = datetime.now().isoformat() + 'Z'
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

# ok . . . with input collected, what should be done with it?
prompt_for_action(prompt.results)               # view/save/send/discard results?

if prompt.config_revisions:                     # if new input was seen ...
    save_json(prompt.config, config_path)       # update config

# cache new study/trial names
if args.study:                                  # if study was created ...
    name = prompt.results['data']['name']       # name entered when prompted
    if not name in cache['studies']:
        cache['studies'][name] = []
        save_json(cache, cache_path)            # update cache

elif args.trial:                                # if trial was created ...
    study = prompt.results['data']['study']     # study name entered
    trial = prompt.results['data']['name']      # trial name entered
    if not study in cache['studies']:
        cache['studies'][study] = []
    if not trial in cache['studies'][study]:
        cache['studies'][study].append(trial)
        save_json(cache, cache_path)            # update cache

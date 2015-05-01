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
from prompter import Prompter

# set config dir based on $XROMM_CONFIG env variable if present
# otherwise look for a `config` dir in current working dir
cwd_config = os.path.join(os.getcwd(), 'config')
CONFIG_DIR = os.environ.get('XROMM_CONFIG', cwd_config)

# setup the argument parser
parser = argparse.ArgumentParser(version="0.1", description=__doc__)
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
    # add cached study names if creating a trial
    if config['key'] == 'trial':
        # first prompt should be for name of study
        config['prompts'][0]['options'] = cache['studies'].keys()

prompt = Prompter(config, verbose=args.verbose) # initialize a prompter

prompt()        # prompt for input

# if new input was seen, we'll add it to the config file ...
if prompt.config_revisions:
    now = datetime.now().isoformat() + 'Z'
    prompt.config['updated_at'] = now
    # revised_config = json.dumps(prompt.config, indent=4)
    # save changes
    with open(config_path, 'w') as f:
            json.dump(prompt.config, f, indent=4)

print prompt    # print collected input

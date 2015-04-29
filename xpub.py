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
import argparse
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
    res = 'study.json'
elif args.trial:
    res = 'trial.json'
elif args.file:
    res = 'file.json'
else:
    parser.print_help()
    raise SystemExit

config = os.path.join(CONFIG_DIR, res)
    
# initialize a prompter with appropriate resource config file
prompt = Prompter(config, verbose=args.verbose)

prompt()        # prompt for input

print prompt    # print collected input

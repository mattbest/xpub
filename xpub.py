#!/usr/bin/env python 
#            / 
#  )( /) (/ () 
#    /       
"""
A CLI for `xromm.uchicago.edu`.

Prompts the user for metadata when creating a study or trial or 
transferring a file.

"""
import argparse
from prompter import Prompter

parser = argparse.ArgumentParser(version="0.1", description=__doc__)
parser.add_argument('--study', 
                    action="store_true", 
                    help="Create a new study")
parser.add_argument('--trial', 
                    action="store_true",
                    help="Create a new trial")
parser.add_argument('--file', 
                    action="store",
                    help="Transfer a file")
parser.add_argument('--verbose', 
                    action="store_true", 
                    help="Provide additional info when prompting")

args = parser.parse_args()

if args.study:
    config = 'config/study.json'
elif args.trial:
    config = 'config/trial.json'
elif args.file:
    config = 'config/file.json'
else:
    parser.print_help()
    raise SystemExit
    

prompt = Prompter(config, verbose=args.verbose)
prompt()

print prompt

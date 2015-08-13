#!/usr/bin/env python 
#            / 
#  )( /) (/ () 
#    /       
"""
A CLI for `xromm.uchicago.edu` data portal.

Prompts the user for metadata when transferring a file.  Also permits 
users to create a new study or trial on the portal.

See `xpub --help` for usage.

Examples:

    xpub --study     (create a new study)
    xpub --trial     (create a new trial)
    xpub FILE        (transfer a file)

"""
import os
import json
import argparse
from datetime import datetime
from mediatype import get_mediatype
from action import prompt_for_action, save_json
from prompter import Prompt, Prompter


def run():
    
    # set config dir based on $XROMM_CONFIG env variable if present
    # otherwise look for a `config` dir in current working dir
    cwd_config = os.path.join(os.getcwd(), 'config')
    if not os.path.isfile(cwd_config):
        pkg_dir = os.path.dirname(os.path.abspath(__file__))
        cwd_config = os.path.join(pkg_dir, 'config')
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
    group.add_argument('--healthrecord', 
                       action="store_true", 
                       help="Create a heatlh report in the Hatabase")
    
    args = parser.parse_args()

    if args.study:
        resource = 'study.json'
    elif args.trial:
        resource = 'trial.json'
    elif args.file:
        resource = 'file.json'
        mt = get_mediatype()    # get config for specific mediatype
        try:                    # set config for selected mediatype
            mt_config_path = os.path.join(CONFIG_DIR, 'mediatypes', mt + '.json')
            if os.path.isfile(mt_config_path):
                resource = os.path.join('mediatypes', mt + '.json')
        except NameError:
            pass                # if not found, use default file prompting
    elif args.healthrecord:
        resource = 'macaque_health_record.json'
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
        if args.trial:
            # first prompt should be for name of study
            config['prompts'][0]['options'] = cache['studies'].keys()
    
        # if transferring a file, add cached study/trial names 
        elif args.file:
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
    
    # ok . . . with input collected, what should be done with it?
    prompt_for_action(prompt.results, args.file)    # view/save/send/discard
    
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

# END run()


if __name__ == '__main__':

    run()
